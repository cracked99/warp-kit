#!/usr/bin/env python3
"""
Test suite for SDD Bootstrap Module.

Tests cover:
- Constitution creation (with preservation of existing files)
- Specs directory setup
- Template creation and idempotency
- Agent command setup
- Helper scripts setup
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.project_detection import DetectedStack, SDDStatus
from specify_cli.sdd_bootstrap import (
    create_or_update_constitution,
    setup_specs_directory,
    setup_agent_commands,
    setup_specify_scripts,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_project_root():
    """Create a temporary project directory."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_stack():
    """Create a sample detected stack."""
    return DetectedStack(
        id="node",
        name="Node.js / TypeScript",
        confidence_score=0.85,
        signals=["package.json", "tsconfig.json"],
        test_framework="jest",
        source_dir="src",
        test_dir="tests",
        commands={},
        ci_present=False,
    )


@pytest.fixture
def sample_sdd_status():
    """Create a sample SDD status."""
    return SDDStatus(
        has_constitution=False,
        has_specs=False,
        has_specify_dir=False,
        has_warp_root=False,
        has_warp_subdirs={},
    )


# ============================================================================
# Constitution Tests
# ============================================================================


def test_create_constitution_new(temp_project_root, sample_stack, sample_sdd_status):
    """Test creating a new constitution file."""
    was_created, action = create_or_update_constitution(
        temp_project_root, sample_stack, sample_sdd_status
    )
    
    assert was_created is True
    assert action == "created"
    
    const_file = temp_project_root / "memory" / "constitution.md"
    assert const_file.exists()
    
    content = const_file.read_text()
    assert "Constitution" in content
    assert "Spec-Driven Development" in content
    assert "Core Principles" in content


def test_create_constitution_preserves_existing(temp_project_root, sample_stack, sample_sdd_status):
    """Test that existing constitution is preserved."""
    # Create existing constitution
    memory_dir = temp_project_root / "memory"
    memory_dir.mkdir()
    const_file = memory_dir / "constitution.md"
    original_content = "# My Custom Constitution\n\nCustom content"
    const_file.write_text(original_content)
    
    # Try to create (should preserve)
    was_created, action = create_or_update_constitution(
        temp_project_root, sample_stack, sample_sdd_status
    )
    
    assert was_created is False
    assert action == "preserved"
    assert const_file.read_text() == original_content


def test_constitution_contains_stack_specific_notes(temp_project_root, sample_sdd_status):
    """Test that constitution includes stack-specific notes."""
    stacks_to_test = [
        ("node", "Node.js / TypeScript"),
        ("python", "Python"),
        ("dotnet", ".NET / C#"),
        ("go", "Go"),
        ("java", "Java"),
        ("rust", "Rust"),
    ]
    
    for stack_id, stack_name in stacks_to_test:
        stack = DetectedStack(
            id=stack_id,
            name=stack_name,
            confidence_score=0.90,
            signals=[],
            test_framework="",
            source_dir="",
            test_dir="",
            commands={},
            ci_present=False,
        )
        
        was_created, _ = create_or_update_constitution(
            temp_project_root / stack_id, stack, sample_sdd_status
        )
        
        assert was_created is True
        
        const_file = temp_project_root / stack_id / "memory" / "constitution.md"
        content = const_file.read_text()
        
        # Check for stack-specific content
        if stack_id == "node":
            assert "Node.js" in content or "TypeScript" in content
        elif stack_id == "python":
            assert "pytest" in content or "Python" in content
        elif stack_id == "dotnet":
            assert ".NET" in content or "C#" in content


def test_constitution_project_name_substitution(temp_project_root, sample_stack, sample_sdd_status):
    """Test that project name is substituted in constitution."""
    project_with_name = temp_project_root / "my-project"
    project_with_name.mkdir()
    
    create_or_update_constitution(project_with_name, sample_stack, sample_sdd_status)
    
    const_file = project_with_name / "memory" / "constitution.md"
    content = const_file.read_text()
    
    assert "my-project Constitution" in content


# ============================================================================
# Specs Directory Tests
# ============================================================================


def test_setup_specs_directory_creates_readme(temp_project_root):
    """Test that specs directory setup creates README."""
    actions = setup_specs_directory(temp_project_root)
    
    specs_readme = temp_project_root / "specs" / "README.md"
    assert specs_readme.exists()
    
    content = specs_readme.read_text()
    assert "Specifications" in content
    assert "User Stories" not in content  # README != template


