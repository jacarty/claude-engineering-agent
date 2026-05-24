# Claude Engineering Agent — Claude Code Context

## Project Overview

An adaptive engineering agent that reads Linear issues and produces contextualised technical briefs, implementation specs, and automated PRs using Claude's MCP Connector, web search, and the target repo's own skills/templates. Built as a Python CLI tool — install once, run from any git repository.

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
Python CLI — installable via `uv tool install`, runs from any git repo
  → repo.py discovers target repo (owner, name) from git remote
  → runner.py reads .claude/skills/ and .claude/agents/ from cwd
  → prompts.py injects repo context and skills into system prompt
  → Claude API (direct, beta mcp-client-2025-11-20)
  → MCP Connector (server-side):
      - Linear MCP (mcp.linear.app/mcp) — read issues, post comments, update status/labels
      - GitHub MCP (api.githubcopilot.com/mcp) — search code, read files
  → Claude server tool:
      - Web search (web_search_20250305)
  → Streaming agentic loop (call until stop_reason is end_turn)
  → Output posted to Linear as comment
```

### Key architecture decisions

- **Repo-agnostic CLI** — the agent discovers everything from cwd: repo owner/name from `git remote`, skills/agents from `.claude/`, and `.env` from the local directory or `~/.config/claude-agent/.env`.
- **MCP Connector (server-side)** over client-side MCP — Anthropic's infrastructure handles connection, tool discovery, and execution. No MCP Python SDK needed.
- **Streaming** (`messages.stream()`) over blocking (`messages.create()`) — real-time visibility into tool calls and reasoning.
- **Deferred tool loading** — only eagerly load the ~10 tools the agent uses, not the 70+ available across Linear and GitHub.
- **Local skills inventory** — read `.claude/skills/` and `.claude/agents/` from the target repo's filesystem at startup, inject into the system prompt. Eliminates GitHub MCP calls for directory listings. Works with any repo's skills, not just this one.
- **Dynamic prompt building** — `prompts.py` exports builder functions (`build_research_prompt`, `build_spec_prompt`) that accept repo context and skills inventory as parameters. No hardcoded repo references.
- **Prompt-driven delivery** — Claude posts the brief and adds labels via Linear MCP within the same agentic loop. No separate Python delivery step.

### Key technology choices

- **Language:** Python 3.12+
- **Package manager:** uv
- **API client:** anthropic (Python SDK), max_retries=4
- **MCP integration:** MCP Connector (server-side via `mcp_servers` parameter)
- **CLI:** `claude-agent` via `[project.scripts]` entry point, argparse
- **Config:** python-dotenv with fallback chain (cwd → `~/.config/claude-agent/` → env vars)
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
│       ├── __main__.py              # CLI entry point (argparse, RepoDiscoveryError handling)
│       ├── config.py                # .env fallback chain, MCP server + tool config, client factory
│       ├── implementer.py           # Claude Code orchestration (phase loop + acceptance)
│       ├── prompts.py               # System prompt builders (dynamic repo context injection)
│       ├── repo.py                  # Git remote discovery (owner, name, URL parsing)
│       └── runner.py                # Streaming agentic loop with traces and error handling
└── tests/
```

---

## Key Patterns

### Repo discovery

`repo.py:discover_repo()` parses `git remote get-url origin` to extract the repo owner and name. Handles both HTTPS and SSH remote formats. Raises `RepoDiscoveryError` if cwd is not a git repo or has no origin remote — caught in `__main__.py` for a clean exit message.

### .env fallback chain

`config.py` loads environment variables in priority order (local wins):

1. `~/.config/claude-agent/.env` with `override=True`
2. cwd `.env` with `override=True` (via `find_dotenv(usecwd=True)`)

Uses `find_dotenv(usecwd=True)` because `load_dotenv()` without it searches from the module's file location — which is `~/.local/share/uv/tools/...` when installed as a global tool.

### Dynamic prompt building

`prompts.py` exports `build_research_prompt()` and `build_spec_prompt()` — functions that accept `owner`, `repo_name`, and `skills_inventory` as parameters. The base instructions are built dynamically with the target repo's context injected. No hardcoded repo references anywhere in the prompts.

### MCP Connector configuration

MCP servers are defined in `config.py:get_mcp_servers()`. Tool filtering is done via `defer_loading` in `config.py:get_tools()` — only the tools the agent actually uses are eagerly loaded.

### Agentic loop

The runner calls `client.beta.messages.stream()` in a loop. Events are processed in real time for terminal output. After each iteration, `stream.get_final_message()` provides the full response for loop control. The loop continues until `stop_reason` is `end_turn` or `max_iterations` is reached. `pause_turn` (MCP Connector server-side limit) is handled as a continuation.

### Local skills inventory

`runner.py:_build_skills_inventory()` reads `.claude/skills/` and `.claude/agents/` from cwd at startup, extracts `description` from YAML frontmatter, and returns a formatted string. This is injected into the system prompt by the builder functions. If the target repo has no skills or agents, an empty string is returned and the prompt notes their absence.

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
| Unit | pytest | Config loading, response parsing, skills inventory, repo discovery |
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
- **Max loop iterations.** Hard cap at 3 to prevent runaway token spend.
- **`pause_turn` stop reason.** The MCP Connector may return this if it hits its server-side iteration limit. The runner treats it as a continuation.
- **`load_dotenv` + global tool install.** `load_dotenv()` without `usecwd=True` on `find_dotenv` searches from the module's file location, not cwd. When installed via `uv tool install`, the module lives in `~/.local/share/uv/tools/...` — use `find_dotenv(usecwd=True)`.
- **`uv tool install --force` uses cached builds.** Run `uv cache clean claude-engineering-agent` before reinstalling to pick up source changes.

---

## Pipeline Modes

| Mode | Flag | Output |
|------|------|--------|
| Research | (default) | Research brief → Linear comment |
| Spec | `--spec` | Research + implementation spec → Linear comments |
| Spec only | `--spec-only` | Spec from existing research → Linear comment |
| Implement | `--implement` | Research + spec + Claude Code execution → PR |
| Implement only | `--implement-only` | Claude Code from existing build guide → PR |

Each step reads the previous step's output from Linear comments. Any step can be run independently with `--*-only` flags if prerequisites exist.

---

## Updating this document

This file is maintained by the **doc-generator** agent at phase boundaries and should reflect the current state of the codebase. If you notice drift between this document and reality, fix it.
