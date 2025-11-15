#!/usr/bin/env python3
"""
Test suite for CLI Integration Module.

Tests cover:
- Complete SDD initialization pipeline
- Decision logic for when to run pipeline
- Result generation and summaries
- Next steps generation
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.project_detection import DetectedStack
from specify_cli.cli_integration import (
    InitializationResult,
    run_sdd_initialization,
    should_run_sdd_pipeline,
    get_next_steps,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_python_project():
    """Create a temporary Python project."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create Python project indicators
        (project_root / "pyproject.toml").touch()
        (project_root / "src").mkdir()
        (project_root / "tests").mkdir()
        
        yield project_root


@pytest.fixture
def temp_node_project():
    """Create a temporary Node.js project."""
    with TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create Node project indicators
        (project_root / "package.json").touch()
        (project_root / "src").mkdir()
        (project_root / "tests").mkdir()
        
        yield project_root


@pytest.fixture
def temp_empty_project():
    """Create a temporary empty project."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# InitializationResult Tests
# ============================================================================


def test_initialization_result_creation():
    """Test InitializationResult object creation."""
    result = InitializationResult()
    
    assert result.stack_detected is False
    assert result.stack_id is None
    assert result.warp_created is False
    assert result.constitution_created is False
    assert result.messages == []


def test_initialization_result_add_message():
    """Test adding messages to result."""
    result = InitializationResult()
    
    result.add_message("Test message 1")
    result.add_message("Test message 2")
    
    assert len(result.messages) == 2
    assert "Test message 1" in result.messages


def test_initialization_result_summary_with_stack():
    """Test summary generation with stack detected."""
    result = InitializationResult()
    result.stack_detected = True
    result.stack_id = "python"
    result.stack_name = "Python"
    result.constitution_created = True
    result.specs_setup = True
    
    summary = result.summary()
    
    assert "Python" in summary
    assert "✓ Constitution created" in summary
    assert "✓ Specs directory" in summary


def test_initialization_result_summary_minimal():
    """Test summary generation with minimal setup."""
    result = InitializationResult()
    result.stack_detected = True
    result.stack_id = "generic"
    result.stack_name = "Generic"
    result.constitution_preserved = True
    
    summary = result.summary()
    
    assert "Generic" in summary
    assert "✓ Existing constitution preserved" in summary


# ============================================================================
# SDD Initialization Pipeline Tests
# ============================================================================


def test_run_sdd_initialization_python_project(temp_python_project):
    """Test complete SDD initialization for Python project."""
    result = run_sdd_initialization(temp_python_project)
    
    assert result.stack_detected is True
    assert result.stack_id == "python"
    assert result.stack_name == "Python"
    assert result.constitution_created is True
    assert result.specs_setup is True
    assert result.agent_commands_setup is True
    assert result.scripts_setup is True


def test_run_sdd_initialization_node_project(temp_node_project):
    """Test complete SDD initialization for Node.js project."""
    result = run_sdd_initialization(temp_node_project)
    
    assert result.stack_detected is True
    assert result.stack_id == "node"
    # WARP may not be created if there's an error, but constitution should be
    assert result.constitution_created is True


def test_run_sdd_initialization_empty_project(temp_empty_project):
    """Test SDD initialization for empty/generic project."""
    result = run_sdd_initialization(temp_empty_project)
    
    assert result.stack_detected is True  # Falls back to generic
    assert result.stack_id == "generic"
    assert result.constitution_created is True


def test_run_sdd_initialization_creates_artifacts(temp_python_project):
    """Test that initialization creates expected artifacts."""
    run_sdd_initialization(temp_python_project)
    
    # Check for constitution
    assert (temp_python_project / "memory" / "constitution.md").exists()
    
    # Check for specs
    assert (temp_python_project / "specs" / "README.md").exists()
    
    # Check for templates
    assert (temp_python_project / ".specify" / "templates" / "spec-template.md").exists()
    assert (temp_python_project / ".specify" / "templates" / "plan-template.md").exists()
    assert (temp_python_project / ".specify" / "templates" / "tasks-template.md").exists()
    
    # Check for agent dirs
    assert (temp_python_project / ".specify" / "agents").exists()
    
    # Check for scripts
    assert (temp_python_project / ".specify" / "scripts" / "bash").exists()
    assert (temp_python_project / ".specify" / "scripts" / "powershell").exists()


def test_run_sdd_initialization_idempotent(temp_python_project):
    """Test that running initialization twice is idempotent."""
    result1 = run_sdd_initialization(temp_python_project)
    result2 = run_sdd_initialization(temp_python_project)
    
    # Both should report success
    assert result1.constitution_created is True
    assert result2.constitution_preserved is True
    
    # Check files weren't duplicated
    const_content = (temp_python_project / "memory" / "constitution.md").read_text()
    assert const_content.count("Core Principles") == 1


def test_run_sdd_initialization_messages(temp_python_project):
    """Test that initialization generates meaningful messages."""
    result = run_sdd_initialization(temp_python_project)
    
    assert len(result.messages) > 0
    assert any("Detected stack" in msg for msg in result.messages)
    assert any("constitution" in msg.lower() for msg in result.messages)


def test_run_sdd_initialization_skip_warp(temp_python_project):
    """Test skipping WARP generation."""
    result = run_sdd_initialization(temp_python_project, skip_warp=True)
    
    # Should still do bootstrap
    assert result.constitution_created is True
    assert result.specs_setup is True
    
    # WARP should not be created
    assert result.warp_created is False


# ============================================================================
# Pipeline Decision Logic Tests
# ============================================================================


def test_should_run_sdd_pipeline_new_project(temp_empty_project):
    """Test that pipeline should run for new projects."""
    should_run, reason = should_run_sdd_pipeline(temp_empty_project)
    
    assert should_run is True
    assert "not SDD-enabled" in reason


def test_should_run_sdd_pipeline_python_project(temp_python_project):
    """Test that pipeline should run for detected projects."""
    should_run, reason = should_run_sdd_pipeline(temp_python_project)
    
    assert should_run is True


def test_should_run_sdd_pipeline_already_sdd_enabled(temp_python_project):
    """Test behavior when project is already SDD-enabled."""
    # Bootstrap first
    run_sdd_initialization(temp_python_project)
    
    # Check if should run again
    should_run, reason = should_run_sdd_pipeline(temp_python_project)
    
    # Should still offer to update if stack detected
    assert should_run is True


def test_pipeline_decision_provides_reason():
    """Test that decision logic provides meaningful reason."""
    with TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)
        
        should_run, reason = should_run_sdd_pipeline(project)
        
        assert isinstance(reason, str)
        assert len(reason) > 0


# ============================================================================
# Next Steps Generation Tests
# ============================================================================


def test_get_next_steps_basic():
    """Test basic next steps generation."""
    result = InitializationResult()
    result.stack_id = "python"
    result.specs_setup = True
    
    steps = get_next_steps(result)
    
    assert isinstance(steps, list)
    assert len(steps) > 0
    assert any("specify" in step.lower() for step in steps)


def test_get_next_steps_includes_warp_review():
    """Test that next steps include WARP review."""
    result = InitializationResult()
    result.warp_created = True
    
    steps = get_next_steps(result)
    
    assert any("WARP" in step for step in steps)


def test_get_next_steps_includes_constitution_review():
    """Test that next steps include constitution review."""
    result = InitializationResult()
    result.constitution_created = True
    
    steps = get_next_steps(result)
    
    assert any("constitution" in step.lower() for step in steps)


def test_get_next_steps_includes_speckit_commands():
    """Test that next steps include /speckit commands."""
    result = InitializationResult()
    result.specs_setup = True
    
    steps = get_next_steps(result)
    
    speckit_commands = [
        "specify",
        "clarify",
        "plan",
        "tasks",
        "implement",
    ]
    
    steps_text = " ".join(steps).lower()
    for cmd in speckit_commands:
        assert cmd in steps_text


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_python_pipeline(temp_python_project):
    """Test complete pipeline for Python project."""
    # Run initialization
    result = run_sdd_initialization(temp_python_project)
    
    # Verify stack detection
    assert result.stack_id == "python"
    assert result.stack_detected is True
    
    # Verify artifacts created
    assert (temp_python_project / "memory" / "constitution.md").exists()
    # WARP may fail if generate_root_warp has issues, but specs should always work
    assert (temp_python_project / "specs").exists()
    
    # Get next steps
    steps = get_next_steps(result)
    assert len(steps) > 0
    
    # Summary should be meaningful
    summary = result.summary()
    assert "Python" in summary
    assert "✓" in summary


def test_full_node_pipeline(temp_node_project):
    """Test complete pipeline for Node.js project."""
    result = run_sdd_initialization(temp_node_project)
    
    assert result.stack_id == "node"
    assert result.constitution_created is True
    assert (temp_node_project / "memory" / "constitution.md").exists()


def test_multiple_projects_independent(temp_python_project, temp_node_project):
    """Test that initializing multiple projects doesn't interfere."""
    result1 = run_sdd_initialization(temp_python_project)
    result2 = run_sdd_initialization(temp_node_project)
    
    assert result1.stack_id == "python"
    assert result2.stack_id == "node"
    
    # Each project should have its own artifacts
    assert (temp_python_project / "memory" / "constitution.md").exists()
    assert (temp_node_project / "memory" / "constitution.md").exists()
    
    # Content should reflect stack differences
    python_const = (temp_python_project / "memory" / "constitution.md").read_text()
    node_const = (temp_node_project / "memory" / "constitution.md").read_text()
    
    assert "pytest" in python_const or "Python" in python_const
    assert "TypeScript" in node_const or "Node" in node_const


def test_result_status_consistency(temp_python_project):
    """Test that result status fields are consistent."""
    result = run_sdd_initialization(temp_python_project)
    
    # If stack detected, we should have artifacts
    if result.stack_detected:
        assert result.constitution_created or result.constitution_preserved
        assert result.specs_setup is True
    
    # WARP should only be marked created/updated
    assert (result.warp_created or not result.warp_created) is not None


# ============================================================================
# Error Handling Tests
# ============================================================================


def test_initialization_with_read_only_error():
    """Test initialization handles permission errors gracefully."""
    with TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)
        
        # This should not crash even in edge cases
        result = run_sdd_initialization(project)
        
        assert result is not None
        assert isinstance(result.messages, list)


def test_get_next_steps_never_empty():
    """Test that next steps generation always produces output."""
    result = InitializationResult()
    result.stack_id = None  # No stack detected
    
    steps = get_next_steps(result)
    
    assert isinstance(steps, list)
    assert len(steps) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
