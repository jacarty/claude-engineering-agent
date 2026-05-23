"""Orchestrate Claude Code implementation via the Agent SDK."""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

from claude_engineering_agent.config import Config

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def _create_branch(issue_id: str, repo_root: Path) -> str:
    """Create a feature branch, or switch to it if it already exists."""
    branch_name = f"feat/{issue_id}"
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Created branch {branch_name}")
    except subprocess.CalledProcessError:
        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Switched to existing branch {branch_name}")
    return branch_name


def _commit_build_guide(build_guide_path: Path, issue_id: str, repo_root: Path) -> Path:
    """Copy build guide to docs/build-guides/ if needed, then git add and commit."""
    target_path = repo_root / "docs" / "build-guides" / f"{issue_id}.md"

    if build_guide_path.resolve() != target_path.resolve():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(build_guide_path, target_path)
        print(f"Copied build guide to {target_path}")

    subprocess.run(
        ["git", "add", str(target_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )

    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_root,
        capture_output=True,
    )

    if status.returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", f"chore: add build guide for {issue_id}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"Committed build guide for {issue_id}")
    else:
        print(f"Build guide for {issue_id} already committed")

    return target_path


# ---------------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------------


def _estimate_cost(phases: list[dict]) -> float:
    """Estimate implementation cost and prompt for confirmation.

    Returns the estimate in USD, or raises SystemExit if the user declines.
    """
    estimate = len(phases) * 0.05
    print(f"\n{'─' * 40}")
    print(f"  Phases: {len(phases)}")
    print(f"  Estimated cost: ${estimate:.2f}")
    print(f"  (heuristic: ${0.05:.2f} per phase)")
    print(f"{'─' * 40}")

    confirm = input("\nProceed with implementation? [y/N] ").strip().lower()
    if confirm != "y":
        print("Implementation cancelled.")
        raise SystemExit(0)

    return estimate


# ---------------------------------------------------------------------------
# Agent SDK calls
# ---------------------------------------------------------------------------


async def _run_phase(
    phase: dict,
    build_guide_path: Path,
    repo_root: Path,
    attempt: int,
    rejection_feedback: str | None,
) -> tuple[list, float]:
    """Run the implementation query() call for a single phase.

    Returns (collected_messages, cost_usd).
    """
    phase_num = phase["number"]
    phase_name = phase["name"]
    phase_content = phase["content"]

    prompt = f"""You are implementing Phase {phase_num}: {phase_name}

Here is the full phase specification from the build guide:

---
{phase_content}
---

Instructions:
1. Implement everything described in this phase specification.
2. After completing the implementation, follow the pre-PR agent cadence
   described in docs/process.md — run the appropriate agents based on
   what you changed and fold their findings into your work.
3. Commit your work with a clear commit message referencing Phase {phase_num}.
"""

    if attempt > 1 and rejection_feedback:
        prompt += f"""

IMPORTANT: This is attempt {attempt}. The previous attempt was rejected by phase-acceptance.
Here is the feedback from the rejection — address every point:

---
{rejection_feedback}
---
"""

    print(f"\n{'=' * 60}")
    print(f"  Phase {phase_num}: {phase_name} (attempt {attempt})")
    print(f"{'=' * 60}\n")

    options = ClaudeAgentOptions(
        permission_mode="acceptEdits",
        max_turns=50,
        max_budget_usd=2.00,
        cwd=str(repo_root),
        strict_mcp_config=True,
        mcp_servers={},
        setting_sources=["project"],
    )

    messages = []
    cost = 0.0

    async for message in query(prompt=prompt, options=options):
        messages.append(message)

        # Print assistant text as it arrives
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)

        # Extract cost from the result message
        if isinstance(message, ResultMessage):
            if message.total_cost_usd is not None:
                cost = message.total_cost_usd
            print(f"\n\n  Phase {phase_num} implementation cost: ${cost:.4f}")
            if message.is_error:
                print(f"  ⚠️  Agent ended with error: {message.subtype}")

    return messages, cost


