"""Orchestrate Claude Code implementation via the Agent SDK."""

import re
from dataclasses import dataclass
from pathlib import Path

from claude_engineering_agent.config import Config


@dataclass
class ImplementationResult:
    """Result of an implementation run."""

    issue_id: str
    phases_completed: int
    stopped_at_phase: int | None
    total_cost_usd: float
    branch_name: str


async def run_implementation(
    config: Config, issue_id: str, build_guide_path: Path
) -> ImplementationResult:
    """Run the implementation pipeline. Stub for Phase 1."""
    print(f"Implementation stub for {issue_id}")
    print(f"Build guide: {build_guide_path}")
    return ImplementationResult(
        issue_id=issue_id,
        phases_completed=0,
        stopped_at_phase=None,
        total_cost_usd=0.0,
        branch_name=f"feat/{issue_id}",
    )


def parse_phases(build_guide: str) -> list[dict]:
    """Parse a build guide into phases.

    Splits on '## Phase N' or '### Phase N' headers (case-insensitive).
    Returns a list of dicts with keys: number (int), name (str), content (str).
    """
    # Match ## or ### followed by "Phase" then a number, optional colon/dash, then the name
    pattern = r"^(#{2,3})\s+phase\s+(\d+)\s*[:\-—]?\s*(.*)"

    phases = []
    current_phase = None

    for line in build_guide.splitlines(keepends=True):
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            # Save the previous phase if one was in progress
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

    # Don't forget the last phase
    if current_phase is not None:
        current_phase["content"] = current_phase["content"].strip()
        phases.append(current_phase)

    return phases
