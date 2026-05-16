---
name: presentation-outline
description: >
  Turn a topic into a structured presentation outline with slide-by-slide content and
  speaker notes. Use when the user needs to prepare a talk, presentation, pitch, or
  slide deck. Triggers include "help me prepare a presentation", "outline slides for",
  "I have a talk on", "build a deck about", "presentation outline", "slide structure",
  "help me with my talk", "pitch deck", or any request to organise content into a
  presentation format. Also use when the user has raw content or notes and needs them
  shaped into a talk structure.
---

# Presentation Outline — From Topic to Talk Structure

## What This Skill Does

This skill produces a **slide-by-slide presentation outline** with content guidance and
speaker notes. It handles the structural thinking — narrative arc, pacing, what to include
and what to cut — so the user can focus on their slides and delivery.

The output is an outline, not a finished deck. It tells the user what goes on each slide
and what to say, not how to design it.

## When to Use This Skill

Use when:

- The user needs to prepare a presentation and wants help structuring it
- A topic or set of notes needs organising into a talk format
- The user knows their content but not how to pace or sequence it
- A pitch, demo, or team presentation needs an outline

Do NOT use when:

- The user wants a written document (use technical-blog-post or write directly)
- The user wants to design slides (this skill covers structure, not design)
- The content is better as a one-pager or memo than a presentation

---

## Process

### Step 1 — Understand the Talk

Establish the parameters:

1. **Topic** — what is this presentation about?
2. **Audience** — who's in the room? What do they already know? What do they care about?
3. **Duration** — how long is the slot? (This determines slide count: roughly 1 slide
   per 1-2 minutes, depending on density.)
4. **Goal** — what should the audience think, feel, or do differently after this talk?
   One sentence.
5. **Format** — keynote, team update, technical deep dive, pitch, demo, workshop?

### Step 2 — Choose the Narrative Arc

Every good presentation has a shape. Select the arc that fits:

**Problem → Solution → Impact** (best for pitches, project updates)
- Here's the problem → here's what we did → here's what happened

**What → So What → Now What** (best for sharing insights or results)
- Here's what we found → here's why it matters → here's what to do about it

**Journey** (best for experience reports, retrospectives)
- Where we started → what we tried → what worked → where we are now

**Teach** (best for technical talks, knowledge sharing)
- Why this matters to you → the concept → how it works → try it yourself

**Contrast** (best for comparisons, persuasive talks)
- The current way → its limitations → the better way → evidence → transition path

Present the recommended arc and confirm before outlining slides.

### Step 3 — Outline Slides

For each slide, provide:

- **Slide number and title** — what appears on the slide
- **Key point** — the single thing this slide communicates (if you can't state it in
  one sentence, the slide is doing too much)
- **Content guidance** — what goes on the slide (bullet points, diagram description,
  code snippet, chart, image, demo step)
- **Speaker notes** — what the presenter says that isn't on the slide. This is where
  the story lives. 2-4 sentences.
- **Transition** — how this slide connects to the next one (the sentence that bridges them)

### Structural Rules

- **Slide 1** is always a title slide with the talk title and one sentence that makes
  the audience want to hear more.
- **Slide 2** should establish why the audience should care. Don't start with background
  or definitions — start with relevance.
- **No slide should have more than 3-4 bullet points.** If it does, split it.
- **Include breathing room.** A diagram slide, a demo, a question — something every
  5-7 slides that breaks the pattern.
- **The last slide** should not be "Questions?" or "Thank You." End on the takeaway,
  the call to action, or the forward-looking thought. Put contact info in small text
  if needed.

### Step 4 — Review

After the outline, do a quick check:

- **Pacing** — is the slide count right for the time slot?
- **Narrative** — does the story flow logically from start to finish?
- **Audience fit** — is the depth right? Too basic? Too advanced?
- **One-thing test** — can you state the entire talk's message in one sentence?

---

## Output Template

```markdown
# Presentation Outline: [Talk Title]

**Audience:** [Who]
**Duration:** [Minutes]
**Goal:** [One sentence]
**Arc:** [Problem→Solution→Impact / What→So What→Now What / etc.]

---

### Slide 1: [Title]
**Key point:** [One sentence]
**Content:** [What appears on the slide]
**Speaker notes:** [What to say]
**Transition:** [Bridge to next slide]

### Slide 2: [Title]
**Key point:** [One sentence]
**Content:** [What appears on the slide]
**Speaker notes:** [What to say]
**Transition:** [Bridge to next slide]

...

### Slide N: [Closing Title]
**Key point:** [The takeaway]
**Content:** [Final visual or statement]
**Speaker notes:** [Closing words]
```

---

## Interaction Style

- Practical and direct. The user has a talk to give and needs structure, not theory
  about presentations.
- British English spelling and punctuation.
- Be opinionated about what to cut. "You have 15 minutes and 20 slides' worth of
  content — here's what I'd drop" is more useful than including everything.
- Speaker notes should sound like natural speech, not written prose. Short sentences.
  Conversational rhythm.
- Flag slides that need the user's specific data, examples, or anecdotes with
  [YOUR EXAMPLE] or [INSERT DATA].

## Handling Edge Cases

- **User gives a topic but no constraints**: Assume a 15-minute internal talk to a
  technical audience. State the assumption and adjust if corrected.
- **User has too much content**: Help them identify the one thing and ruthlessly cut
  everything that doesn't serve it. Suggest parking cut material for a follow-up
  post or appendix slides.
- **User wants a very short talk (5 minutes / lightning talk)**: Maximum 5-6 slides.
  One key point, one example, one takeaway. No background section.
- **User wants a workshop, not a talk**: Suggest alternating between presentation slides
  and hands-on exercise blocks. Outline both.
- **Pitch deck**: Tighten the structure — problem, solution, traction/evidence, ask.
  Every slide earns its place by moving toward the ask.