async def _run_acceptance(
    phase: dict,
    build_guide_path: Path,
    repo_root: Path,
) -> tuple[bool, str, float]:
    """Run the phase-acceptance query() call.

    Returns (passed, verdict_text, cost_usd).
    """
    phase_num = phase["number"]
    phase_name = phase["name"]
    phase_content = phase["content"]

    prompt = f"""Use the phase-acceptance agent to validate Phase {phase_num}: {phase_name}

The phase specification from the build guide is:

---
{phase_content}
---

Run the phase-acceptance agent. It will check the codebase against every requirement
and verification checkpoint in the phase specification above. Report the results
exactly as the phase-acceptance agent produces them, including the final verdict
line with ✅ PASS or ❌ FAIL.
"""

    print(f"\n{'─' * 40}")
    print(f"  Running phase-acceptance for Phase {phase_num}...")
    print(f"{'─' * 40}\n")

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob", "Bash"],
        max_turns=30,
        max_budget_usd=1.00,
        cwd=str(repo_root),
        strict_mcp_config=True,
        mcp_servers={},
        setting_sources=["project"],
    )

    messages = []
    cost = 0.0
    last_assistant_text = ""

    async for message in query(prompt=prompt, options=options):
        messages.append(message)

        # Collect assistant text — we need the final one for verdict parsing
        if isinstance(message, AssistantMessage):
            text_parts = []
            for block in message.content:
                if isinstance(block, TextBlock):
                    text_parts.append(block.text)
                    print(block.text, end="", flush=True)
            if text_parts:
                last_assistant_text = "\n".join(text_parts)

        if isinstance(message, ResultMessage) and message.total_cost_usd is not None:
            cost = message.total_cost_usd

    # Parse verdict from the last assistant message
    passed = _parse_verdict(last_assistant_text)

    verdict_label = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n\n  Phase-acceptance verdict: {verdict_label}")
    print(f"  Acceptance cost: ${cost:.4f}")

    return passed, last_assistant_text, cost


def _parse_verdict(text: str) -> bool:
    """Parse pass/fail from phase-acceptance output.

    Looks for ✅ PASS or ❌ FAIL in the text. If both appear (unlikely),
    the last occurrence wins. If neither appears, defaults to False (fail).
    """
    pass_idx = text.rfind("PASS")
    fail_idx = text.rfind("FAIL")

    if pass_idx == -1 and fail_idx == -1:
        # No verdict found — treat as failure
        return False
    if pass_idx == -1:
        return False
    if fail_idx == -1:
        return True

    # Both found — last one wins
    return pass_idx > fail_idx


# ---------------------------------------------------------------------------
# Trace saving
# ---------------------------------------------------------------------------


def _save_impl_trace(
    issue_id: str,
    phases_trace: list[dict],
    total_cost: float,
) -> None:
    """Save the implementation trace as JSON to docs/traces/."""
    traces_dir = Path("docs/traces")
    traces_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{issue_id}_impl_{timestamp}.json"
    filepath = traces_dir / filename

    trace_data = {
        "issue_id": issue_id,
        "timestamp": timestamp,
        "total_cost_usd": total_cost,
        "phases": phases_trace,
    }

    filepath.write_text(json.dumps(trace_data, indent=2))
    print(f"Trace saved to {filepath}")


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class ImplementationResult:
    """Result of an implementation run."""

    issue_id: str
    phases_completed: int
    stopped_at_phase: int | None
    total_cost_usd: float
    branch_name: str


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


