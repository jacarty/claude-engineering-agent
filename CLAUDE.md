# Claude Engineering Agent — Claude Code Context

## Project Overview

An adaptive research agent that reads Linear issues and produces contextualised technical briefs using Claude's MCP Connector, web search, and the repo's own skills/templates. Built as a Python CLI.

**PRD:** `docs/prd/v1.0-prd.md` (not yet created)
**Build Guide:** `docs/build-guides/v1.0-build-guide.md` (not yet created)
**Process:** `docs/process.md` — branch/PR cadence, pre-commit + pre-PR agent gates, trivial-change fast path, phase-boundary rituals. Read this before any feature work.

**Issue Tracking:** Linear — project "AI and Machine Learning", team "James", key `JAM`. Parent issue: JAM-244.

---

## Rules

These are non-negotiable. They apply to every session regardless of scope.

- **Never commit directly to main.** Always create a feature or fix branch and open a PR. No exceptions.
- **Before pushing, verify only intended files are staged.** Run `git status` and `git diff --cached --name-only` before every commit. Do not include unrelated config files, lockfile churn, or editor artefacts.
- **Run lint + tests + build locally before opening a PR.** Do not rely on CI to catch issues. The pre-PR gates in `docs/process.md` exist to shift catches earlier, not replace local validation.
- **Read `docs/process.md` before any feature work.** It defines the agent cadence, trivial-change fast path, and fold timing. Follow it.
- **Never commit `.env` or any file containing API keys/tokens.** The `.gitignore` and `.claudeignore` are configured to prevent this, but check anyway.
- **Use `uv` for all package management.** No pip, no poetry. `uv sync` to install, `uv add` to add dependencies, `uv run` to execute.

---

## Architecture

```
Python CLI (src/claude_engineering_agent/)
  → Claude API (direct, beta mcp-client-2025-11-20)
  → MCP Connector (server-side):
      - Linear MCP (mcp.linear.app/mcp) — read issues, post comments, update status
      - GitHub MCP (api.githubcopilot.com/mcp) — search code, read files, create branches
  → Claude server tool:
      - Web search (web_search_20250305)
  → Agentic loop (call until stop_reason is end_turn)
  → Structured research brief posted to Linear
```

### Key architecture decision

Uses the **MCP Connector** (server-side) rather than client-side MCP. The `mcp_servers` parameter in `messages.create()` lets Anthropic's infrastructure handle connection, tool discovery, and execution. No MCP Python SDK, no session management, no tool wrappers needed.

The repo's own skills (`.claude/skills/`) and agents (`.claude/agents/`) are read via the GitHub MCP server — no local filesystem tool required.

### Key technology choices

- **Language:** Python 3.12+
- **Package manager:** uv
- **API client:** anthropic (Python SDK)
- **MCP integration:** MCP Connector (server-side via `mcp_servers` parameter)
- **CLI:** `python -m claude_engineering_agent` with argparse
- **Config:** python-dotenv for environment variables
- **Testing:** pytest
- **Linting:** ruff

### Environment

- **GitHub Repo:** jacarty/claude-engineering-agent
- **Linear Project:** AI and Machine Learning, team James
- **Parent Issue:** JAM-244

---

## Repository Structure

```
claude-engineering-agent/
├── CLAUDE.md                        # This file
├── README.md                        # Public-facing project documentation
├── pyproject.toml                   # Python project configuration (uv)
├── .env.example                     # Required environment variables template
├── .claude/
│   ├── agents/                      # Claude Code subagents (9 agents)
│   ├── commands/                    # Claude Code custom commands
│   ├── skills/                      # Thinking/writing frameworks (11 skills)
│   └── settings.json                # Claude Code tool permissions
├── .githooks/                       # Local git hooks (secret scanning, conventional commits)
├── .github/                         # GitHub templates (PR, issues, CODEOWNERS)
├── docs/
│   ├── decisions/                   # Architecture Decision Records
│   └── process.md                   # Development process and agent cadence
├── src/
│   └── claude_engineering_agent/
│       ├── __init__.py
│       ├── __main__.py              # CLI entry point
│       ├── config.py                # MCP server + tool configuration
│       ├── runner.py                # Agentic loop (call API until done)
│       └── parsing.py               # Response block extraction
└── tests/
```

---

## Key Patterns

### MCP Connector configuration

MCP servers and tools are configured as data structures passed to `client.beta.messages.create()`:

```python
mcp_servers = [
    {"type": "url", "url": "https://mcp.linear.app/mcp", "name": "linear", "authorization_token": "..."},
    {"type": "url", "url": "https://api.githubcopilot.com/mcp", "name": "github", "authorization_token": "..."},
]

tools = [
    {"type": "mcp_toolset", "mcp_server_name": "linear"},
    {"type": "mcp_toolset", "mcp_server_name": "github"},
    {"type": "web_search_20250305", "name": "web_search"},
]
```

### Agentic loop

The runner calls `messages.create()` in a loop. Each response may contain `mcp_tool_use` and `mcp_tool_result` blocks (handled server-side by the MCP Connector) alongside `text` blocks. The loop continues until `stop_reason` is `end_turn`. A max-iteration guard prevents runaway loops.

### Response content block types

- `text` — Claude's reasoning and output
- `mcp_tool_use` — tool invocation (name, server, input params)
- `mcp_tool_result` — tool result (content, is_error flag)

### Environment variables

All secrets via `.env` (never committed):

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Claude API access |
| `LINEAR_MCP_TOKEN` | Linear MCP server OAuth token |
| `GITHUB_MCP_TOKEN` | GitHub MCP server OAuth token |

---

## Testing

| Level | Tool | Scope |
|-------|------|-------|
| Unit | pytest | Config loading, response parsing, error handling |
| Integration | pytest | Live API call against a real Linear issue |

Run tests: `uv run pytest`
Lint: `uv run ruff check src/ tests/`

---

## Git Workflow

**Branch strategy:** Feature branches → PR → merge to main.

```
main                    ← production; protected
└── feature/<slug>      ← feature work (e.g. feature/agent-runner)
└── fix/<slug>          ← bug fixes
```

---

## Deployment

This is a CLI tool, not a deployed service. Run locally:

```bash
uv run python -m claude_engineering_agent JAM-238
```

---

## Common Pitfalls & Constraints

- **MCP Connector is beta.** Requires `betas=["mcp-client-2025-11-20"]` in every `messages.create()` call. The previous beta header (`mcp-client-2025-04-04`) is deprecated.
- **MCP Connector only supports tools.** MCP resources and prompts are not available through the connector — only tool calls.
- **MCP Connector requires HTTPS URLs.** All MCP server URLs must start with `https://`.
- **OAuth tokens expire.** Linear and GitHub MCP tokens obtained via the MCP Inspector OAuth flow have limited lifetimes. If the agent fails with auth errors, re-run the OAuth flow.
- **MCP Connector is not available on Bedrock or Vertex AI.** This project uses the direct Claude API specifically because of this.
- **Rate limits apply per-model, per-region.** Implement exponential backoff on 429 responses.
- **Max loop iterations.** The agentic loop must have a hard cap to prevent runaway token spend.

---

## Updating this document

This file is maintained by the **doc-generator** agent at phase boundaries and should reflect the current state of the codebase. If you notice drift between this document and reality, fix it — stale context is worse than no context.
