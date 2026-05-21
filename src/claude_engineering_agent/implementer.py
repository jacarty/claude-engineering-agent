"""Orchestrate Claude Code implementation via the Agent SDK."""

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from claude_engineering_agent.config import Config


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
    print(f"Starting implementation for {issue_id}")
    print(f"Build guide: {build_guide_path}")

    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    repo_root = Path(result.stdout.strip())

    _create_branch(issue_id, repo_root)

    _commit_build_guide(build_guide_path, issue_id, repo_root)

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