def test_setup_specs_creates_templates(temp_project_root):
    """Test that specs directory setup creates template files."""
    actions = setup_specs_directory(temp_project_root)
    
    templates_dir = temp_project_root / ".specify" / "templates"
    assert templates_dir.exists()
    
    template_files = [
        "spec-template.md",
        "plan-template.md",
        "tasks-template.md",
    ]
    
    for template_file in template_files:
        template_path = templates_dir / template_file
        assert template_path.exists()
        
        content = template_path.read_text()
        assert len(content) > 0
        assert "{{" in content  # Templates have placeholders


def test_setup_specs_idempotent(temp_project_root):
    """Test that setup_specs_directory is idempotent."""
    # First call
    actions_1 = setup_specs_directory(temp_project_root)
    created_count_1 = sum(1 for created, _ in actions_1 if created)
    
    # Second call
    actions_2 = setup_specs_directory(temp_project_root)
    created_count_2 = sum(1 for created, _ in actions_2 if created)
    
    # Second call should not create anything new
    assert created_count_2 == 0
    assert created_count_1 > 0


def test_specs_templates_have_placeholders(temp_project_root):
    """Test that templates contain placeholder variables."""
    setup_specs_directory(temp_project_root)
    
    spec_template = temp_project_root / ".specify" / "templates" / "spec-template.md"
    plan_template = temp_project_root / ".specify" / "templates" / "plan-template.md"
    tasks_template = temp_project_root / ".specify" / "templates" / "tasks-template.md"
    
    # All should have FEATURE_NAME placeholder
    assert "{{FEATURE_NAME}}" in spec_template.read_text()
    assert "{{FEATURE_NAME}}" in plan_template.read_text()
    assert "{{FEATURE_NAME}}" in tasks_template.read_text()


# ============================================================================
# Agent Commands Tests
# ============================================================================


def test_setup_agent_commands_creates_dir(temp_project_root):
    """Test that agent commands setup creates directory."""
    actions = setup_agent_commands(temp_project_root)
    
    agents_dir = temp_project_root / ".specify" / "agents"
    assert agents_dir.exists()
    
    readme = agents_dir / "README.md"
    assert readme.exists()


def test_setup_agent_commands_idempotent(temp_project_root):
    """Test that setup_agent_commands is idempotent."""
    actions_1 = setup_agent_commands(temp_project_root)
    created_count_1 = sum(1 for created, _ in actions_1 if created)
    
    actions_2 = setup_agent_commands(temp_project_root)
    created_count_2 = sum(1 for created, _ in actions_2 if created)
    
    assert created_count_2 == 0
    assert created_count_1 > 0


# ============================================================================
# Scripts Setup Tests
# ============================================================================


def test_setup_specify_scripts_creates_directories(temp_project_root):
    """Test that scripts setup creates bash and powershell directories."""
    actions = setup_specify_scripts(temp_project_root)
    
    bash_dir = temp_project_root / ".specify" / "scripts" / "bash"
    ps_dir = temp_project_root / ".specify" / "scripts" / "powershell"
    
    assert bash_dir.exists()
    assert ps_dir.exists()
    
    assert (bash_dir / "README.md").exists()
    assert (ps_dir / "README.md").exists()


def test_setup_specify_scripts_idempotent(temp_project_root):
    """Test that setup_specify_scripts is idempotent."""
    actions_1 = setup_specify_scripts(temp_project_root)
    created_count_1 = sum(1 for created, _ in actions_1 if created)
    
    actions_2 = setup_specify_scripts(temp_project_root)
    created_count_2 = sum(1 for created, _ in actions_2 if created)
    
    assert created_count_2 == 0
    assert created_count_1 > 0


def test_setup_specify_scripts_content(temp_project_root):
    """Test that scripts READMEs have appropriate content."""
    setup_specify_scripts(temp_project_root)
    
    bash_readme = temp_project_root / ".specify" / "scripts" / "bash" / "README.md"
    ps_readme = temp_project_root / ".specify" / "scripts" / "powershell" / "README.md"
    
    assert "Helper scripts" in bash_readme.read_text()
    assert "Helper scripts" in ps_readme.read_text()


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_bootstrap_creates_structure(temp_project_root, sample_stack, sample_sdd_status):
    """Test that running all bootstrap functions creates expected structure."""
    # Run all bootstrap functions
    create_or_update_constitution(temp_project_root, sample_stack, sample_sdd_status)
    setup_specs_directory(temp_project_root)
    setup_agent_commands(temp_project_root)
    setup_specify_scripts(temp_project_root)
    
    # Verify structure
    expected_dirs = [
        "memory",
        "specs",
        ".specify/templates",
        ".specify/agents",
        ".specify/scripts/bash",
        ".specify/scripts/powershell",
    ]
    
    for dir_path in expected_dirs:
        assert (temp_project_root / dir_path).exists()
    
    expected_files = [
        "memory/constitution.md",
        "specs/README.md",
        ".specify/templates/spec-template.md",
        ".specify/templates/plan-template.md",
        ".specify/templates/tasks-template.md",
        ".specify/agents/README.md",
        ".specify/scripts/bash/README.md",
        ".specify/scripts/powershell/README.md",
    ]
    
    for file_path in expected_files:
        assert (temp_project_root / file_path).exists()


