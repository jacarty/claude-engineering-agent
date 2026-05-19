"""
CLI entry point for the Claude Engineering Agent

Usage:
    uv run python -m claude_engineering_agent "JAM-XX"
    uv run python -m claude_engineering_agent "JAM-XX" --spec
    uv run python -m claude_engineering_agent "JAM-XX" --spec-only

Modes:
    (default)   Research the Linear issue only.
    --spec      Research and generate a spec.
    --spec-only Generate a spec without re-running research.
"""

import argparse

from claude_engineering_agent.config import Config
from claude_engineering_agent.runner import run_agent


def main():
    """Parse CLI arguments, resolve the run mode, and execute the agent."""

    parser = argparse.ArgumentParser(description="CLI entry point for the Claude Engineering Agent")
    parser.add_argument("issue_id", help="Linear issue ID (e.g. JAM-238)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--spec", help="Run Research agent and also create the Spec", action="store_true"
    )
    group.add_argument("--spec-only", help="Create Spec only", action="store_true")
    args = parser.parse_args()

    config = Config()

    if args.spec:
        mode = "spec"
        action = "Researching and creating spec for"
    elif args.spec_only:
        mode = "spec_only"
        action = "Creating spec for"
    else:
        mode = "research"
        action = "Researching"

    print(f"{action} {args.issue_id} with model {config.model}")
    result = run_agent(config, args.issue_id, mode)
    print(result)


if __name__ == "__main__":
    main()
