"""
CLI entry point for the Claude Engineering Agent

Usage:
    uv run python -m claude_engineering_agent "JAM-XX"
    uv run python -m claude_engineering_agent "JAM-XX" --spec
    uv run python -m claude_engineering_agent "JAM-XX" --spec-only
    uv run python -m claude_engineering_agent "JAM-XX" --implement-only
    uv run python -m claude_engineering_agent "JAM-XX" --implement

Modes:
    (default)       Research the Linear issue only.
    --spec          Research and generate a spec.
    --spec-only     Generate a spec without re-running research.
    --implement     Research, create spec, and implement.
    --implement-only Implement from existing build guide.
"""

import argparse
import subprocess
from pathlib import Path

import anyio

from claude_engineering_agent.config import Config
from claude_engineering_agent.implementer import run_implementation
from claude_engineering_agent.runner import run_agent


def main():
    """Parse CLI arguments, resolve the run mode, and execute the agent."""

    parser = argparse.ArgumentParser(description="CLI entry point for the Claude Engineering Agent")
    parser.add_argument("--version", action="version", version="0.1.0")
    parser.add_argument("issue_id", help="Linear issue ID (e.g. JAM-238)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--spec",
        help="Run Research agent and also create the Spec",
        action="store_true",
    )
    group.add_argument("--spec-only", help="Create Spec only", action="store_true")
    group.add_argument(
        "--implement",
        help="Run Research, create Spec and Implement",
        action="store_true",
    )
    group.add_argument(
        "--implement-only",
        help="Implement based on existing Research and Spec",
        action="store_true",
    )
    parser.add_argument(
        "--build-guide",
        help="Path to a specific build guide document",
    )
    args = parser.parse_args()

    config = Config()
    build_guide_path = (
        Path(args.build_guide)
        if args.build_guide
        else Path(f"docs/build-guides/{args.issue_id}.md")
    )

    if args.spec:
        mode = "spec"
        action = "Researching and creating spec for"
    elif args.spec_only:
        mode = "spec_only"
        action = "Creating spec for"
    elif args.implement:
        mode = "implement"
        action = "Researching, creating spec and implementing build for"
    elif args.implement_only:
        mode = "implement_only"
        action = "Implementing build for"
    else:
        mode = "research"
        action = "Researching"

    if args.build_guide and mode not in ("implement", "implement_only"):
        parser.error("--build-guide can only be used with --implement or --implement-only")

    print(f"{action} {args.issue_id} with model {config.model}")

    if mode in ("implement", "implement_only"):

        async def _run_impl():
            return await run_implementation(config, args.issue_id, build_guide_path)

        impl_result = anyio.run(_run_impl)
        print(impl_result)

        # Create PR if all phases passed and branch was pushed
        if (
            impl_result.stopped_at_phase is None
            and impl_result.phases_completed > 0
            and impl_result.branch_pushed
        ):
            print("\n🔀 Creating pull request...")
            try:
                pr_result = subprocess.run(
                    [
                        "gh",
                        "pr",
                        "create",
                        "--head",
                        impl_result.branch_name,
                        "--base",
                        "main",
                        "--title",
                        f"feat: {args.issue_id} implementation",
                        "--body",
                        (
                            f"## What\n\n"
                            f"Implementation of {args.issue_id}\n\n"
                            f"## Pipeline\n\n"
                            f"Automated via Claude Engineering Agent "
                            f"(`--implement-only`):\n"
                            f"- Phases completed: "
                            f"{impl_result.phases_completed}\n"
                            f"- Total cost: "
                            f"${impl_result.total_cost_usd:.2f}\n\n"
                            f"Closes {args.issue_id}"
                        ),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print(f"✅ PR created: {pr_result.stdout.strip()}")
            except FileNotFoundError:
                print("⚠️  `gh` CLI not found. Install it: https://cli.github.com")
                print(
                    f"  Create manually: gh pr create --head {impl_result.branch_name} --base main"
                )
            except subprocess.CalledProcessError as e:
                print(f"⚠️  PR creation failed: {e.stderr.strip()}")
                print(
                    f"  Create manually: gh pr create --head {impl_result.branch_name} --base main"
                )
    else:
        result = run_agent(config, args.issue_id, mode)
        print(result)


if __name__ == "__main__":
    main()
