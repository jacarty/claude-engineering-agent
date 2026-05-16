---
name: architecture-decision-record
description: >
  Generate a structured Architecture Decision Record (ADR) from a design discussion
  or decision. Use when the user has made or is making a technical decision and wants
  to document it properly. Triggers include "write an ADR", "document this decision",
  "architecture decision record", "record this design choice", "why did we choose",
  "document the rationale", or any situation where a technical decision has been made
  and the reasoning should be captured for future reference. Also use when the user
  describes a completed design discussion and wants the outcome formalised.
---

# Architecture Decision Record — Capture Design Decisions

## What This Skill Does

This skill produces a **structured ADR** that captures a technical decision, the context
that drove it, the options considered, and the rationale for the choice. The output follows
the widely-adopted Michael Nygard format with practical extensions.

Good ADRs are the institutional memory of a codebase. They answer "why did we do it this
way?" for the developer who joins in six months.

## When to Use This Skill

Use when:

- A technical decision has been made and needs documenting
- The user is weighing options and wants the discussion captured as they go
- Someone asks "why did we choose X over Y?" and there's no written record
- A design review or RFC needs a concise decision document

Do NOT use when:

- The user is still exploring options with no decision in sight (use ToT or GoT)
- The decision is trivial and reversible (just do it)
- The user wants a full design document (an ADR captures the *decision*, not the *design*)

---

## Process

### Step 1 — Identify the Decision

Clarify exactly what decision is being recorded. A good ADR addresses one decision, not
a collection of loosely related choices.

- **Decision title** — short, specific, starts with a verb or "Use" (e.g. "Use PostgreSQL
  for the metadata store", "Adopt event sourcing for order processing")
- **Status** — Proposed, Accepted, Deprecated, or Superseded (by ADR-XXX)
- **Date** — when the decision was made (or proposed)

### Step 2 — Capture the Context

Document the forces that shaped this decision. This is the most important section — it's
what makes the ADR useful in six months when the context has been forgotten.

- **What problem prompted this decision?** — the specific technical challenge or requirement
- **What constraints applied?** — team skills, timeline, budget, existing infrastructure,
  compliance requirements, performance targets
- **What assumptions were we making?** — things treated as true that influenced the choice

Write this as a narrative paragraph, not a bullet list. Context is a story, not a checklist.

### Step 3 — Document the Options

List each option that was seriously considered. For each:

- **Option name** — clear label
- **Description** — 1-2 sentences on what this option entails
- **Pros** — concrete advantages
- **Cons** — concrete disadvantages

Include the chosen option and at least one rejected alternative. If there was only one
viable option, say so and explain why alternatives were dismissed early.

### Step 4 — State the Decision

One sentence: "We will use [X] because [primary reason]."

Then a short paragraph (3-5 sentences) expanding on the rationale. Reference specific
pros from Step 3 that were decisive and specific cons from rejected options that were
disqualifying.

### Step 5 — Consequences

What follows from this decision — both positive and negative:

- **Positive consequences** — what this enables, simplifies, or improves
- **Negative consequences** — what this constrains, complicates, or rules out
- **Risks** — what could go wrong with this choice
- **Follow-up actions** — things that need to happen as a result of this decision

Be honest about the negative consequences. Every decision has trade-offs; an ADR that
lists only positives is either incomplete or dishonest.

---

## Output Template

```markdown
# ADR-[NNN]: [Decision Title]

**Status:** Accepted
**Date:** [YYYY-MM-DD]
**Deciders:** [Who was involved]

## Context

[Narrative paragraph describing the problem, constraints, and assumptions that led
to this decision.]

## Options Considered

### Option 1: [Name]
[Description]
- **Pros:** [concrete advantages]
- **Cons:** [concrete disadvantages]

### Option 2: [Name]
[Description]
- **Pros:** [concrete advantages]
- **Cons:** [concrete disadvantages]

### Option 3: [Name] (if applicable)
...

## Decision

We will use [Option X] because [primary rationale].

[Expanded rationale — 3-5 sentences referencing specific pros/cons from above.]

## Consequences

**Positive:**
- [What this enables]

**Negative:**
- [What this constrains]

**Risks:**
- [What could go wrong]

**Follow-up:**
- [ ] [Action items resulting from this decision]
```

---

## Interaction Style

- Precise and factual. ADRs are reference documents, not persuasive essays.
- Write for the future reader who has no context. Avoid jargon that won't age well;
  explain acronyms on first use.
- British English spelling and punctuation.
- If the user hasn't fully decided yet, capture the current state as "Proposed" and
  note what's needed to move to "Accepted."
- Keep it short. A good ADR is one page. If it's longer, the decision might need
  splitting into multiple ADRs.

## Handling Edge Cases

- **User describes a decision already made**: Skip the deliberation; capture the
  context and rationale from what they've shared. Ask about consequences.
- **User is mid-discussion and undecided**: Write the ADR with status "Proposed",
  document the options, and note which way the discussion is leaning.
- **Decision supersedes an earlier one**: Reference the earlier ADR by number and
  explain what changed.
- **User provides very little context**: Ask 2-3 targeted questions about why this
  decision matters and what the alternatives were, then draft the ADR.
- **Trivial decision**: Suggest it may not need an ADR. Offer to write a brief
  commit message or code comment instead.
