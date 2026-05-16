---
name: project-retrospective
description: >
  Run a structured post-mortem or retrospective on a completed project, sprint, or
  significant piece of work. Use when the user wants to reflect on what happened, extract
  lessons, and decide what to carry forward. Triggers include "retrospective", "retro",
  "post-mortem", "what did we learn", "project review", "lessons learned", "what went
  well", "what went wrong", "wrap up this project", "debrief", or any request to reflect
  on completed work. Also use when the user finishes a lab, certification track, or
  learning project and wants to consolidate what they learned.
---

# Project Retrospective — Extract Lessons, Carry Forward What Matters

## What This Skill Does

This skill runs a **structured retrospective** that captures what happened, why it happened,
and what to do differently next time. It works for completed projects, sprints, learning
tracks, or any significant piece of work worth reflecting on.

The output is a concise document that's useful in three months when the user starts a
similar project and thinks "didn't I learn something about this last time?"

## When to Use This Skill

Use when:

- A project, sprint, or significant task has been completed
- A learning track or certification has been finished
- Something went wrong and the user wants to understand why
- Something went well and the user wants to replicate it
- The user wants to close out a piece of work with a structured reflection

Do NOT use when:

- The project is still in progress (help them finish it first)
- The user wants planning, not reflection (use requirements-elicitation or ToT)
- The user wants to vent, not learn (listen, then offer the retro when they're ready)

---

## Process

### Phase 1 — Set the Scope

Establish what's being retrospected:

- **What was the project/task?** — one sentence
- **What was the original goal?** — what were we trying to achieve?
- **What was the actual outcome?** — what did we actually deliver?
- **Timeline** — planned vs actual duration
- **Context** — any relevant constraints, team composition, or environmental factors

The gap between "original goal" and "actual outcome" is where the interesting lessons live.

### Phase 2 — What Went Well

Identify 3-5 things that worked. For each:

- **What happened** — specific, concrete description
- **Why it worked** — the underlying reason (process, decision, skill, luck?)
- **Replicable?** — can this be deliberately repeated, or was it situational?

Be specific. "Communication was good" is useless. "Daily 10-minute standups kept
everyone aligned on blockers and prevented the two-week delay we had last quarter"
is a lesson.

### Phase 3 — What Didn't Go Well

Identify 3-5 things that didn't work. For each:

- **What happened** — specific description, no blame
- **Root cause** — why did this happen? Use "5 whys" if needed to get past symptoms
  to causes
- **Impact** — what did this cost (time, quality, morale, money)?
- **Preventable?** — with hindsight, what would have caught this earlier?

Frame this as "what we'd do differently," not "what went wrong." The goal is learning,
not punishment.

### Phase 4 — Surprises

Things that were unexpected — positive or negative:

- **What surprised us?** — things we didn't anticipate
- **Why didn't we anticipate them?** — blind spot, lack of experience, wrong assumption?
- **What would we look for next time?** — the early warning sign we now know to watch for

Surprises are often the most valuable category because they reveal gaps in the team's
mental model.

### Phase 5 — Carry Forward

This is the most important section — it's what makes the retro actionable.

#### Keep Doing
- Practices, habits, or approaches that should become standard

#### Start Doing
- New practices to adopt based on lessons learned

#### Stop Doing
- Things that didn't add value or actively hurt

#### Key Learnings
- 3-5 bullet points that capture the most important insights. Write these as standalone
  statements that make sense without reading the full retro. They should be specific
  enough to be actionable and general enough to apply to future projects.

---

## Output Template

```markdown
# Retrospective: [Project Name]

**Date:** [YYYY-MM-DD]
**Goal:** [Original objective]
**Outcome:** [What actually happened]
**Timeline:** [Planned vs actual]

## What Went Well
1. **[Thing]** — [Why it worked] — [Replicable? Yes/No/Partially]
2. ...

## What Didn't Go Well
1. **[Thing]** — **Root cause:** [Why] — **Impact:** [Cost] — **Prevention:** [What to do next time]
2. ...

## Surprises
1. **[Surprise]** — **Why unexpected:** [Reason] — **Watch for next time:** [Early signal]
2. ...

## Carry Forward

### Keep Doing
- [Practice to continue]

### Start Doing
- [New practice to adopt]

### Stop Doing
- [Practice to drop]

### Key Learnings
- [Standalone insight 1]
- [Standalone insight 2]
- [Standalone insight 3]
```

---

## Interaction Style

- Reflective and honest. A retro that only lists positives is a missed opportunity.
  A retro that only lists negatives is demoralising. Balance both.
- British English spelling and punctuation.
- Ask probing questions. "Why?" is the most useful question in a retrospective.
  When the user gives a surface-level answer, dig one level deeper.
- No blame. Frame everything as system-level learning, not individual failure.
  "The deploy process didn't catch the regression" not "James broke production."
- Be concrete. Vague lessons ("communicate better") don't change behaviour.
  Specific lessons ("send a summary Slack message after each design decision so
  the team doesn't discover changes in code review") do.

## Handling Edge Cases

- **User gives a brief summary and wants a retro**: Ask 3-4 targeted follow-up
  questions to surface the non-obvious lessons, then write the retro.
- **Project was a disaster**: Acknowledge it, focus on root causes and prevention,
  and ensure the "carry forward" section is actionable. Even failed projects
  produce valuable lessons.
- **Project was a huge success**: Still do the retro. Success hides problems that
  will surface in the next project. "What almost went wrong?" is a productive
  question for successful projects.
- **Learning project or certification**: Adapt the framing — "what went well"
  becomes "what learning approaches worked," "what didn't go well" becomes
  "where did I get stuck and why," and "carry forward" becomes "study habits
  and techniques to keep/change."
- **User wants a team retro format**: Suggest running Phases 2-4 as a group
  exercise (everyone contributes items), then consolidate into Phase 5 together.
  The skill can structure the output from a group session.
