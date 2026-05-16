# claude-toolkit

My GitHub template repository for starting new projects with Claude Code — pre-configured with agents, skills, commands, git hooks, and a codified development process. This is a living repo that evolves as I refine my workflow, so expect it to change over time.

Feel free to fork, clone, or cherry-pick whatever is useful. Not everything will fit your setup — delete what you don't need.

The toolkit covers three surfaces: **Claude Code** (agents, commands, and skills load automatically), **Claude Desktop** (upload individual skill files to Project Knowledge), and **Claude.ai** (same as Desktop).

## What's included

### Skills (`.claude/skills/`)

Eleven reusable thinking and writing frameworks. Claude Code loads them automatically based on what you ask. For Claude Desktop or Claude.ai, upload individual `SKILL.md` files to Project Knowledge.

#### Design & Decision-Making

| Skill | Purpose | Use When |
|---|---|---|
| `tree-of-thought` | Structured branching, evaluation, and pruning | You need to compare distinct approaches and pick one |
| `graph-of-thought` | Interconnected exploration where ideas merge and combine | The best answer combines elements from multiple angles |
| `trade-off-analysis` | Quick pros/cons comparison with a clear recommendation | You have 2-3 known options and want a decisive answer |
| `requirements-elicitation` | Structured interview to turn a vague brief into a spec | You have an idea but not yet a clear specification |
| `architecture-decision-record` | Capture a technical decision with context and rationale | A design choice has been made and needs documenting |

#### Writing & Communication

| Skill | Purpose | Use When |
|---|---|---|
| `technical-blog-post` | Structure a topic or notes into a publishable draft | You want to write about something you've built or learned |
| `documentation-review` | Audit existing docs for gaps, staleness, and clarity | You want feedback on docs you've written |
| `presentation-outline` | Turn a topic into a slide-by-slide talk structure | You need to prepare a presentation or pitch |

#### Learning & Synthesis

| Skill | Purpose | Use When |
|---|---|---|
| `concept-explainer` | Explain a concept with analogies, examples, and progressive depth | You want to understand how something works before using it |
| `certification-study` | Generate scenario-based practice questions for certification exams | You're preparing for a cloud or technology certification |
| `project-retrospective` | Structured post-mortem to extract and carry forward lessons | You've finished a project and want to capture what you learned |

#### Choosing between the thinking skills

**Trade-Off Analysis** — fast, decisive, 2-3 known options. "Should I use X or Y?"

**Tree of Thought** — thorough, branching exploration. "What are all my options and which is best?"

**Graph of Thought** — deep, interconnected synthesis. "How do I combine the best parts of multiple approaches?"

When in doubt: if the options are already known and few, use Trade-Off Analysis. If you need to discover options, use Tree of Thought. If the options overlap and could be combined, use Graph of Thought.

### Agents (`.claude/agents/`)

Nine custom agents that Claude Code delegates to based on context. They can also be invoked explicitly with `@agent-name`.

| Agent | Model | Purpose |
|---|---|---|
| `code-reviewer` | Opus | Reviews code for style, complexity, anti-patterns, naming, and architectural smells. Read-only. |
| `code-optimiser` | Sonnet | Identifies performance bottlenecks, N+1 queries, unnecessary allocations, and algorithmic inefficiencies. Read-only. |
| `codebase-review` | Sonnet | Scans a repo and produces a structured briefing covering tech stack, architecture, posture assessment, and recommendations. Read-only. |
| `test-generator` | Sonnet | Generates unit tests, suggests edge cases, and reviews existing tests for quality and coverage gaps. |
| `doc-generator` | Sonnet | Creates and updates READMEs, docstrings, API docs, changelogs, and Architecture Decision Records. |
| `devops-reviewer` | Sonnet | Reviews GitHub Actions workflows, Dockerfiles, Kubernetes manifests, and Terraform/CloudFormation templates. |
| `refactorer` | Sonnet | Handles framework upgrades, dependency migrations, and pattern modernisation with incremental, test-verified changes. |
| `linter` | Haiku | Detects and auto-fixes formatting issues, unused imports, and style violations. Uses project linter config when present. |
| `phase-acceptance` | Opus | Validates that a build-guide phase is complete before the PR opens. Checks code against every PRD requirement and verification checkpoint. |

All agents have `memory: user` set, so they accumulate knowledge about your codebase patterns across sessions.

### Commands (`.claude/commands/`)

| Command | Description |
|---|---|
| `/create_worktree <branch-name>` | Creates a new git worktree in `.trees/<branch-name>`, symlinks `.venv` if present, and opens it in VS Code if available. |
| `/merge_worktree <branch-name>` | Merges a worktree branch back into the current branch, with automatic conflict resolution. |

### Development process (`docs/process.md`)

A codified development process that defines when each agent runs automatically during the PR lifecycle:

- **Pre-commit** — linter runs on every commit
- **Pre-PR gates** — code-reviewer, devops-reviewer, test-generator, and doc-generator run conditionally based on what changed, with findings folded into the branch before the PR opens
- **Phase boundaries** — codebase-review and doc-generator refresh tech-debt tracking and CLAUDE.md at the end of each build-guide phase
- **Phase acceptance** — phase-acceptance validates PRD requirements when a phase closes out
- **Trivial-change fast path** — small changes (≤ 50 lines, ≤ 2 files, no critical paths) skip all gates except the linter

The process doc also covers branch/PR cadence, issue tracking conventions, fold timing for gate findings, and how to handle agent feedback.

### Git hooks (`.githooks/`)

