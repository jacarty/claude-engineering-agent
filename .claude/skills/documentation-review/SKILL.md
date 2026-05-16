---
name: documentation-review
description: >
  Review existing documentation for gaps, staleness, inaccuracies, and readability.
  Use when the user wants feedback on docs they've written, wants to audit a project's
  documentation health, or asks whether their README, guide, or technical doc is any good.
  Triggers include "review my docs", "is this documentation clear", "audit the docs",
  "what's missing from this README", "improve this documentation", "review this guide",
  "is this accurate", "docs feedback", or any request to evaluate written documentation.
  Also use when the user shares a document and asks a quality question about it.
---

# Documentation Review — Audit & Improve Existing Docs

## What This Skill Does

This skill performs a **structured review of existing documentation**, identifying gaps,
staleness, inaccuracies, readability issues, and structural problems. It produces actionable
feedback the user can work through, not vague suggestions.

Good documentation review answers three questions: Is it correct? Is it complete? Can the
target reader actually use it?

## When to Use This Skill

Use when:

- The user shares a document and wants feedback
- A project's documentation needs an audit
- A README, guide, or API doc feels "off" and the user wants to know why
- The user is about to publish docs and wants a review pass

Do NOT use when:

- The user wants docs written from scratch (just write them)
- The user wants a blog post (use technical-blog-post)
- The content isn't documentation (code review is a different skill)

---

## Process

### Step 1 — Identify the Document Type and Audience

Different documents have different quality criteria. Establish:

- **Document type** — README, API reference, tutorial/guide, architecture doc, runbook,
  onboarding doc, changelog, or other
- **Target audience** — new user, experienced developer, operator, non-technical stakeholder
- **Goal** — what should the reader be able to do after reading this?

### Step 2 — Review Against Quality Dimensions

Evaluate the document across six dimensions. For each, provide a rating
(Good / Needs Work / Missing) and specific feedback.

#### Accuracy
- Are code examples correct and runnable?
- Do commands produce the stated output?
- Are version numbers, URLs, and references current?
- Do technical claims match the actual behaviour?

#### Completeness
- Are prerequisites stated?
- Are all steps included (no "then just deploy it" hand-waving)?
- Are error cases and troubleshooting covered?
- Is there a "what next?" or further reading section?

#### Structure
- Is there a clear progression from simple to complex?
- Can the reader find what they need without reading everything?
- Are headings descriptive and scannable?
- Is related content grouped logically?

#### Clarity
- Would the target audience understand this without external help?
- Are acronyms and jargon explained on first use?
- Are sentences concise? (Flag paragraphs over 5 sentences.)
- Are complex concepts supported by examples or diagrams?

#### Currency
- When was this last updated?
- Do references point to current versions of tools and libraries?
- Are deprecated features or patterns still being recommended?
- Does it reflect the current state of the codebase?

#### Usability
- Can a new reader follow this end-to-end and succeed?
- Are copy-pasteable commands and code blocks provided where appropriate?
- Is the formatting consistent (code blocks, headings, lists)?
- Is the document the right length for its purpose?

### Step 3 — Prioritised Findings

Present findings as a prioritised list:

- **Critical** — blocks the reader or is factually wrong. Fix before publishing.
- **Important** — degrades the experience significantly. Fix soon.
- **Minor** — polish items. Fix when convenient.

For each finding, state:

- **What** — the specific issue
- **Where** — the section or line
- **Why** — why it matters to the reader
- **Fix** — a concrete suggestion (not "improve this section" but "add a code example
  showing the error output when the API key is missing")

### Step 4 — Summary

A brief overall assessment:

- What's working well (always lead with this — documentation is thankless work)
- The single most impactful improvement
- Estimated effort to address the critical and important findings

---

## Output Template

```markdown
# Documentation Review: [Document Name]

**Type:** [README / Guide / API Reference / ...]
**Audience:** [Who it's for]
**Overall:** [Brief 1-2 sentence assessment]

## What's Working
[Specific positives — be genuine, not performative]

## Findings

### Critical
1. **[Issue]** — [Section] — [Why it matters] — **Fix:** [Specific suggestion]

### Important
2. **[Issue]** — [Section] — [Why it matters] — **Fix:** [Specific suggestion]

### Minor
3. **[Issue]** — [Section] — [Why it matters] — **Fix:** [Specific suggestion]

## Recommendation
[Single most impactful improvement + effort estimate]
```

---

## Interaction Style

- Constructive. Documentation is hard and often thankless. Lead with what's good.
- Specific. "The install section is unclear" is useless. "The install section doesn't
  mention that Node 18+ is required, which will cause the npm install to fail" is useful.
- Actionable. Every finding should include a concrete fix, not just a diagnosis.
- British English spelling and punctuation.
- Proportional. A 50-line README gets a lighter review than a 20-page guide. Don't
  over-review short documents.

## Handling Edge Cases

- **User shares code, not docs**: Note that this is a code review, not a doc review.
  Offer to review the code's inline documentation (comments, docstrings) or suggest
  the code-reviewer agent if they're using Claude Code.
- **Document is excellent**: Say so. A short review with genuine praise and 1-2 minor
  suggestions is better than inventing problems to seem thorough.
- **Document is very poor**: Be honest but kind. Prioritise ruthlessly — give the top
  3 critical fixes, not a 20-item list that feels overwhelming.
- **User wants a rewrite, not a review**: Suggest doing the review first to identify
  what needs changing, then rewrite the specific sections. A full rewrite without a
  review often reproduces the same problems.
