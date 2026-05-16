"""
CLI entry point for the research agent.

Usage:
    uv run python -m claude_engineering_agent "JAM-XX"
"""

import argparse

from claude_engineering_agent.config import Config
from claude_engineering_agent.runner import run_agent


def main():
    """Accept input for Linear issue and pass to runner"""

    parser = argparse.ArgumentParser(description="Research agent for Linear issues")
    parser.add_argument("issue_id", help="Linear issue ID (e.g. JAM-238)")
    args = parser.parse_args()

    config = Config()
    print(f"Researching {args.issue_id} with model {config.model}")

    result = run_agent(config, args.issue_id)
    print(result)


if __name__ == "__main__":
    main()
