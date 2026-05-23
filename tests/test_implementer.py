"""Tests for the implementer module."""

from claude_engineering_agent.implementer import _parse_verdict, parse_phases


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


class TestParseVerdict:
    """Tests for _parse_verdict()."""

    def test_pass(self):
        text = """### Phase 1: Setup — Acceptance Report

**Status: ✅ PASS**

All requirements met."""
        assert _parse_verdict(text) is True

    def test_fail(self):
        text = """### Phase 1: Setup — Acceptance Report

**Status: ❌ FAIL**

Missing items:
- Unit tests not found"""
        assert _parse_verdict(text) is False

    def test_no_verdict(self):
        text = "Some random text with no verdict markers."
        assert _parse_verdict(text) is False

    def test_empty_string(self):
        assert _parse_verdict("") is False

    def test_pass_in_longer_output(self):
        text = """Checking requirements...
Requirement 1: ✅
Requirement 2: ✅
Requirement 3: ✅

### Verdict

**Status: ✅ PASS**

All 3 requirements satisfied."""
        assert _parse_verdict(text) is True

    def test_fail_after_partial_passes(self):
        text = """Checking requirements...
Requirement 1: PASS
Requirement 2: PASS
Requirement 3: FAIL

### Verdict

**Status: ❌ FAIL**

1 of 3 requirements not met."""
        assert _parse_verdict(text) is False
