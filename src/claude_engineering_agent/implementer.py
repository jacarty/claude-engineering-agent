"""Orchestrate Claude Code implementation via the Agent SDK."""

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
    """Parse a build guide into phases. Stub for Phase 1."""
    return []
