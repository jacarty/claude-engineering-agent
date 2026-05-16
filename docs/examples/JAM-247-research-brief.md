jcarty@MacBookPro src % uv run python -m claude_engineering_agent JAM-247
Researching JAM-247 with model claude-sonnet-4-6

--- Iteration 1 ---
Calling Claude API...
Stop reason: end_turn
Content blocks: 41
  Tool: linear/get_issue
  Tool: github/get_file_contents
  Tool: linear/get_issue
  Tool: github/get_file_contents
  Tool: github/get_file_contents
  Tool: github/get_file_contents
  Text: I'll start by reading the Linear issue and the skills directory simultaneously....
  Text: Good. Now let me read the parent issue, the existing runner.py, and the agents directory, all in par...
  Text: Now let me run web searches on the key technical topics in parallel, and also check the config file ...
  Text: Now let me do a final targeted search on the key gap: whether `client.beta.messages.stream()` works ...
  Text: I now have everything I need. Let me compose the research brief.

---

# Research Brief: Streaming o...
  Text: The `.stream()` methods accept the same parameters as `.create()` except for the `stream` parameter ...
  Text:  Since the project already uses `client.beta.messages.create(... betas=["mcp-client-2025-11-20"])`, ...
  Text: The beta streaming infrastructure mirrors the stable implementation with additional features for bet...
  Text:

**2. Two consumption patterns; use both in combination**

...
  Text: If you don't need to process text as it arrives, the SDKs provide a way to use streaming under the h...
  Text:

