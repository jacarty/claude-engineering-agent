---
name: technical-blog-post
description: >
  Draft a technical blog post from a topic, experience, or set of notes. Use when the
  user wants to write about something they've built, learned, or figured out. Triggers
  include "write a blog post about", "help me write up", "turn this into a post",
  "I want to write about", "draft a technical article", "help me blog about", or any
  request to produce a written piece about a technical topic for a public or team audience.
  Also use when the user shares raw notes, a project retrospective, or a learning experience
  and wants it shaped into publishable prose.
---

# Technical Blog Post — From Notes to Publishable Draft

## What This Skill Does

This skill transforms a topic, experience, or set of raw notes into a **structured technical
blog post draft**. It handles the parts of writing that technical people find hardest:
structure, audience calibration, opening hooks, and knowing when to stop.

The output is a complete first draft ready for the user to edit, not a polished final
piece — writing is personal, and the user's voice should come through in the edit.

## When to Use This Skill

Use when:

- The user has a topic and wants help structuring a blog post
- Raw notes or a project write-up need shaping into readable prose
- The user knows what they want to say but not how to organise it
- A learning experience or project outcome would make a good post

Do NOT use when:

- The user wants documentation (use documentation-review or write docs directly)
- The user wants a presentation (use presentation-outline)
- The content is internal/private and not meant for an audience

---

## Process

### Step 1 — Understand the Post

Before writing, establish:

1. **What's the one thing?** — Every good post has a single core insight or takeaway.
   If the user can't state it in one sentence, help them find it. Everything else in
   the post serves this one thing.
2. **Who's the reader?** — Junior developer? Experienced engineer exploring a new area?
   Decision-maker evaluating a technology? The answer shapes vocabulary, depth, and
   what you can assume.
3. **What's the angle?** — Tutorial ("how to"), experience report ("what I learned"),
   comparison ("X vs Y"), opinion ("why you should/shouldn't"), or deep dive ("how X
   works under the hood"). Each has a different structure.

### Step 2 — Structure

Choose the structure that fits the angle:

**Tutorial / How-To:**
1. What we're building and why it matters
2. Prerequisites and setup
3. Step-by-step implementation (with code)
4. Results and what to watch out for
5. Where to go next

**Experience Report / "What I Learned":**
1. The situation (what I was trying to do)
2. What I expected vs what happened
3. The key insight (the one thing)
4. What I'd do differently
5. Takeaway for the reader

**Comparison / "X vs Y":**
1. Why this comparison matters now
2. What X does well
3. What Y does well
4. Where each falls short
5. When to use which

**Opinion / "Why You Should/Shouldn't":**
1. The claim (stated clearly up front)
2. The strongest evidence for the claim
3. The best counterargument (and why it doesn't hold)
4. What this means in practice
5. The nuanced conclusion

**Deep Dive / "How X Works":**
1. What X is and why understanding it matters
2. The mental model (simplified)
3. How it actually works (with detail)
4. Where the mental model breaks down
5. Practical implications

Present the chosen structure as an outline and confirm before writing.

### Step 3 — Draft

Write the full draft following these principles:

- **Open with a hook.** Not "In this blog post, I will discuss..." Start with a
  concrete scenario, a surprising fact, a problem the reader recognises, or a bold
  claim. The first two sentences determine whether anyone reads sentence three.
- **Use concrete examples.** Abstract explanations are forgettable. Code snippets,
  real numbers, actual error messages, screenshots described — these are what readers
  remember and share.
- **One idea per paragraph.** Technical readers skim. Short paragraphs with clear
  topic sentences let them find what they need.
- **Code blocks earn their place.** Every code snippet should be there for a reason.
  If it doesn't illustrate the point better than prose would, cut it.
- **Close with value.** End on the takeaway, a call to action, or a forward-looking
  thought. Not "In conclusion, we have seen that..." — just land the point.

### Step 4 — Review Pass

After the draft, do a quick review:

- **Title check** — is it specific and searchable? "How We Reduced API Latency by 40%
  with Connection Pooling" beats "Thoughts on Performance."
- **Skim test** — can a reader get the gist from headings and first sentences alone?
- **Length check** — 800-1500 words for most posts. Flag if it's running long and
  suggest cuts.
- **Missing context** — would a reader need to know something you haven't explained?

---

## Output Template

```markdown
# [Title — Specific, Searchable, Compelling]

[Opening hook — 2-3 sentences that grab attention]

## [Section 1 Heading]
[Content]

## [Section 2 Heading]
[Content with code examples where relevant]

## [Section 3 Heading]
[Content]

## [Closing Section]
[Takeaway, call to action, or forward-looking thought]
```

---

## Interaction Style

- Write in the user's voice, not Claude's. If the user writes casually, match that.
  If they're more formal, match that. When in doubt, aim for "smart friend explaining
  something at a whiteboard" — technically precise but not stiff.
- British English spelling and punctuation.
- Be opinionated about structure. "This would work better as two shorter posts" is
  useful feedback.
- Flag sections that need the user's specific experience or data — mark them with
  [YOUR EXAMPLE HERE] or [INSERT METRICS] so the user knows where to add their voice.
- Don't pad. A tight 800-word post beats a flabby 2000-word one.

## Handling Edge Cases

- **User gives a topic but no notes**: Ask 3-4 questions to surface the core insight
  and key examples, then draft.
- **User gives extensive raw notes**: Don't include everything. Identify the one thing
  and structure around it. Flag interesting material that could be a separate post.
- **User wants a series, not a single post**: Help them identify 2-3 post boundaries,
  write a series outline, then draft the first post.
- **Topic is too broad**: Narrow it. "Kubernetes" is not a blog post; "Why we moved
  from ECS to EKS and what surprised us" is.
- **User wants SEO optimisation**: Note that good technical content with a specific,
  searchable title does better than keyword-stuffed content. Suggest a clear title
  and subheadings that match what people actually search for.
