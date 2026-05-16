# Research Brief: Eval Framework — LLM-as-judge, Metrics, Multi-config Comparison

**Issue:** JAM-242
**Tools used:** Linear MCP (JAM-242, JAM-237), GitHub MCP (`.claude/skills/`, `.claude/agents/`, `trade-off-analysis/SKILL.md`), GitHub search (fca-regulatory-rag-eval repo), Web Search ×4 (RAG evaluation frameworks, LLM judge calibration, Bedrock structured output, cost tracking)

---

## Summary

JAM-242 is the centrepiece of the FCA Regulatory RAG Eval project (JAM-237): a Python evaluation harness that runs 50–100 ground-truth Q&A pairs through all 18 pipeline configurations (3 chunking × 2 embeddings × 3 retrieval methods), scores each result across 7 metrics, and emits per-question JSON detail plus an aggregated Markdown comparison table. The core challenge is threefold: (1) implementing automated retrieval metrics that work correctly given chunk-ID-based ground truth, (2) designing LLM-as-judge prompts for Claude Opus on Bedrock that produce reliable, calibrated 1–5 scores across faithfulness, hallucination, and citation, and (3) building a runner that parallelises 18 configs × ~75 questions without blowing cost, latency, or result reproducibility.

---

## Key Findings

1. **Build the eval harness from scratch rather than use RAGAS or DeepEval.** RAGAS and DeepEval are excellent general frameworks, but they impose their own LLM calls for every retrieval metric and use internal judge models you can't control. Since this project already uses Bedrock + Claude Opus as the judge and has explicit chunk-ID ground truth in the Q&A dataset, writing thin custom metric functions is more transparent, cheaper, and more portfolio-demonstrable than wrapping RAGAS.

2. **Precision@k and Recall@k are pure Python — no LLM required.** The standard implementation compares `top_k` retrieved chunk IDs against ground-truth doc lists and computes hits — straightforward array comparison. These metrics are typically computed for each query individually then averaged across the full test set, with each query mapped to its own ground-truth chunk set. These should be the first metrics implemented and the ones used to validate the runner wiring before the judge is involved.

3. **Separate judge calls per metric dimension is the right design.** Limit evaluation criteria to 3–5 dimensions per judge call — evaluating too many dimensions at once dilutes the judge's focus and reduces scoring quality. Run separate judge calls for separate concerns. Practically: use one Opus call for Faithfulness + Hallucination (they share the same context window), and a second for Citation Accuracy, rather than one megaprompt scoring all seven metrics.

4. **Use a 1–5 scale with an explicit rubric and chain-of-thought reasoning.** A 0–3 or 1–5 grading scale balances precision with explainability and makes it easier to align with human labels and provide examples for each score in the range. Asking for reasoning helps improve evaluation quality and debugging. The issue already specifies a 1–5 scale — this is well-supported by the literature.

5. **Few-shot calibration examples embedded in the judge prompt are the single highest-leverage improvement.** Setting temperature to 0.1 for consistency is recommended. Providing 2–3 examples per score level gives +25–30% accuracy improvement over zero-shot. The issue calls for 10 known-good + 10 known-bad examples for calibration — the output of that calibration run (scored examples with judge reasoning) should be folded back in as few-shot examples in the production prompt.

6. **Bedrock Converse API now natively supports structured JSON output (GA since Feb 2026).** For Converse APIs, use the `outputConfig.textFormat` request field — the model's response will conform to the specified JSON schema. Note: the InvokeModel API uses `output_config.format`; always set `additionalProperties: false` on all object types in the schema or structured outputs will not work correctly. This eliminates fragile regex parsing of judge output — define a Pydantic-style schema `{score: int, reasoning: str}` and let Bedrock enforce it.

7. **Important Bedrock structured output caveat: incompatible with citations.** Structured outputs is incompatible with citations for Anthropic models. If you enable citations while using structured outputs, the model will return a 400 error. Since the generation step uses citation grounding, structured outputs must only be used for the *judge* calls — not the generation calls.

