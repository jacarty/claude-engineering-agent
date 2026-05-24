"""Discover target repository context from git remote."""

import subprocess
from dataclasses import dataclass
from urllib.parse import urlsplit


class RepoDiscoveryError(Exception):
    """Raised when the target repository cannot be determined from cwd."""


@dataclass
class RepoInfo:
    """Repository owner, name, and remote URL."""

    owner: str
    name: str
    remote_url: str


def _parse_owner_name(remote_url: str) -> tuple[str, str]:
    """Extract owner and repo name from an HTTPS or SSH git remote URL."""
    url = remote_url.removesuffix(".git")

    if "://" in url:
        # HTTPS: https://github.com/owner/repo
        path = urlsplit(url).path
    else:
        # SSH: git@github.com:owner/repo
        _, path = url.split(":", 1)

    parts = path.strip("/").split("/")
    if len(parts) < 2:
        raise RepoDiscoveryError(f"Cannot parse owner/repo from remote URL: {remote_url}")
    return parts[0], parts[1]


def discover_repo() -> RepoInfo:
    """Discover the target repo from the git remote in cwd.

    Raises RepoDiscoveryError if cwd is not a git repo or has no origin remote.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RepoDiscoveryError("git is not installed or not on PATH") from None
    except subprocess.CalledProcessError:
        raise RepoDiscoveryError(
            "Not a git repository, or no 'origin' remote configured. "
            "Run claude-agent from inside a git repo with an origin remote."
        ) from None

    remote_url = result.stdout.strip()
    owner, name = _parse_owner_name(remote_url)

    return RepoInfo(owner=owner, name=name, remote_url=remote_url)
