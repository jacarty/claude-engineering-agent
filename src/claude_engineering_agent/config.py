"""
Configuration and Anthropic client factory.

Loads settings from .env and provides a get_client() function that returns
the Anthropic client, MCP servers and tools.
"""

import os
from dataclasses import dataclass, field

import anthropic
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """All settings loaded from environment variables with sensible defaults."""

    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    linear_mcp_token: str = os.getenv("LINEAR_MCP_TOKEN", "")
    github_mcp_pat: str = os.getenv("GITHUB_MCP_PAT", "")

    # Model and output settings
    model: str = os.getenv("MODEL", "claude-sonnet-4-6")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))
    betas: list[str] = field(default_factory=lambda: ["mcp-client-2025-11-20"])

    def __post_init__(self):
        if not self.model:
            raise ValueError("Model must be defined. Update with a valid API model.")
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY cannot be empty. Update .env")
        if not self.linear_mcp_token:
            raise ValueError("LINEAR_MCP_TOKEN cannot be empty. Update .env")
        if not self.github_mcp_pat:
            raise ValueError("GITHUB_MCP_PAT cannot be empty. Update .env")

    def get_client(self) -> anthropic.Anthropic:
        """Create the Anthropic client with retry configuration."""
        return anthropic.Anthropic(api_key=self.anthropic_api_key, max_retries=4)

    def get_mcp_servers(self) -> list[dict]:
        """Return the list of MCP servers"""
        mcp_servers = [
            {
                "type": "url",
                "url": "https://mcp.linear.app/mcp",
                "name": "linear",
                "authorization_token": self.linear_mcp_token,
            },
            {
                "type": "url",
                "url": "https://api.githubcopilot.com/mcp",
                "name": "github",
                "authorization_token": self.github_mcp_pat,
            },
        ]

        return mcp_servers

    def get_tools(self) -> list[dict]:
        """Return the list of tools available"""

        tools = [
            {
                "type": "mcp_toolset",
                "mcp_server_name": "linear",
                "default_config": {"defer_loading": True},
                "configs": {
                    "get_issue": {"defer_loading": False},
                    "list_comments": {"defer_loading": False},
                    "save_comment": {"defer_loading": False},
                    "save_issue": {"defer_loading": False},
                    "list_issue_labels": {"defer_loading": False},
                },
            },
            {
                "type": "mcp_toolset",
                "mcp_server_name": "github",
                "default_config": {"defer_loading": True},
                "configs": {
                    "get_file_contents": {"defer_loading": False},
                    "search_code": {"defer_loading": False},
                    "search_repositories": {"defer_loading": False},
                    "pull_request_read": {"defer_loading": False},
                },
            },
            {"type": "web_search_20250305", "name": "web_search"},
        ]

        return tools
