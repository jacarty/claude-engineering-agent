import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

token = os.environ["GITHUB_MCP_PAT"]
print(f"Token starts with: {token[:10]}...")

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What tools do you have available?"}],
    mcp_servers=[
        {
            "type": "url",
            "url": "https://api.githubcopilot.com/mcp",
            "name": "github",
            "authorization_token": os.environ["GITHUB_MCP_PAT"],
        }
    ],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "github"}],
    betas=["mcp-client-2025-11-20"],
)

for block in response.content:
    print(block.type, ":", getattr(block, "text", getattr(block, "name", "")))