The right pattern for this agent is **both**: iterate over the stream to print live output and cap...
  Text: Certain errors will be automatically retried 2 times by default, with a short exponential backoff. C...
  Text:  ...
  Text: The SDK implements automatic retry with exponential backoff for transient failures. The `max_retries...
  Text:

The SDK's default of 2 retries is too low for a 5–15 minute agentic run. Set `max_retries=4` or `5...
  Text: For 429 errors, always check for the `retry-after` header first. If present, wait exactly that durat...
  Text:  The SDK handles this internally already, but if you add a custom outer retry handler (for auth or m...
  Text: The exponential backoff pattern (2 seconds, 4 seconds, 8 seconds) avoids hammering the API during te...
  Text:  For `anthropic.APITimeoutError`: retry once with a logged warning, then re-raise with context (the ...
  Text: Claude's Model Context Protocol connector feature enables you to connect to remote MCP servers direc...
  Text:  The MCP Connector's tool execution happens server-side within each API call; from the streaming cli...
I'll start by reading the Linear issue and the skills directory simultaneously.
Good. Now let me read the parent issue, the existing runner.py, and the agents directory, all in parallel.
Now let me run web searches on the key technical topics in parallel, and also check the config file for context.
Now let me do a final targeted search on the key gap: whether `client.beta.messages.stream()` works with MCP Connector beta headers.
I now have everything I need. Let me compose the research brief.

---

# Research Brief: Streaming output, execution traces, and resilient error handling

**Issue:** JAM-247
**Tools used:** `linear_get_issue` (JAM-247, JAM-244), `github_get_file_contents` (runner.py, config.py, .claude/skills/, .claude/agents/), web search ×4

---

## Summary

JAM-247 upgrades `runner.py` from a bare blocking loop into an **observable, resilient, instrumented agentic runner**. The parent project (JAM-244) is a public portfolio piece targeting Anthropic hiring managers, so the quality of this runner — streaming UX, structured traces, graceful error recovery — is as important as the research output it produces. The current implementation in `runner.py` is ~35 lines: a `for` loop, `messages.create()`, a stop-reason check, and a `print()`. It provides zero visibility during execution (minutes of blank terminal), no error handling, no token accounting, and no trace. This issue closes all four gaps in a single file with no new modules.

---

## Key Findings

**1. `client.beta.messages.stream()` is the right entry point — and it accepts the same params as `.create()`**


The `.stream()` methods accept the same parameters as `.create()` except for the `stream` parameter itself, which is implicitly set to `True`.
 Since the project already uses `client.beta.messages.create(... betas=["mcp-client-2025-11-20"])`, switching to `client.beta.messages.stream()` with the same `mcp_servers`, `tools`, and `betas` args is the entire change to the call site.
The beta streaming infrastructure mirrors the stable implementation with additional features for beta-specific content types. Beta streams track three tool types instead of two.


**2. Two consumption patterns; use both in combination**


If you don't need to process text as it arrives, the SDKs provide a way to use streaming under the hood while returning the complete Message object, identical to what `.create()` returns. This is especially useful for requests with large max_tokens values, where the SDKs require streaming to avoid HTTP timeouts. The `.stream()` call keeps the HTTP connection alive with server-sent events, then `.get_final_message()` accumulates all events and returns the complete Message object.


The right pattern for this agent is **both**: iterate over the stream to print live output and capture trace data, then call `stream.get_final_message()` to get the final `response` object (including `stop_reason` and `usage`) for the outer agentic loop. `stream.current_message_snapshot` is available at any time mid-stream.

**3. The SDK already retries 429s and 5xxs — but you need to raise `max_retries` and handle auth errors yourself**


Certain errors will be automatically retried 2 times by default, with a short exponential backoff. Connection errors, 409 Conflict, 429 Rate Limit, and >=500 Internal errors will all be retried by default.

The SDK implements automatic retry with exponential backoff for transient failures. The `max_retries` parameter can be set at client initialization or per-request.


The SDK's default of 2 retries is too low for a 5–15 minute agentic run. Set `max_retries=4` or `5` in `get_client()` inside `config.py`. Auth failures (401) are **not** retried by the SDK — these need explicit detection and a human-readable error (`anthropic.AuthenticationError`). The issue's requirement for "clear error messages on auth failure" needs a manual `except anthropic.AuthenticationError` block.

**4. Retry-after header should drive wait time, not just backoff math**


For 429 errors, always check for the `retry-after` header first. If present, wait exactly that duration — no more, no less. Retrying earlier wastes resources and may extend your rate limit window. If no header is present, use exponential backoff starting at 1 second.
 The SDK handles this internally already, but if you add a custom outer retry handler (for auth or max-iteration recovery), follow this priority.

**5. Token usage is available on the final message object**

`response.usage` on the final `BetaMessage` returned by `stream.get_final_message()` contains `input_tokens` and `output_tokens` as integers. Accumulate `total_input` and `total_output` across iterations; print per-iteration and final summary. The issue's token tracking requirement is entirely achievable with no additional API calls.

**6. The SDK's `APITimeoutError` is a subclass of `APIConnectionError` — catch specifically**


The exponential backoff pattern (2 seconds, 4 seconds, 8 seconds) avoids hammering the API during temporary issues.
 For `anthropic.APITimeoutError`: retry once with a logged warning, then re-raise with context (the partial result, iteration number). Given `max_tokens=16384` and multi-iteration runs, long read timeouts are a real risk — the SDK's default is 10-minute total timeout, which should be sufficient, but worth confirming it's not being truncated somewhere.

**7. No new MCP-streaming-specific issues — the MCP Connector is transparent to the streaming API**


Claude's Model Context Protocol connector feature enables you to connect to remote MCP servers directly from the Messages API without a separate MCP client.
 The MCP Connector's tool execution happens server-side within each API call; from the streaming client's perspective, tool activity appears as `content_block` events of type `tool_use` / `tool_result`. The stream will show these in real time — printing them gives the "user always knows what the agent is doing" requirement.

---

## Recommended Approach

All changes go in `runner.py` and a small config change in `config.py`. No new modules.

**Step 1 — Bump `max_retries` in `config.py`**

In `get_client()`, change to:
```python
return anthropic.Anthropic(api_key=self.anthropic_api_key, max_retries=4)
```
This covers the SDK-handled retries (429, 5xx, connection errors) without any custom retry loop.

**Step 2 — Switch to `beta.messages.stream()` with a streaming event handler**

Replace the `response = client.beta.messages.create(...)` call with a `with client.beta.messages.stream(...) as stream:` block. Inside the stream context, iterate over events and:
- For `event.type == "text"`: print to terminal with `end="", flush=True`
- For content blocks where type is `tool_use` or `mcp_tool_use`: print `[Tool: {name}({input_summary})]` to terminal
- Accumulate trace data (see Step 3)

After the `with` block, call `response = stream.get_final_message()` — this replaces the old `response` variable and the rest of the loop logic is unchanged.

**Step 3 — Build the execution trace**

Create a `trace = []` list before the loop. In each iteration, append a dict after `get_final_message()`:
```python
trace.append({
    "iteration": iteration + 1,
    "stop_reason": response.stop_reason,
    "tools_called": [...],  # accumulated from stream events
    "text_blocks": [...],   # accumulated from stream events
    "usage": {"input": response.usage.input_tokens, "output": response.usage.output_tokens},
    "duration_seconds": round(time.time() - iter_start, 2),
})
```

After the loop, write `trace` as JSON to `docs/traces/{issue_id}_{timestamp}.json`.

**Step 4 — Add targeted error handling**

Wrap the `stream` context with a try/except catching:
- `anthropic.AuthenticationError` → print clear message ("Check LINEAR_MCP_TOKEN / GITHUB_MCP_PAT / ANTHROPIC_API_KEY"), re-raise
- `anthropic.APITimeoutError` → log warning with current iteration, retry once (simple re-enter the outer loop), then re-raise with partial result
- `anthropic.RateLimitError` → this shouldn't reach userland with `max_retries=4`, but log it if it does
- General `anthropic.APIStatusError` with 5xx → same

Auth failures from MCP tokens (Linear/GitHub) will surface as `APIStatusError` from the MCP Connector with a non-200 body — detect by checking `e.response` body for recognizable patterns and print a named message.

**Step 5 — Token tracking**

```python
total_input = total_output = 0
# each iteration:
total_input += response.usage.input_tokens
total_output += response.usage.output_tokens
print(f"  Tokens this iteration: {response.usage.input_tokens}in / {response.usage.output_tokens}out")
# at end:
print(f"\nTotal tokens: {total_input}in / {total_output}out")
```

**Step 6 — Ensure `docs/traces/` exists**

```python
Path("docs/traces").mkdir(parents=True, exist_ok=True)
```

---

## Relevant Skills & Templates

**`.claude/agents/code-reviewer.md`** — Useful after implementation. Run the code reviewer agent over `runner.py` before committing; the file will grow to ~150 lines with error handling, stream event processing, and trace logic. Worth a review pass to check for silent exception swallowing, correct exception hierarchy ordering, and resource cleanup (stream context manager exit).

**`.claude/agents/test-generator.md`** — The streaming loop and error handlers are good candidates for unit tests, especially the error-handling branches (mocked `anthropic.APITimeoutError`, mocked auth failure). The test generator can scaffold tests from the implementation.

No skills from `.claude/skills/` are directly relevant here — this is a focused implementation task, not a design or documentation task.

---

## Open Questions

1. **Does `client.beta.messages.stream()` actually work with `mcp_servers=` and `betas=` today?** The SDK source confirms beta streaming exists (`_beta_messages.py`) and the signatures match `create()`, but this hasn't been explicitly tested in the repo. This should be the very first thing verified — run the simplest possible `stream()` call with the MCP Connector and confirm events flow before building the full trace machinery.

2. **What do MCP tool-use events look like in the stream?** The MCP Connector executes tools server-side, so tool events may appear differently from standard `tool_use` blocks (they might use `mcp_tool_use` as a block type). Run a quick test and inspect `event.type` values to know exactly what to filter for in the live-printing code.

3. **Auth token expiry for Linear/GitHub MCPs** — The issue mentions "auth failure detection (expired MCP tokens)" but it's unclear how this surfaces through the MCP Connector. It could be a 401 from the API gateway (structured as `APIStatusError`), or it could be a Claude-level error embedded in a tool result. Needs empirical testing to know what exception or response shape to detect.

4. **Trace output directory** — The issue suggests `docs/traces/` but doesn't confirm. Worth a quick alignment check before creating the dir structure, in case a different location is expected by the portfolio README.

5. **The `max_iterations` guard currently uses a `for/else`** — the existing `else` block runs when the loop completes without breaking. This should be preserved as-is; just ensure it logs the partial `trace` before returning rather than silently discarding it.

---

## Next Steps

1. **Spike: confirm `beta.messages.stream()` works with MCP Connector** — Write a 10-line script using the existing `Config` that calls `client.beta.messages.stream()` with `mcp_servers` and `betas` and prints raw event types. Confirm events flow and identify tool-use event type names before any other work.

2. **Create git branch** — `jamescarty/jam-247-3-streaming-output-execution-traces-and-resilient-error` (already created in Linear).

3. **Update `config.py`** — Add `max_retries=4` to `get_client()`.

4. **Rewrite `runner.py`** in order: streaming → trace accumulation → token tracking → error handling. Keep each change shippable.

5. **Create `docs/traces/` directory** and add a `.gitkeep`. Add `docs/traces/*.json` to `.gitignore` if traces are large/noisy, or keep them in if they're intended as portfolio artefacts (the issue says they are).

6. **Test on 2+ JAM issues** as required by acceptance criteria — run against JAM-238 and JAM-239 (RAG sub-issues), save traces, verify they look coherent.

7. **Run the `code-reviewer` agent** over the final `runner.py` before marking done.
jcarty@MacBookPro src %
