---
name: certification-study
description: >
  Generate scenario-based practice questions in the style of cloud certification exams.
  Use when the user is preparing for a certification (AWS, GCP, Azure, Kubernetes, or
  similar) and wants practice questions, topic review, or exam-style drilling. Triggers
  include "quiz me on", "practice questions for", "certification prep", "exam practice",
  "test me on", "study session", "drill me on", "mock exam questions", or any request
  related to certification study or exam preparation. Also use when the user names a
  specific certification (e.g. "AIP-C01", "Professional ML Engineer", "CKA") and wants
  to study.
---

# Certification Study — Scenario-Based Exam Practice

## What This Skill Does

This skill generates **realistic scenario-based practice questions** in the style of cloud
and technology certification exams. It doesn't just test recall — it tests the ability to
apply knowledge to realistic situations, which is how modern certification exams work.

The questions include detailed explanations of both the correct answer and why each
incorrect option is wrong, turning every question into a learning opportunity.

## When to Use This Skill

Use when:

- The user is studying for a certification and wants practice questions
- The user names a specific exam or domain and wants to drill
- A study session needs structure beyond "read the docs"
- The user wants to identify weak areas before an exam

Do NOT use when:

- The user wants to understand a concept (use concept-explainer)
- The user wants hands-on lab guidance (use direct assistance)
- The user wants general career advice about certifications

---

## Process

### Step 1 — Establish the Study Context

Identify:

1. **Which certification?** — specific exam code if possible (e.g. AIP-C01, PDE, CKA)
2. **Which domain or topic?** — a specific exam domain, service, or concept area. If
   the user says "everything," start with the highest-weighted exam domain.
3. **Difficulty level** — foundational (testing knowledge), intermediate (testing
   application), or advanced (testing judgement in ambiguous scenarios)
4. **How many questions?** — default to 5 if not specified

### Step 2 — Generate Questions

Each question follows this structure:

#### Question Format

- **Scenario** — 2-4 sentences describing a realistic business or technical situation.
  Include relevant constraints (budget, timeline, team size, compliance requirements,
  existing infrastructure). The scenario should require understanding, not just recall.
- **Question** — one clear question about what to do in this scenario.
- **Options** — 4 options (A-D) for single-answer questions, or "select TWO" / "select
  THREE" for multi-answer questions. Options should include:
  - The correct answer
  - A plausible distractor (correct service but wrong use case)
  - A common misconception (what someone who half-knows the topic would pick)
  - An obviously wrong option (for confidence calibration)

#### Question Quality Rules

- **No trivial recall.** "What does S3 stand for?" is not a useful practice question.
  "A company needs to store 50TB of infrequently accessed log data with 99.999999999%
  durability. Which storage class minimises cost?" — that tests application.
- **Distractors must be plausible.** If someone who studied could reasonably pick the
  wrong answer, it's a good distractor. If it's obviously wrong to anyone, replace it.
- **Include "almost right" options.** The hardest exam questions have an option that's
  90% correct but fails on one specific detail. Include at least one of these per set.
- **Vary question types.** Mix single-answer, multi-answer, and "which is the LEAST
  appropriate" questions.
- **Match exam patterns.** Use the phrasing style of the target certification. AWS
  exams love "most cost-effective" and "with the LEAST operational overhead." GCP exams
  favour "which Google Cloud service" and "what should you do."

### Step 3 — Provide Explanations

After all questions are presented and the user has answered (or asks for answers),
provide for each question:

- **Correct answer** — stated clearly
- **Why it's correct** — 2-3 sentences explaining the reasoning
- **Why each wrong answer is wrong** — 1-2 sentences per distractor, explaining the
  specific flaw. This is where the learning happens.
- **Exam tip** — one sentence of pattern recognition: "When the question mentions
  [X constraint], think [Y service]."
- **Study reference** — the specific documentation page or concept to review if this
  question was difficult

### Step 4 — Assessment

After the set, provide:

- **Score** — X/N correct
- **Weak areas** — topics where the user got questions wrong or hesitated
- **Pattern** — any recurring mistake (e.g. "you're consistently confusing managed
  services with self-hosted equivalents")
- **Next steps** — specific topics to study before the next session

---

## Output Template

### Questions (presented first, without answers)

```markdown
# Practice Questions: [Certification] — [Domain/Topic]

## Question 1
**Scenario:** [2-4 sentence realistic scenario]

**Question:** [Clear question]

A) [Option]
B) [Option]
C) [Option]
D) [Option]

---

## Question 2
...
```

### Answers (presented after user attempts, or on request)

```markdown
# Answers & Explanations

## Question 1
**Correct: [Letter]** — [Option text]

**Why:** [2-3 sentence explanation]

**Why not [A]:** [Flaw]
**Why not [B]:** [Flaw]
**Why not [C]:** [Flaw]

**Exam tip:** [Pattern recognition hint]
**Study:** [Specific reference]

---

## Assessment
**Score:** X/N
**Weak areas:** [Topics to review]
**Pattern:** [Recurring mistake, if any]
**Next session:** [What to study next]
```

---

## Interaction Style

- Present questions first, let the user attempt them, then reveal answers. Don't
  show answers immediately unless the user asks.
- If the user gets a question wrong, explain without condescension. The point is
  learning, not scoring.
- British English spelling and punctuation.
- Be honest about confidence. If a question tests a niche topic that might not appear
  on the actual exam, say so.
- Adjust difficulty based on performance. If the user gets 5/5, increase difficulty
  next round. If they get 1/5, step back to foundational questions.

## Handling Edge Cases

- **User doesn't specify a certification**: Ask which one. If they're exploring,
  suggest starting with the most popular in their area of interest.
- **User wants questions on a very narrow topic**: Generate 3-5 questions going
  deeper on that topic rather than 5 surface-level questions across a domain.
- **User wants a full mock exam**: Suggest breaking into domain-by-domain sessions
  rather than a single 65-question marathon. Fatigue degrades learning.
- **User disputes an answer**: Take it seriously. Check the reasoning, acknowledge
  if the question was ambiguous, and clarify. Exam questions can legitimately have
  debatable answers.
- **User is close to exam day**: Focus on the highest-weighted domains and the
  topics they're weakest on. Don't introduce new topics — reinforce what they know.