8. **Cost tracking is extractable directly from Bedrock response metadata.** The Converse API response returns `usage.inputTokens`, `usage.outputTokens`, and `usage.totalTokens` on every call. Multiply by per-token prices for Claude Sonnet (generation), Titan/Cohere (embedding), and Opus (judge) to compute cost-per-query. This is deterministic and doesn't require any additional instrumentation.

9. **Chunk-boundary instability when changing chunking strategies makes ground-truth mapping non-trivial.** Building the ground-truth dataset takes time — you have to manually map each test question to the right context, and changing chunk boundaries reshuffles everything you've labelled. The Q&A ground-truth dataset needs to store *source document references* (FCA module + section), not raw chunk IDs, and the chunk ID lookup should be resolved dynamically at eval time per config. This is critical for supporting all 18 configs against the same ground-truth set.

10. **The `fca-regulatory-rag-eval` repo does not yet exist.** The GitHub search returned zero results — meaning this issue is building from scratch. The eval module is the fifth of the sub-issues, so the pipeline infrastructure (ingestion, chunking, embedding, retrieval) must be complete enough to query before this can be wired end-to-end.

---

## Recommended Approach

### Phase 1 — Data model and ground-truth contract (before writing eval code)
Define the Q&A ground-truth schema as a JSON file: `{question, answer, source_refs: [{doc, section, module}]}`. Separately, define the per-config chunk registry format: `{chunk_id, doc, section, module, text}`. The eval harness resolves `source_refs → chunk_ids` at runtime per config. This decouples the ground-truth set from chunking strategy.

### Phase 2 — Automated metrics module (`metrics/retrieval.py`)
Implement `precision_at_k(retrieved_ids, ground_truth_ids, k)` and `recall_at_k(...)` as pure functions. Wire into an `EvalResult` dataclass. Test with synthetic data before touching LLM calls. Also implement latency (wall-clock `time.perf_counter`) and cost aggregation (token counts from Bedrock response metadata × price table).

### Phase 3 — LLM-as-judge module (`metrics/judge.py`)
- Write a calibration runner: loads 10 known-good + 10 known-bad examples, calls Claude Opus with a zero-shot rubric, records output scores + reasoning to `calibration_results.json`.
- Review calibration output manually to confirm scoring distribution looks sensible (aim for >85% agreement with your human labelling of the known examples, per industry guidance).
- Update judge prompts with 2–3 few-shot examples per score level drawn from calibration run. Use temperature 0.1 for deterministic evaluation.
- Use Bedrock Converse API with `outputConfig.textFormat` JSON schema to enforce `{score: int (1–5), reasoning: str}` output.
- Implement three judge calls: (A) Faithfulness, (B) Hallucination Rate, (C) Citation Accuracy. Faithfulness and Hallucination share context; run them in one call with two score fields to save cost.

### Phase 4 — Single-config runner (`eval/runner.py`)
Build `run_single_config(config: PipelineConfig, qa_pairs: list) -> ConfigResult`. For each Q&A pair: call the pipeline, capture retrieved chunks + answer + latency + token counts, run automated metrics, run judge calls, assemble into `QuestionResult`. Serialise to JSONL for incremental writes (fault tolerance). Test on one config end-to-end.

