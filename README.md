# claude-engineering-agent

An adaptive research agent that takes a Linear issue, investigates it using multiple tools, and produces a contextualised technical brief — posted back to Linear as a comment.

The agent doesn't follow a fixed script. Claude generates a research plan per issue, executes it, evaluates intermediate results, and adapts the remaining plan. Findings are grounded against the repo's own skills and templates, so output is contextualised to the developer's ecosystem rather than generic advice.

**Phase 1 (current):** Adaptive research agent — issue → research → structured brief.

**Phase 2 (planned):** Full engineering pipeline — issue → research → PRD → build guide → Claude Code handoff with subagent ecosystem (code-reviewer, test-generator, phase-acceptance).

## Architecture

```
Python CLI
  → Claude API (direct, not Bedrock)
  → MCP Connector (server-side, beta mcp-client-2025-11-20):
      - Linear MCP (mcp.linear.app/mcp)
      - GitHub MCP (api.githubcopilot.com/mcp)
  → Claude server tool:
      - Web search (web_search_20250305)
  → Adaptive planning loop
  → Structured research brief
  → Linear comment delivery
```

### How it works

1. **Read** — Pull issue context (title, description, labels, parent issue, comments) via Linear MCP
2. **Plan** — Claude generates a structured research plan: which tools to call, what queries to run, what each step is trying to answer
3. **Execute with adaptation** — Run the plan step by step; after each tool call, Claude evaluates results and can add steps, skip redundant ones, refine queries, or terminate early
4. **Contextualise** — Read relevant skills and templates from this repo via GitHub MCP
5. **Synthesise** — Produce a structured research brief: Background, Key Findings, Recommended Approach, Relevant Skills/Templates, Open Questions, Next Steps
6. **Deliver** — Post brief as Linear comment, update issue labels

### Key architecture decision: MCP Connector over client-side MCP

Anthropic provides two approaches for connecting to MCP servers from the API. We use the **MCP Connector** (server-side) — passing `mcp_servers=[...]` directly in the `messages.create()` call. Anthropic's infrastructure handles connection, tool discovery, and execution. No client-side MCP code needed.

Why this over client-side MCP:

- All MCP servers are remote and URL-accessible — no local stdio servers
- We only need tools, not MCP resources or prompts
- It's the pattern Anthropic recommends for production API integrations
- Eliminates an entire client layer (session management, connection handling, tool discovery)

See `docs/decisions/` for the full ADR.

## Tool connections

| Tool | Mechanism | Purpose |
|------|-----------|---------|
| Linear | MCP Connector | Read issues, post research briefs as comments, update labels/status |
| GitHub | MCP Connector | Search code across repos, read files (including skills/agents/templates from this repo), create branches |
| Web search | Claude server tool | Research technical approaches, documentation, best practices |

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for package management
- Anthropic API key
- Linear and GitHub MCP OAuth tokens

### Installation

```bash
git clone https://github.com/jacarty/claude-engineering-agent.git
cd claude-engineering-agent
uv sync
cp .env.example .env
# Edit .env with your API keys and tokens
```

### Environment variables

| Variable | Purpose | Source |
|----------|---------|--------|
| `ANTHROPIC_API_KEY` | Claude API access | [Anthropic Console](https://console.anthropic.com/) |
| `LINEAR_MCP_TOKEN` | Linear MCP server auth | Linear OAuth flow via [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) |
| `GITHUB_MCP_TOKEN` | GitHub MCP server auth | GitHub OAuth flow via [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) |

### Usage

```bash
uv run python -m claude_engineering_agent JAM-238
```

## Project structure

```
claude-engineering-agent/
├── .claude/
│   ├── agents/                  # Claude Code subagents (code-reviewer, test-generator, etc.)
│   ├── commands/                # Claude Code custom commands
│   ├── skills/                  # Thinking and writing frameworks (ToT, GoT, ADR, etc.)
│   └── settings.json            # Claude Code tool permissions
├── docs/
│   ├── decisions/               # Architecture Decision Records
│   └── process.md               # Development process and agent cadence
├── src/
│   └── claude_engineering_agent/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       ├── config.py            # MCP server + tool configuration
│       ├── runner.py            # Agentic loop
│       └── parsing.py           # Response block extraction
├── tests/
├── pyproject.toml
├── .env.example
├── CLAUDE.md
└── README.md
```

## Skills and agents

This repo includes reusable Claude Code skills and agents from the [claude-toolkit](https://github.com/jacarty/claude-toolkit) template. The research agent reads these via GitHub MCP to contextualise its recommendations.

### Skills

| Skill | Purpose |
|-------|---------|
| `tree-of-thought` | Structured branching, evaluation, and pruning |
| `graph-of-thought` | Interconnected exploration where ideas merge and combine |
| `trade-off-analysis` | Quick pros/cons comparison with a clear recommendation |
| `requirements-elicitation` | Structured interview to turn a vague brief into a spec |
| `architecture-decision-record` | Capture a technical decision with context and rationale |
| `technical-blog-post` | Structure a topic into a publishable draft |
| `documentation-review` | Audit existing docs for gaps and clarity |
| `presentation-outline` | Turn a topic into a slide-by-slide talk structure |
| `concept-explainer` | Explain a concept with analogies and progressive depth |
| `certification-study` | Generate scenario-based practice questions |
| `project-retrospective` | Structured post-mortem to extract lessons |

### Agents

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Reviews code for style, complexity, anti-patterns |
| `code-optimiser` | Identifies performance bottlenecks and inefficiencies |
| `codebase-review` | Produces a structured repo briefing |
| `test-generator` | Generates unit tests and suggests edge cases |
| `doc-generator` | Creates and updates READMEs, docstrings, ADRs |
| `devops-reviewer` | Reviews CI/CD workflows, Dockerfiles, IaC templates |
| `refactorer` | Handles framework upgrades and pattern migrations |
| `linter` | Detects and auto-fixes formatting and style violations |
| `phase-acceptance` | Validates build-guide phase completion against PRD |

## Development

This project uses the development process defined in `docs/process.md`. Key points:

- Feature branches → PR → merge to main
- Pre-commit linting on every commit
- Pre-PR gates (code-reviewer, test-generator, doc-generator) run before PR creation
- Git hooks for secret scanning and conventional commits

### Git hooks setup

```bash
./githooks/setup-hooks.sh
```

## Licence

MIT
