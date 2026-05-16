"""Run the research agent loop."""

from claude_engineering_agent.config import Config
from claude_engineering_agent.prompts import SYSTEM_PROMPT


def run_agent(config: Config, issue_id: str) -> str:
    """Research a Linear issue and return a structured brief."""

    client = config.get_client()
    messages = [{"role": "user", "content": f"Research the Linear issue {issue_id}"}]
    max_iterations = 5
    system = SYSTEM_PROMPT

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")
        print("Calling Claude API...")

        response = client.beta.messages.create(
            model=config.model,
            max_tokens=config.max_tokens,
            messages=messages,
            mcp_servers=config.get_mcp_servers(),
            tools=config.get_tools(),
            betas=config.betas,
            system=system,
            timeout=300.0,
        )

        print(f"Stop reason: {response.stop_reason}")
        print(f"Content blocks: {len(response.content)}")

        # Log tool calls
        tool_calls = [block for block in response.content if block.type == "mcp_tool_use"]
        if tool_calls:
            for tc in tool_calls:
                print(f"  Tool: {tc.server_name}/{tc.name}")

        # Log text block previews
        text_blocks = [block for block in response.content if block.type == "text"]
        for tb in text_blocks:
            print(f"  Text: {tb.text[:100]}...")

        # If Claude is done, break
        if response.stop_reason == "end_turn":
            break

        # Otherwise, append the assistant response and continue
        messages.append({"role": "assistant", "content": response.content})

    else:
        print(f"\n⚠️  Max iterations ({max_iterations}) reached — agent may not have finished")

    return "\n".join(block.text for block in response.content if block.type == "text")
