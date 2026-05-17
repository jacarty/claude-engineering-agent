"""Run the research agent loop with streaming output and execution traces."""

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import anthropic

from claude_engineering_agent.config import Config
from claude_engineering_agent.prompts import SYSTEM_PROMPT


def run_agent(config: Config, issue_id: str) -> str:
    """Research a Linear issue and return a structured brief.

    Streams output to the terminal in real time so the user always
    knows what the agent is doing. Saves a structured execution
    trace to docs/traces/.
    """
    client = config.get_client()
    messages = [{"role": "user", "content": f"Research the Linear issue {issue_id}"}]
    max_iterations = 5
    system = SYSTEM_PROMPT

    # Accumulate trace and token totals across iterations
    trace = []
    total_input_tokens = 0
    total_output_tokens = 0

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
                system=system,
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
                                # Some events use "text" directly
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
            break
        elif response.stop_reason == "pause_turn":
            print("pause_turn — MCP Connector hit server-side limit, continuing...")

        # Otherwise, append the assistant response and continue
        messages.append({"role": "assistant", "content": response.content})

    else:
        print(f"\n⚠️  Max iterations ({max_iterations}) reached — agent may not have finished")

    # Final summary
    print(f"\n{'=' * 60}")
    print("  Research complete")
    print(f"  Total tokens: {total_input_tokens:,} in / {total_output_tokens:,} out")
    print(f"  Iterations: {len(trace)}")
    print(f"{'=' * 60}\n")

    # Save trace
    _save_trace(issue_id, trace, total_input_tokens, total_output_tokens)

    # Extract final text
    return "\n".join(block.text for block in response.content if block.type == "text")


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
