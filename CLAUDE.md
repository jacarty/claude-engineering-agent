# Claude Engineering Agent — Claude Code Context

## Project Overview

An adaptive research agent that reads Linear issues and produces contextualised technical briefs using Claude's MCP Connector, web search, and the repo's own skills/templates. Built as a Python CLI. Phase 2 extends to PRD generation, build guide generation, Claude Code handoff, and PR creation.

**Process:** `docs/process.md` — branch/PR cadence, pre-commit + pre-PR agent gates, trivial-change fast path, phase-boundary rituals. Read this before any feature work.

**Issue Tracking:** Linear — project "AI and Machine Learning", team "James", key `JAM`. Parent issue: JAM-244.

---

## Rules

These are non-negotiable. They apply to every session regardless of scope.

- **Never commit directly to main.** Always create a feature or fix branch and open a PR.
- **Before pushing, verify only intended files are staged.** Run `git status` and `git diff --cached --name-only` before every commit.
- **Run lint + tests locally before opening a PR.** `uv run ruff check src/ tests/` and `uv run pytest`.
- **Read `docs/process.md` before any feature work.**
- **Never commit `.env` or any file containing API keys/tokens.**
- **Use `uv` for all package management.** No pip, no poetry.

---

## Architecture

```
Python CLI (src/claude_engineering_agent/)
  → Claude API (direct, beta mcp-client-2025-11-20)
  → MCP Connector (server-side):
      - Linear MCP (mcp.linear.app/mcp) — read issues, post comments, update status/labels
      - GitHub MCP (api.githubcopilot.com/mcp) — search code, read files
  → Claude server tool:
      - Web search (web_search_20250305)
  → Streaming agentic loop (call until stop_reason is end_turn)
  → Research brief posted to Linear as comment
```

### Key architecture decisions

- **MCP Connector (server-side)** over client-side MCP — Anthropic's infrastructure handles connection, tool discovery, and execution. No MCP Python SDK needed.
- **Streaming** (`messages.stream()`) over blocking (`messages.create()`) — real-time visibility into tool calls and reasoning.
- **Deferred tool loading** — only eagerly load the ~10 tools the agent uses, not the 70+ available across Linear and GitHub.
- **Local skills inventory** — read `.claude/skills/` and `.claude/agents/` from the local filesystem at startup, inject into the system prompt. Eliminates GitHub MCP calls for directory listings.
- **Prompt-driven delivery** — Claude posts the brief and adds labels via Linear MCP within the same agentic loop. No separate Python delivery step.

### Key technology choices

- **Language:** Python 3.12+
- **Package manager:** uv
- **API client:** anthropic (Python SDK), max_retries=4
- **MCP integration:** MCP Connector (server-side via `mcp_servers` parameter)
- **CLI:** `python -m claude_engineering_agent` with argparse
- **Config:** python-dotenv for environment variables
- **Testing:** pytest
- **Linting:** ruff

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
├── .githooks/                       # Local git hooks (conventional commits, branch naming)
├── .github/                         # GitHub templates (PR, issues, CODEOWNERS)
├── docs/
│   ├── examples/                    # Example research briefs from dogfooding
│   ├── traces/                      # Execution traces (JSON per run)
│   └── process.md                   # Development process and agent cadence
├── src/
│   └── claude_engineering_agent/
│       ├── __init__.py
│       ├── __main__.py              # CLI entry point (argparse)
│       ├── config.py                # MCP server + tool configuration, client factory
│       ├── prompts.py               # System prompt (the planning engine)
│       └── runner.py                # Streaming agentic loop with traces and error handling
└── tests/
```

---

## Key Patterns

### MCP Connector configuration

MCP servers are defined in `config.py:get_mcp_servers()`. Tool filtering is done via `defer_loading` in `config.py:get_tools()` — only the tools the agent actually uses are eagerly loaded.

### Agentic loop

The runner calls `client.beta.messages.stream()` in a loop. Events are processed in real time for terminal output. After each iteration, `stream.get_final_message()` provides the full response for loop control. The loop continues until `stop_reason` is `end_turn` or `max_iterations` is reached. `pause_turn` (MCP Connector server-side limit) is handled as a continuation.

### Local skills inventory

`runner.py:_build_skills_inventory()` reads `.claude/skills/` and `.claude/agents/` at startup, extracts `description` from YAML frontmatter, and injects a summary into the system prompt. This eliminates GitHub MCP calls for skill discovery.

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
| `GITHUB_MCP_PAT` | GitHub MCP server OAuth token |

---

## Testing

| Level | Tool | Scope |
|-------|------|-------|
| Unit | pytest | Config loading, response parsing, skills inventory |
| Integration | pytest | Live API call against a real Linear issue |

Run tests: `uv run pytest`
Lint: `uv run ruff check src/ tests/`

---

## Git Workflow

**Branch strategy:** Feature branches → PR → merge to main.

```
main                    ← production; protected
└── feature/<slug>      ← feature work
└── fix/<slug>          ← bug fixes
```

---

## Common Pitfalls & Constraints

- **MCP Connector is beta.** Requires `betas=["mcp-client-2025-11-20"]` in every API call.
- **MCP Connector only supports tools.** MCP resources and prompts are not available.
- **OAuth tokens expire.** If the agent fails with auth errors, re-run the OAuth flow via MCP Inspector.
- **MCP Connector is not available on Bedrock or Vertex AI.** This project uses the direct Claude API.
- **Rate limits apply per-model, per-region.** SDK handles retries with `max_retries=4`.
- **Max loop iterations.** Hard cap at 5 to prevent runaway token spend.
- **`pause_turn` stop reason.** The MCP Connector may return this if it hits its server-side iteration limit. The runner treats it as a continuation.
- **Run from the repo root.** The skills inventory reads `.claude/skills/` relative to the working directory.

---

## Phase 2 Roadmap

Phase 2 extends the pipeline with CLI flags that build progressively:

| Flag | Input | Output |
|------|-------|--------|
| (default) | Issue ID | Research brief → Linear comment |
| `--prd` | Issue ID | Research + PRD → Linear comments |
| `--build-guide` | Issue ID | Research + PRD + build guide → Linear comments |
| `--implement` | Issue ID | Research + PRD + build guide + Claude Code execution |
| `--full` | Issue ID | Full pipeline through to PR creation |

Each step reads the previous step's output from Linear comments. Any step can be run independently with `--*-only` flags if prerequisites exist.

---

## Updating this document

This file is maintained by the **doc-generator** agent at phase boundaries and should reflect the current state of the codebase. If you notice drift between this document and reality, fix it.
