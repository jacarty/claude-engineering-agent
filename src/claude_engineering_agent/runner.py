"""Run the research agent loop with streaming output and execution traces."""

import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import anthropic

from claude_engineering_agent.config import Config
from claude_engineering_agent.prompts import build_research_prompt, build_spec_prompt
from claude_engineering_agent.repo import discover_repo


def _build_skills_inventory() -> str:
    """Read local .claude/skills/ and .claude/agents/ and build a summary."""
    sections = []

    skills_dir = Path(".claude/skills")
    if skills_dir.exists():
        skills = []
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    desc = _extract_frontmatter_description(skill_md)
                    if desc:
                        skills.append(f"- {skill_dir.name} — {desc}")
        if skills:
            sections.append("### Skills (.claude/skills/)\n" + "\n".join(skills))

    agents_dir = Path(".claude/agents")
    if agents_dir.exists():
        agents = []
        for agent_file in sorted(agents_dir.glob("*.md")):
            desc = _extract_frontmatter_description(agent_file)
            if desc:
                agents.append(f"- {agent_file.stem} — {desc}")
        if agents:
            sections.append("### Agents (.claude/agents/)\n" + "\n".join(agents))

    if not sections:
        return ""

    return (
        "## Available skills and agents\n\n"
        "These are already in the repository and listed below. Do not use GitHub MCP "
        "to list or read these directories — the inventory is here. You can still use "
        "GitHub MCP to read a specific skill's full SKILL.md if you need the detailed "
        "instructions for your recommendation.\n\n" + "\n\n".join(sections)
    )


def _extract_frontmatter_description(filepath: Path) -> str:
    """Extract the description field from YAML frontmatter."""
    text = filepath.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return ""
    frontmatter = match.group(1)
    desc_match = re.search(r"^description:\s*>?\s*\n((?:\s+.*\n)*)", frontmatter, re.MULTILINE)
    if desc_match:
        # Multi-line YAML description — join and clean
        lines = desc_match.group(1).strip().splitlines()
        return " ".join(line.strip() for line in lines)
    # Single-line description
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        return desc_match.group(1).strip()
    return ""


def _run_agent_loop(client, config, system_prompt, user_message, issue_id) -> tuple:

    # Accumulate trace and token totals across iterations
    trace = []
    total_input_tokens = 0
    total_output_tokens = 0
    max_iterations = 3
    success = False
    messages = [{"role": "user", "content": user_message}]

    for iteration in range(max_iterations):
        iter_start = time.time()
        print(f"\n{'=' * 60}")
        print(f"  Iteration {iteration + 1}/{max_iterations}")
        print(f"{'=' * 60}\n")

        # Track tool calls and text for this iteration
        iter_tools = []
        iter_text_chunks = []
        current_tool_name = None
        current_tool_server = None

        try:
            with client.beta.messages.stream(
                model=config.model,
                max_tokens=config.max_tokens,
                messages=messages,
                mcp_servers=config.get_mcp_servers(),
                tools=config.get_tools(),
                betas=config.betas,
                system=system_prompt,
            ) as stream:
                for event in stream:
                    if event.type == "content_block_start":
                        block = event.content_block
                        if hasattr(block, "type") and block.type == "mcp_tool_use":
                            current_tool_name = block.name
                            current_tool_server = getattr(block, "server_name", "unknown")
                            print(f"  🔧 Tool: {current_tool_server}/{current_tool_name}")
                            iter_tools.append(f"{current_tool_server}/{current_tool_name}")

                    elif event.type == "content_block_delta":
                        delta = event.delta
                        if hasattr(delta, "type"):
                            if delta.type == "text_delta":
                                text = delta.text
                                print(text, end="", flush=True)
                                iter_text_chunks.append(text)
                            elif delta.type == "text":
                                text = getattr(delta, "text", "")
                                if text:
                                    print(text, end="", flush=True)
                                    iter_text_chunks.append(text)

                    elif event.type == "content_block_stop":
                        current_tool_name = None
                        current_tool_server = None

                response = stream.get_final_message()

        except anthropic.AuthenticationError as e:
            print(f"\n❌ Authentication failed: {e}")
            print("   Check your ANTHROPIC_API_KEY, LINEAR_MCP_TOKEN, and GITHUB_MCP_TOKEN in .env")
            sys.exit(1)

        except anthropic.RateLimitError as e:
            print(f"\n⚠️  Rate limited after retries: {e}")
            print(
                "   The SDK retried automatically but limits are still exceeded."
                " Wait and try again."
            )
            sys.exit(1)

        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                print(f"\n❌ API server error ({e.status_code}): {e}")
                print("   Anthropic API is having issues. Try again later.")
            else:
                print(f"\n❌ API error ({e.status_code}): {e}")
            sys.exit(1)

        except anthropic.APIConnectionError as e:
            print(f"\n❌ Connection error: {e}")
            print("   Check your network connection.")
            sys.exit(1)

        # Iteration summary
        iter_duration = round(time.time() - iter_start, 2)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        print(f"\n\n{'─' * 40}")
        print(f"  Stop reason: {response.stop_reason}")
        print(f"  Tools called: {len(iter_tools)}")
        print(f"  Tokens: {input_tokens:,} in / {output_tokens:,} out")
        print(f"  Duration: {iter_duration}s")
        print(f"{'─' * 40}")

        # Append to trace
        trace.append(
            {
                "iteration": iteration + 1,
                "stop_reason": response.stop_reason,
                "tools_called": iter_tools,
                "token_usage": {"input": input_tokens, "output": output_tokens},
                "duration_seconds": iter_duration,
            }
        )

        # If Claude is done, break
        if response.stop_reason == "end_turn":
            success = True
            break
        elif response.stop_reason == "pause_turn":
            print("pause_turn — MCP Connector hit server-side limit, continuing...")

        # Otherwise, append the assistant response and continue
        messages.append({"role": "assistant", "content": response.content})

    if not success:
        print(f"\n⚠️  Max iterations ({max_iterations}) reached — agent may not have finished")

    # Final summary
    print(f"\n{'=' * 60}")
    print("  Agent complete")
    print(f"  Total tokens: {total_input_tokens:,} in / {total_output_tokens:,} out")
    print(f"  Iterations: {len(trace)}")
    print(f"{'=' * 60}\n")

    # Save trace
    _save_trace(issue_id, trace, total_input_tokens, total_output_tokens)

    # Extract final text
    output = "\n".join(block.text for block in response.content if block.type == "text")

    return output, success


