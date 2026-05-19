"""Tests for the implementer module."""

from claude_engineering_agent.implementer import parse_phases


class TestParsePhases:
    """Tests for parse_phases()."""

    def test_single_phase(self):
        build_guide = """\
## Phase 1: Setup

Install dependencies and configure the project.
"""
        phases = parse_phases(build_guide)
        assert len(phases) == 1
        assert phases[0]["number"] == 1
        assert phases[0]["name"] == "Setup"
        assert "Install dependencies" in phases[0]["content"]

    def test_multiple_phases(self):
        build_guide = """\
# Build Plan

Some preamble text that is not a phase.

### Phase 1: Skeleton

Create the stub files.

### Phase 2: Parser

Implement the parser with tests.

### Phase 3: Integration

Wire everything together.
"""
        phases = parse_phases(build_guide)
        assert len(phases) == 3
        assert phases[0]["number"] == 1
        assert phases[0]["name"] == "Skeleton"
        assert "stub files" in phases[0]["content"]
        assert phases[1]["number"] == 2
        assert phases[1]["name"] == "Parser"
        assert "parser with tests" in phases[1]["content"]
        assert phases[2]["number"] == 3
        assert phases[2]["name"] == "Integration"
        assert "Wire everything" in phases[2]["content"]

    def test_no_phases(self):
        build_guide = """\
# Some Document

This has no phase headers at all.
Just regular markdown content.
"""
        phases = parse_phases(build_guide)
        assert phases == []

    def test_preamble_ignored(self):
        build_guide = """\
# Requirements

Must have: feature X.

## Technical Decisions

Use library Y.

## Phase 1: Build it

Do the thing.
"""
        phases = parse_phases(build_guide)
        assert len(phases) == 1
        assert phases[0]["number"] == 1
        assert "Requirements" not in phases[0]["content"]
        assert "Technical Decisions" not in phases[0]["content"]

    def test_case_insensitive(self):
        build_guide = """\
## phase 1: Lowercase

Content here.

## PHASE 2: Uppercase

More content.
"""
        phases = parse_phases(build_guide)
        assert len(phases) == 2
        assert phases[0]["name"] == "Lowercase"
        assert phases[1]["name"] == "Uppercase"

    def test_dash_separator(self):
        build_guide = """\
### Phase 1 - Setup and config

Do setup things.
"""
        phases = parse_phases(build_guide)
        assert len(phases) == 1
        assert phases[0]["name"] == "Setup and config"

    def test_mixed_header_levels(self):
        build_guide = """\
## Phase 1: Two hashes

Content A.

### Phase 2: Three hashes

Content B.
"""
        phases = parse_phases(build_guide)
        assert len(phases) == 2
        assert phases[0]["name"] == "Two hashes"
        assert phases[1]["name"] == "Three hashes"

    def test_empty_string(self):
        assert parse_phases("") == []
