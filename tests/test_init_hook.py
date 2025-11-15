#!/usr/bin/env python3
"""
Test suite for CLI integration hook (Phase 6).

Tests cover:
- Decision logic for when to run SDD
- Hook execution and result handling
- Summary and next steps formatting
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.init_hook import (
    should_init_sdd,
    run_sdd_init_hook,
    get_sdd_next_steps,
    format_sdd_summary,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def empty_dir():
    """Create an empty temporary directory."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def python_project():
    """Create a Python project directory."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").touch()
        (root / "src").mkdir()
        yield root


@pytest.fixture
def node_project():
    """Create a Node project directory."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").touch()
        (root / "src").mkdir()
        yield root


@pytest.fixture
def sdd_project():
    """Create an SDD-enabled project directory."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "memory").mkdir()
        (root / "memory" / "constitution.md").touch()
        (root / "specs").mkdir()
        (root / "specs" / "README.md").touch()
        yield root


# ============================================================================
# Decision Logic Tests
# ============================================================================


class TestShouldInitSdd:
    """Test decision logic for when to run SDD initialization."""
    
    def test_explicit_warp_spec_flag(self, python_project):
        """Test that --warp-spec flag always enables SDD."""
        should_run, reason = should_init_sdd(python_project, warp_spec_flag=True)
        
        assert should_run is True
        assert "explicitly requested" in reason
    
    def test_detect_python_project(self, python_project):
        """Test detection of Python project triggers SDD."""
        should_run, reason = should_init_sdd(python_project, warp_spec_flag=False)
        
        assert should_run is True
        assert "detected" in reason.lower()
    
    def test_detect_node_project(self, node_project):
        """Test detection of Node project triggers SDD."""
        should_run, reason = should_init_sdd(node_project, warp_spec_flag=False)
        
        assert should_run is True
    
    def test_empty_directory_no_sdd(self, empty_dir):
        """Test empty directory doesn't trigger SDD (template will add it)."""
        should_run, reason = should_init_sdd(empty_dir, warp_spec_flag=False)
        
        assert should_run is False
        assert "template" in reason.lower() or "empty" in reason.lower()
    
    def test_already_sdd_enabled(self, sdd_project):
        """Test SDD-enabled project skips initialization."""
        should_run, reason = should_init_sdd(sdd_project, warp_spec_flag=False)
        
        assert should_run is False
        assert "SDD-enabled" in reason
    
    def test_already_sdd_with_explicit_flag(self, sdd_project):
        """Test explicit flag overrides SDD-enabled check."""
        should_run, reason = should_init_sdd(sdd_project, warp_spec_flag=True)
        
        assert should_run is True


# ============================================================================
# Hook Execution Tests
# ============================================================================


class TestRunSddInitHook:
    """Test execution of SDD initialization hook."""
    
    def test_hook_runs_for_python_project(self, python_project):
        """Test hook successfully runs for Python project."""
        result = run_sdd_init_hook(python_project, warp_spec_flag=False)
        
        assert result is not None
        assert result.stack_detected is True
        assert result.constitution_created is True
    
    def test_hook_runs_with_explicit_flag(self, empty_dir):
        """Test hook runs with explicit warp-spec flag."""
        result = run_sdd_init_hook(empty_dir, warp_spec_flag=True)
        
        assert result is not None
        assert result.stack_detected is True
    
    def test_hook_skips_already_enabled(self, sdd_project):
        """Test hook skips already SDD-enabled projects."""
        result = run_sdd_init_hook(sdd_project, warp_spec_flag=False)
        
        assert result is None
    
    def test_hook_creates_artifacts(self, python_project):
        """Test hook creates expected artifacts."""
        result = run_sdd_init_hook(python_project)
        
        assert (python_project / "memory" / "constitution.md").exists()
        assert (python_project / "specs" / "README.md").exists()
    
    def test_hook_handles_exceptions_gracefully(self):
        """Test hook handles errors gracefully."""
        # Use a non-existent path
        nonexistent = Path("/nonexistent/path/that/will/fail")
        
        result = run_sdd_init_hook(nonexistent, verbose=False)
        
        # Should return None on error (graceful failure)
        assert result is None


# ============================================================================
# Result Formatting Tests
# ============================================================================


class TestGetSddNextSteps:
    """Test next steps generation."""
    
    def test_next_steps_from_result(self, python_project):
        """Test next steps generated from result."""
        result = run_sdd_init_hook(python_project)
        steps = get_sdd_next_steps(result)
        
        assert len(steps) > 0
        assert isinstance(steps, list)
    
    def test_next_steps_empty_when_skipped(self):
        """Test next steps empty when initialization skipped."""
        steps = get_sdd_next_steps(None)
        
        assert steps == []
    
    def test_next_steps_mention_speckit(self, python_project):
        """Test next steps reference speckit commands."""
        result = run_sdd_init_hook(python_project)
        steps = get_sdd_next_steps(result)
        steps_text = "\n".join(steps).lower()
        
        assert "specify" in steps_text or "speckit" in steps_text


class TestFormatSddSummary:
    """Test summary formatting."""
    
    def test_summary_from_result(self, python_project):
        """Test summary formatted correctly."""
        result = run_sdd_init_hook(python_project)
        summary = format_sdd_summary(result)
        
        assert len(summary) > 0
        assert "Spec-Driven Development" in summary
    
    def test_summary_empty_when_skipped(self):
        """Test summary empty when initialization skipped."""
        summary = format_sdd_summary(None)
        
        assert summary == ""
    
    def test_summary_contains_status(self, python_project):
        """Test summary contains initialization status."""
        result = run_sdd_init_hook(python_project)
        summary = format_sdd_summary(result)
        
        # Should mention what was created
        assert "✓" in summary or "created" in summary.lower()


# ============================================================================
# Integration Tests
# ============================================================================


class TestHookIntegration:
    """Test hook integration scenarios."""
    
    def test_full_workflow_python(self, python_project):
        """Test complete workflow for Python project."""
        # Decide
        should_run, reason = should_init_sdd(python_project)
        assert should_run is True
        
        # Execute
        result = run_sdd_init_hook(python_project)
        assert result is not None
        
        # Format output
        summary = format_sdd_summary(result)
        steps = get_sdd_next_steps(result)
        
        assert len(summary) > 0
        assert len(steps) > 0
    
    def test_full_workflow_node(self, node_project):
        """Test complete workflow for Node project."""
        should_run, reason = should_init_sdd(node_project)
        assert should_run is True
        
        result = run_sdd_init_hook(node_project)
        assert result is not None
        
        summary = format_sdd_summary(result)
        assert "Node" in summary or "Python" in summary or "generic" in summary.lower()
    
    def test_workflow_with_explicit_flag(self, empty_dir):
        """Test workflow with explicit --warp-spec flag."""
        should_run, reason = should_init_sdd(empty_dir, warp_spec_flag=True)
        assert should_run is True
        
        result = run_sdd_init_hook(empty_dir, warp_spec_flag=True)
        assert result is not None
        
        summary = format_sdd_summary(result)
        assert len(summary) > 0
    
    def test_workflow_skip_for_sdd_project(self, sdd_project):
        """Test workflow correctly skips SDD-enabled projects."""
        should_run, reason = should_init_sdd(sdd_project)
        assert should_run is False
        
        result = run_sdd_init_hook(sdd_project)
        assert result is None
        
        summary = format_sdd_summary(result)
        assert summary == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