def run_agent(config: Config, issue_id: str, mode: str) -> str:
    """Takes input from CLI to return the corresponding information. Options:

    - Research on a Linear issue
    - Reseach + Spec for a Linear issue
    - Only Spec for a Linear issue

    Streams output to the terminal in real time so the user always
    knows what the agent is doing. Saves a structured execution
    trace to docs/traces/.
    """
    client = config.get_client()

    repo = discover_repo()
    skills_inventory = _build_skills_inventory()

    research_prompt = build_research_prompt(repo.owner, repo.name, skills_inventory)
    spec_prompt = build_spec_prompt(repo.owner, repo.name, skills_inventory)

    if mode == "research":
        research_text, _ = _run_agent_loop(  # _ to represent unused status in tuple
            client,
            config,
            research_prompt,
            f"Research the Linear issue {issue_id}",
            issue_id,
        )
        return research_text

    elif mode == "spec":
        # First: research
        research_text, research_ok = _run_agent_loop(
            client,
            config,
            research_prompt,
            f"Research the Linear issue {issue_id}",
            issue_id,
        )
        if not research_ok:
            return research_text

        # Second: spec (reads the posted research brief from Linear)
        spec_text, spec_ok = _run_agent_loop(
            client,
            config,
            spec_prompt,
            f"Generate an implementation spec for Linear issue {issue_id}",
            issue_id,
        )
        return spec_text

    elif mode == "spec_only":
        spec_text, _ = _run_agent_loop(  # _ to represent unused status in tuple
            client,
            config,
            spec_prompt,
            f"Generate an implementation spec for Linear issue {issue_id}",
            issue_id,
        )
        return spec_text


def _save_trace(
    issue_id: str,
    trace: list[dict],
    total_input: int,
    total_output: int,
) -> None:
    """Save the execution trace as JSON to docs/traces/."""
    traces_dir = Path("docs/traces")
    traces_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{issue_id}_{timestamp}.json"
    filepath = traces_dir / filename

    trace_data = {
        "issue_id": issue_id,
        "timestamp": timestamp,
        "total_tokens": {"input": total_input, "output": total_output},
        "iterations": trace,
    }

    filepath.write_text(json.dumps(trace_data, indent=2))
    print(f"Trace saved to {filepath}")