### Phase 5 — Multi-config runner (`run_eval.py`)
Add `--all` / `--chunking` / `--embedding` / `--retrieval` CLI flags. Run configs sequentially (or with bounded `asyncio` concurrency — Bedrock has per-account rate limits, so don't just fire all 18 × 75 calls simultaneously). Load previously written JSONL results to skip completed configs. Aggregate into summary stats (mean/median/p95 per metric per config). Generate Markdown comparison table as final output.

**Alternative considered — using RAGAS directly:** RAGAS handles retrieval and generation metrics natively, has a Bedrock integration, and is actively maintained. The trade-off: it uses its own internal LLM judge logic (not easily swapped for Opus), it conflates your pipeline calls with its own, and it adds abstraction that obscures exactly what's happening — a liability for a portfolio project where the methodology story is the whole point. Custom implementation is more code but produces a much cleaner eval narrative.

---

## Relevant Skills & Templates

- **`.claude/skills/trade-off-analysis`** — Directly applicable when documenting the framework design decision (custom vs. RAGAS vs. DeepEval). The issue will need its approach justified for the portfolio README. Use this skill to structure the methodology section of the README.
- **`.claude/agents/test-generator.md`** — The automated metrics (`precision_at_k`, `recall_at_k`, cost computation) are pure functions with deterministic outputs. Use the test-generator agent to produce pytest coverage for these before wiring them into the full runner.
- **`.claude/agents/code-reviewer.md`** — The judge prompts are the most fragile part of this system; use the code-reviewer agent to scrutinise prompt logic, few-shot example quality, and structured output schema definitions.

The `technical-blog-post` skill is relevant to the parent issue (JAM-237), not this one specifically — but note that JAM-242's output (the comparison table + per-question JSONs) is the primary source material for that blog post.

---

## Open Questions

1. **Are the preceding pipeline phases (ingestion, chunking, embedding, retrieval — JAM-238–241) complete?** The eval runner can't be wired end-to-end until the pipeline can accept `(question, config) → (retrieved_chunks, answer, token_usage)`. If not, the runner can be built with a stub/mock interface and integrated later.

2. **What is the ground-truth format from the Q&A generation phase?** The precision/recall calculation depends on chunk IDs, but those IDs are config-specific. How source references are stored in the Q&A dataset determines the design of the ID-resolution layer. This needs agreement before implementing `metrics/retrieval.py`.

3. **Is 50–100 Q&A pairs enough for the 18-config comparison to be statistically meaningful?** At 75 questions, each config produces scores from 75 data points. Mean scores will be noisy — particularly for recall, where many regulatory questions have only 1–2 ground-truth chunks. Consider reporting 95% confidence intervals alongside means rather than raw means.

4. **What are Bedrock rate limits for Claude Opus in the target AWS account?** Running 18 configs × 75 questions × 2 judge calls per question = 2,700 Opus API calls. If rate limits are tight, the multi-config runner needs exponential backoff and a concurrency cap. Check account limits before designing the runner's async strategy.

5. **Faithfulness vs. Hallucination Rate: are these truly distinct metrics here?** In the issue they're described differently (faithfulness = "answer follows logically from context"; hallucination = "claims not grounded in any chunk"), but in practice they're highly correlated. Consider whether a single judge dimension covering both is sufficient, or whether there's a genuine distinction to preserve in the FCA regulatory domain (e.g., a model that is "faithful" but omits a critical regulatory obligation).

---

## Next Steps

1. **Confirm upstream pipeline interfaces are testable** — get the function signatures for `retrieve(question, config)` and `generate(question, chunks, config)` from whatever phases precede this issue. Write a stub implementation if needed.
2. **Define and commit the Q&A ground-truth schema** — JSON file with source references (not raw chunk IDs) per question. Confirm with the ground-truth generation output from JAM-239 or equivalent.
3. **Implement and test `precision_at_k` / `recall_at_k`** as pure Python with unit tests. Validate edge cases: no relevant chunks retrieved, more ground-truth chunks than k, etc.
4. **Write the Faithfulness judge prompt** with zero-shot rubric first, run calibration on 20 examples, review scores manually, then embed 2–3 few-shot examples per score level into the production prompt.
5. **Implement Bedrock structured output for judge calls** using `outputConfig.textFormat` JSON schema — verify `additionalProperties: false` is set to avoid silent schema violations.
6. **Build `run_single_config`** end-to-end on one config (recommend `structure-titan-hybrid` as the hypothesis config), validate all 7 metrics output correctly and JSONs look right.
7. **Extend to multi-config runner** with `--all` flag, sequential execution, incremental JSONL writes, and the Markdown table generator.