Local git hooks that run automatically. No external dependencies required.

| Hook | Trigger | What it does |
|---|---|---|
| `pre-commit` | Before each commit | Scans staged files for secrets (AWS keys, API tokens, private keys, passwords, connection strings) and blocks files over 5MB |
| `commit-msg` | After writing commit message | Validates Conventional Commits format (`type(scope): description`) |
| `pre-push` | Before each push | Validates branch naming follows `type/description` pattern |

All hooks can be bypassed with `--no-verify` when needed.

### GitHub templates (`.github/`)

| File | Purpose |
|---|---|
| `CODEOWNERS` | Default code ownership — set to a `@YOUR-GITHUB-USERNAME` placeholder you must replace |
| `SECURITY.md` | Security policy with vulnerability reporting instructions |
| `pull_request_template.md` | Default PR description with What/Why/How sections and a checklist |
| `ISSUE_TEMPLATE/bug_report.yml` | Structured bug report form |
| `ISSUE_TEMPLATE/feature_request.yml` | Structured feature request form |

### Claude Code permissions (`.claude/settings.json`)

Pre-approves a minimal core of tool invocations so Claude Code doesn't prompt for confirmation on routine operations. The file is JSONC (JSON with `//` comments).

**Live by default**: git, GitHub CLI, Node.js/npm/npx, Python testing (`pytest`, `ruff`, `python -m`), basic shell utilities (`grep`, `ls`, `find`, etc.), and `WebSearch`.

**Commented out — uncomment per project:**

- `uv` and `.venv/bin/*` paths — uncomment if your project uses uv or a repo-root `.venv/` directory
- `Bash(aws:*)` — uncomment on cloud projects where you trust Claude Code to run AWS CLI commands
- `Bash(terraform:*)` — uncomment on IaC projects
- Linear MCP block — uncomment if you have the Linear MCP server connected

### Configuration files

| File | Purpose |
|---|---|
| `.claude/settings.json` | Claude Code tool permissions — pre-approves common dev commands |
| `.claudeignore` | Prevents Claude from reading sensitive files — env files, secrets, keys, credentials, Terraform state, and large generated files |
| `.editorconfig` | Enforces consistent formatting across editors — indent style, line endings, trailing whitespace |
| `.gitignore` | Comprehensive ignore rules covering Python, Node.js, IDE files, secrets, build outputs, and OS-generated files |
| `CLAUDE.md` | Project context skeleton — fill in your architecture, conventions, and patterns |
| `LICENSE` | MIT licence — placeholder copyright holder you must replace |

## Getting started

### Claude Code (full toolkit)

1. Click **Use this template** on GitHub to create a new repository
2. Clone your new repo
3. Enable git hooks: `./githooks/setup-hooks.sh`
4. Update `.github/CODEOWNERS` — replace `@YOUR-GITHUB-USERNAME` with your GitHub handle or team
5. Update `LICENSE` — replace the `[year]` and `[your name]` placeholders
6. Fill in `CLAUDE.md` with your project's architecture and conventions (look for `<!-- ... -->` placeholders)
7. Open `.claude/settings.json` and uncomment any optional sections you need
8. Start Claude Code — all agents, commands, and skills are available immediately

### Claude Desktop or Claude.ai (skills only)

1. Clone or download this repo
2. Open the Claude desktop app or claude.ai
3. Create or open a **Project**
4. Click the project name to open **Project Knowledge**
5. Click **Add content** → **Upload files**
6. Upload the `SKILL.md` file from any skill folder under `.claude/skills/`

The skill will trigger automatically based on what you ask within that project.

## Using agents

Claude will automatically delegate to the right agent based on what you ask. You can also be explicit:

```
# Automatic delegation
Review the code I just changed
Lint this project
Write tests for the auth module

# Explicit invocation
@code-reviewer look at the last 3 commits
@devops-reviewer check my GitHub Actions workflow
@codebase-review give me an overview of this repo
@phase-acceptance validate phase 3
```

## Using skills

Skills trigger automatically from natural language. Examples:

```
Help me think through whether to use PostgreSQL or DynamoDB     → trade-off-analysis
I want to build a CLI tool for managing deployments              → requirements-elicitation
Explain how Kubernetes networking works                          → concept-explainer
Quiz me on AWS Bedrock for the AIP-C01 exam                     → certification-study
Write an ADR for our decision to use event sourcing              → architecture-decision-record
Help me write a blog post about what I learned building this     → technical-blog-post
```

## Customisation

### Adding agents

Drop `.md` files into `.claude/agents/` with YAML frontmatter:

```markdown
---
name: my-agent
description: When Claude should use this agent
tools: Read, Grep, Glob
model: sonnet
---

Your system prompt here.
```

### Adding skills

Create a folder in `.claude/skills/` with a `SKILL.md` file:

```markdown
---
name: my-skill
description: >
  When this skill should trigger. Include keywords and phrases
  that would appear in a user's natural language request.
---

# Skill Title

Instructions for how Claude should handle this type of request.
```

### Removing what you don't need

Everything is modular. Delete any agent, skill, command, or hook you don't use. The remaining components work independently.

### Recommended project structure

Once you start building, consider adding:

```
docs/
├── prd/                    # Product requirements documents
├── build-guides/           # Phase-by-phase implementation guides
├── decisions/              # Architecture Decision Records (ADRs)
├── process.md              # Development process (included)
└── tech-debt.md            # Known gaps and drift
```

The process doc and agents reference this structure.

## Licence

MIT