def test_bootstrap_with_python_stack(temp_project_root, sample_sdd_status):
    """Test bootstrap with Python-specific stack."""
    python_stack = DetectedStack(
        id="python",
        name="Python",
        confidence_score=0.92,
        signals=["requirements.txt", "setup.py"],
        test_framework="pytest",
        source_dir="src",
        test_dir="tests",
        commands={},
        ci_present=True,
    )
    
    create_or_update_constitution(temp_project_root, python_stack, sample_sdd_status)
    
    const_file = temp_project_root / "memory" / "constitution.md"
    content = const_file.read_text()
    
    assert "pytest" in content
    assert "Python" in content


def test_all_bootstrap_functions_return_correct_types(temp_project_root, sample_stack, sample_sdd_status):
    """Test that all functions return expected types."""
    # Constitution returns tuple
    result = create_or_update_constitution(temp_project_root, sample_stack, sample_sdd_status)
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)
    
    # Specs returns list of tuples
    test1 = temp_project_root / "test1"
    test1.mkdir(exist_ok=True)
    result = setup_specs_directory(test1)
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
    
    # Agent commands returns list of tuples
    test2 = temp_project_root / "test2"
    test2.mkdir(exist_ok=True)
    result = setup_agent_commands(test2)
    assert isinstance(result, list)
    
    # Scripts returns list of tuples
    test3 = temp_project_root / "test3"
    test3.mkdir(exist_ok=True)
    result = setup_specify_scripts(test3)
    assert isinstance(result, list)


def test_bootstrap_actions_describe_outcomes(temp_project_root):
    """Test that bootstrap function actions have meaningful descriptions."""
    actions = setup_specs_directory(temp_project_root)
    
    action_strings = [action for _, action in actions]
    
    # Should have descriptive action names
    assert any("specs" in a for a in action_strings)
    assert any("template" in a for a in action_strings)


# ============================================================================
# Edge Cases & Safety Tests
# ============================================================================


def test_constitution_with_generic_stack(temp_project_root, sample_sdd_status):
    """Test constitution creation with generic stack."""
    generic_stack = DetectedStack(
        id="generic",
        name="Generic",
        confidence_score=0.0,
        signals=[],
        test_framework="",
        source_dir="",
        test_dir="",
        commands={},
        ci_present=False,
    )
    
    was_created, action = create_or_update_constitution(
        temp_project_root, generic_stack, sample_sdd_status
    )
    
    assert was_created is True
    const_file = temp_project_root / "memory" / "constitution.md"
    content = const_file.read_text()
    assert "Generic" in content or "Stack-Specific" in content


def test_bootstrap_with_deeply_nested_project(sample_stack, sample_sdd_status):
    """Test bootstrap with deeply nested project path."""
    with TemporaryDirectory() as tmpdir:
        deep_path = Path(tmpdir) / "a" / "b" / "c" / "project"
        
        create_or_update_constitution(deep_path, sample_stack, sample_sdd_status)
        
        const_file = deep_path / "memory" / "constitution.md"
        assert const_file.exists()


def test_templates_contain_standard_sdd_sections(temp_project_root):
    """Test that templates contain standard SDD sections."""
    setup_specs_directory(temp_project_root)
    
    spec_template = (temp_project_root / ".specify" / "templates" / "spec-template.md").read_text()
    plan_template = (temp_project_root / ".specify" / "templates" / "plan-template.md").read_text()
    tasks_template = (temp_project_root / ".specify" / "templates" / "tasks-template.md").read_text()
    
    # Spec template should have core sections
    assert "Feature Overview" in spec_template
    assert "User Stories" in spec_template
    assert "Functional Requirements" in spec_template
    
    # Plan template should have architecture sections
    assert "Architecture" in plan_template or "Overview" in plan_template
    
    # Tasks template should have task list
    assert "Task List" in tasks_template or "Phase" in tasks_template


def test_constitution_quality_gates_present(temp_project_root, sample_stack, sample_sdd_status):
    """Test that constitution includes quality gates."""
    create_or_update_constitution(temp_project_root, sample_stack, sample_sdd_status)
    
    const_file = temp_project_root / "memory" / "constitution.md"
    content = const_file.read_text()
    
    assert "Quality Gates" in content
    assert "Test" in content or "test" in content
    assert "Documentation" in content or "documentation" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