async def run_implementation(
    config: Config, issue_id: str, build_guide_path: Path
) -> ImplementationResult:
    """Run the full implementation pipeline.

    1. Discover repo root
    2. Create feature branch
    3. Commit build guide
    4. Parse phases
    5. Estimate cost and confirm
    6. For each phase: implement → accept → retry on fail
    """
    print(f"Starting implementation for {issue_id}")
    print(f"Build guide: {build_guide_path}")

    # --- Repo setup ---
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    repo_root = Path(result.stdout.strip())

    branch_name = _create_branch(issue_id, repo_root)
    _commit_build_guide(build_guide_path, issue_id, repo_root)

    # --- Parse phases ---
    if not build_guide_path.exists():
        print(f"❌ Build guide not found: {build_guide_path}")
        return ImplementationResult(
            issue_id=issue_id,
            phases_completed=0,
            stopped_at_phase=None,
            total_cost_usd=0.0,
            branch_name=branch_name,
        )

    build_guide_text = build_guide_path.read_text()
    phases = parse_phases(build_guide_text)

    if not phases:
        print("❌ No phases found in build guide. Check the format (## Phase N: name).")
        return ImplementationResult(
            issue_id=issue_id,
            phases_completed=0,
            stopped_at_phase=None,
            total_cost_usd=0.0,
            branch_name=branch_name,
        )

    print(f"\nFound {len(phases)} phase(s):")
    for p in phases:
        print(f"  Phase {p['number']}: {p['name']}")

    # --- Cost estimate and confirmation ---
    _estimate_cost(phases)

    # --- Phase loop ---
    total_cost = 0.0
    phases_completed = 0
    stopped_at_phase = None
    phases_trace = []
    max_attempts = 2

    for phase in phases:
        phase_num = phase["number"]
        phase_passed = False
        rejection_feedback = None

        for attempt in range(1, max_attempts + 1):
            # --- Implementation turn ---
            impl_messages, impl_cost = await _run_phase(
                phase, build_guide_path, repo_root, attempt, rejection_feedback
            )
            total_cost += impl_cost

            # --- Acceptance turn ---
            passed, verdict_text, accept_cost = await _run_acceptance(
                phase, build_guide_path, repo_root
            )
            total_cost += accept_cost

            # Record in trace
            phases_trace.append(
                {
                    "phase": phase_num,
                    "name": phase["name"],
                    "attempt": attempt,
                    "passed": passed,
                    "impl_cost_usd": impl_cost,
                    "accept_cost_usd": accept_cost,
                }
            )

            if passed:
                phase_passed = True
                phases_completed += 1
                print(f"\n✅ Phase {phase_num} complete. Running cost: ${total_cost:.4f}")
                break
            else:
                if attempt < max_attempts:
                    print(
                        f"\n⚠️  Phase {phase_num} failed acceptance (attempt {attempt}). Retrying..."
                    )
                    rejection_feedback = verdict_text
                else:
                    print(
                        f"\n❌ Phase {phase_num} failed acceptance after {max_attempts} attempts."
                    )

        if not phase_passed:
            stopped_at_phase = phase_num
            print(f"\n{'=' * 60}")
            print(f"  ❌ Implementation stopped at Phase {phase_num}: {phase['name']}")
            print(f"  Phases completed: {phases_completed}/{len(phases)}")
            print(f"  Total cost: ${total_cost:.4f}")
            print(f"{'=' * 60}\n")
            break

    else:
        # All phases completed successfully — push the branch
        subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"\n{'=' * 60}")
        print(f"  ✅ All {len(phases)} phases complete!")
        print(f"  Branch '{branch_name}' pushed to origin.")
        print(f"  Total cost: ${total_cost:.4f}")
        print(f"{'=' * 60}\n")

    # --- Save trace ---
    _save_impl_trace(issue_id, phases_trace, total_cost)

    return ImplementationResult(
        issue_id=issue_id,
        phases_completed=phases_completed,
        stopped_at_phase=stopped_at_phase,
        total_cost_usd=total_cost,
        branch_name=branch_name,
    )


# ---------------------------------------------------------------------------
# Phase parser
# ---------------------------------------------------------------------------


def parse_phases(build_guide: str) -> list[dict]:
    """Parse a build guide into phases.

    Splits on '## Phase N' or '### Phase N' headers (case-insensitive).
    Returns a list of dicts with keys: number (int), name (str), content (str).
    """
    pattern = r"^(#{2,3})\s+phase\s+(\d+)\s*[:\-—]?\s*(.*)"

    phases = []
    current_phase = None

    for line in build_guide.splitlines(keepends=True):
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            if current_phase is not None:
                current_phase["content"] = current_phase["content"].strip()
                phases.append(current_phase)

            current_phase = {
                "number": int(match.group(2)),
                "name": match.group(3).strip(),
                "content": "",
            }
        elif current_phase is not None:
            current_phase["content"] += line

    if current_phase is not None:
        current_phase["content"] = current_phase["content"].strip()
        phases.append(current_phase)

    return phases
