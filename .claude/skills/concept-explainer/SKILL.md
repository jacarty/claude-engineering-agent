---
name: concept-explainer
description: >
  Explain a technical concept at the right depth using analogies, examples, and
  progressive disclosure. Use when the user wants to understand how something works,
  what something is, or why something matters. Triggers include "explain", "how does
  X work", "what is X", "help me understand", "break this down", "ELI5", "teach me",
  "walk me through", "what's the intuition behind", "why does X matter", or any request
  for understanding a concept rather than performing a task. Also use when the user is
  learning a new technology, framework, or pattern and wants the mental model before
  diving into code.
---

# Concept Explainer — Build Understanding Before Building Code

## What This Skill Does

This skill explains a technical concept using **progressive disclosure** — starting with
intuition and analogy, building to accurate detail, and finishing with practical application.
It's designed for learners who want to understand the "why" before the "how."

The goal is that the user finishes the explanation able to explain the concept to someone
else in their own words, not just recognise it on an exam.

## When to Use This Skill

Use when:

- The user asks "how does X work?" or "what is X?"
- Someone is learning a new technology, pattern, or concept
- The user wants the mental model before writing code
- A concept needs to be explained at a specific level (beginner, intermediate, expert)

Do NOT use when:

- The user wants to do something, not understand something (just help them do it)
- The concept is simple enough for a one-sentence answer
- The user wants a comparison of options (use trade-off-analysis)

---

## Process

### Layer 1 — The Analogy (Intuition)

Start with an analogy or mental model that maps the concept to something the user already
understands. A good analogy:

- Uses a domain the user is likely familiar with
- Maps the key relationships correctly (not just surface similarity)
- Is honest about where it breaks down

State the analogy in 2-3 sentences, then immediately note its limitations. An analogy
that's taken too far does more harm than good.

### Layer 2 — The Accurate Explanation (Understanding)

Now explain the concept properly, using the analogy as scaffolding:

- **What it is** — precise definition in plain language
- **What problem it solves** — why this concept exists; what was hard before it
- **How it works** — the mechanism, step by step. Use a concrete example, not abstract
  description. Walk through what happens when X receives input Y.
- **Key terminology** — define the 3-5 terms someone needs to discuss this concept
  fluently. Don't front-load these as a glossary; introduce each term when it first
  becomes relevant in the explanation.

### Layer 3 — The Edges (Mastery)

The interesting stuff — where the concept gets nuanced:

- **When it works well** — the scenarios where this concept shines
- **When it breaks down** — the failure modes, limitations, and edge cases
- **Common misconceptions** — what people frequently get wrong and why
- **How it connects** — relationships to other concepts the user might know

### Layer 4 — Practice (Application)

Help the user apply what they've learned:

- **Try this** — a concrete exercise, experiment, or question that tests understanding.
  Not "implement a full system" — something achievable in 10-15 minutes that reveals
  whether the concept has landed.
- **Go deeper** — 2-3 specific resources for further learning (documentation sections,
  talks, papers — not generic "check out the docs" suggestions).

---

## Calibrating Depth

Match the explanation to the user's level. Signals to read:

- **Beginner signals**: "what is", "ELI5", "I'm new to", no jargon in their question
  → Heavy on Layer 1 and 2. Light on Layer 3. Practical Layer 4.

- **Intermediate signals**: Uses some correct terminology, asks about specific behaviour,
  "how does X handle Y?"
  → Brief Layer 1 (they may already have a mental model). Full Layer 2 and 3. Technical Layer 4.

- **Expert signals**: Precise jargon, asks about internals or edge cases, "why does X
  use Y instead of Z?"
  → Skip Layer 1. Brief Layer 2 (confirm shared understanding). Deep Layer 3. Advanced Layer 4.

When in doubt, start at intermediate and adjust based on the user's response.

---

## Output Template

```markdown
# [Concept Name]

## The Intuition
[Analogy + where it breaks down]

## How It Actually Works
[Precise explanation with concrete example]

### Key Terms
[Introduced inline, not as a glossary]

## The Edges
[When it works, when it breaks, common misconceptions, connections]

## Try It
[Concrete exercise or thought experiment]

## Go Deeper
- [Specific resource 1]
- [Specific resource 2]
```

---

## Interaction Style

- Conversational and clear. Explain like a knowledgeable colleague at a whiteboard,
  not a textbook.
- British English spelling and punctuation.
- Use concrete examples, not abstract descriptions. "Imagine you send a request to
  the server..." not "When a client-server interaction occurs..."
- Don't over-qualify. "X does Y" is better than "In most cases, under typical conditions,
  X generally tends to do Y." Be precise, not hedging.
- Admit when something is genuinely complex. "This part is confusing because it actually
  is confusing" is more helpful than pretending everything is simple.
- Check understanding with a question rather than asking "does that make sense?"

## Handling Edge Cases

- **User asks about something very broad** ("explain Kubernetes"): Narrow to the core
  concept first ("Let's start with what problem Kubernetes solves and how pods work —
  that's the foundation everything else builds on"). Offer to go deeper on specific
  areas after.
- **User asks about something very narrow** ("explain the difference between
  SameSite=Lax and SameSite=Strict"): Skip Layer 1 — they don't need an analogy.
  Go straight to the precise explanation.
- **User's mental model is wrong**: Correct it gently and explicitly. "The common
  mental model is [X], but that breaks down when [Y]. Here's a better way to think
  about it..." Don't just present the right model and hope they notice the difference.
- **Concept is genuinely simple**: Give a short, direct answer. Don't inflate a
  one-paragraph concept into a four-layer explanation.
- **User wants math or theory**: Include it in Layer 3, clearly separated so readers
  who want the intuition can stop at Layer 2.
