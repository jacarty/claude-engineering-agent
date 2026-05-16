"""Run"""

from claude_engineering_agent.config import Config


def run_agent(config: Config, issue_id: str) -> str:

    client = config.get_client()
    messages = [{"role": "user", "content": f"Research the Linear issue {issue_id}"}]
    max_iterations = 5
    system = """You are a research agent. Given a Linear issue ID, read the issue using the Linear
        MCP tools, then provide a detailed summary of what the issue is about, its current status,
        and any relevant context."""

    for iteration in range(max_iterations):
        response = client.beta.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            messages=messages,
            mcp_servers=config.get_mcp_servers(),
            tools=config.get_tools(),
            betas=config.betas,
            system=system,
        )

        print(f"\n--- Iteration {iteration + 1} ---")
        print(f"Stop reason: {response.stop_reason}")
        print(f"Content blocks: {len(response.content)}")

        # If Claude is done, break
        if response.stop_reason == "end_turn":
            break

        # Otherwise, append the assistant response and continue
        # Claude needs to see its own previous output to keep going
        messages.append({"role": "assistant", "content": response.content})

    else:
        # This block runs if the loop completed WITHOUT breaking
        print(f"\n⚠️  Max iterations ({max_iterations}) reached — agent may not have finished")

    return "\n".join(block.text for block in response.content if block.type == "text")
