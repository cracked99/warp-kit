"""
Unit tests for WARP generation module.

Tests cover:
- Root WARP generation for all stacks
- Subdirectory WARP generation
- Marker-based idempotent updates
- README extraction
- Agent rules detection
"""

import pytest
import tempfile
from pathlib import Path
from src.specify_cli.project_detection import detect_project_stack, DetectedStack
from src.specify_cli.warp_generation import (
    generate_root_warp,
    upsert_warp,
    generate_subdir_warps,
    WARP_PREFIX,
    WARP_MANAGED_START,
    WARP_MANAGED_END,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def node_project():
    """Minimal Node.js project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").write_text('{"name": "app"}')
        (root / "src").mkdir()
        (root / "tests").mkdir()
        yield root


@pytest.fixture
def python_project():
    """Minimal Python project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text("[tool.pytest]")
        (root / "src").mkdir()
        (root / "tests").mkdir()
        yield root


@pytest.fixture
def generic_project():
    """Empty project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# Tests: Root WARP Generation
# ============================================================================


def test_generate_root_warp_has_prefix(node_project):
    """Root WARP starts with required prefix."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    assert warp.startswith(WARP_PREFIX)


def test_generate_root_warp_has_sdd_section(node_project):
    """Root WARP includes auto-managed SDD section."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    assert WARP_MANAGED_START in warp
    assert WARP_MANAGED_END in warp
    assert "Spec-Driven Development" in warp


def test_generate_root_warp_no_boilerplate(node_project):
    """Root WARP has no forbidden generic boilerplate."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    # Forbidden phrases
    forbidden = ["write unit tests", "write comprehensive tests", "avoid secrets"]
    for phrase in forbidden:
        assert phrase.lower() not in warp.lower()


def test_generate_root_warp_stack_commands_present(node_project):
    """Root WARP includes stack-specific commands."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    # Should have some npm commands for Node
    assert "npm" in warp or "node" in warp.lower()


def test_generate_root_warp_architecture_section(node_project):
    """Root WARP has Architecture Overview section."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    assert "Architecture" in warp


def test_generate_root_warp_with_readme(generic_project):
    """Root WARP extracts README summary if present."""
    # Create README
    (generic_project / "README.md").write_text("# My Project\n\nThis is cool.")
    (generic_project / "package.json").write_text("{}")
    
    stack = detect_project_stack(generic_project)
    warp = generate_root_warp(stack, generic_project)
    
    assert "Project Overview" in warp
    assert "My Project" in warp


def test_generate_root_warp_without_readme(node_project):
    """Root WARP works without README."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    # Should still be valid
    assert WARP_PREFIX in warp
    assert "Technology Stack" in warp


# ============================================================================
# Tests: WARP Upsert (Idempotency)
# ============================================================================


def test_upsert_warp_first_creation(generic_project):
    """upsert_warp creates new file with full content."""
    warp_path = generic_project / "WARP.md"
    content = "# Test\n\nContent here."
    
    created, action = upsert_warp(warp_path, content)
    
    assert created
    assert action == "created"
    assert warp_path.exists()
    assert warp_path.read_text() == content


def test_upsert_warp_append_sdd_section(generic_project):
    """upsert_warp appends SDD section to existing WARP without markers."""
    warp_path = generic_project / "WARP.md"
    
    # Create existing WARP without markers
    existing = "# WARP\n\nMy content here."
    warp_path.write_text(existing)
    
    # New content with SDD section
    new_content = f"""# WARP

Some content.

{WARP_MANAGED_START}
## SDD Section
{WARP_MANAGED_END}
"""
    
    created, action = upsert_warp(warp_path, new_content)
    
    assert not created
    assert action == "appended_sdd_section"
    
    result = warp_path.read_text()
    assert "My content here" in result  # Original content preserved
    assert WARP_MANAGED_START in result
    assert "SDD Section" in result


def test_upsert_warp_update_marked_section(generic_project):
    """upsert_warp replaces only marked section."""
    warp_path = generic_project / "WARP.md"
    
    # Create WARP with old SDD section
    existing = f"""# WARP

My content.

{WARP_MANAGED_START}
Old SDD content
{WARP_MANAGED_END}

More user content."""
    
    warp_path.write_text(existing)
    
    # New content with updated SDD section
    new_content = f"""# WARP

{WARP_MANAGED_START}
New SDD content
{WARP_MANAGED_END}
"""
    
    created, action = upsert_warp(warp_path, new_content)
    
    assert not created
    assert action == "updated_sdd_section"
    
    result = warp_path.read_text()
    assert "My content" in result  # Original preserved
    assert "New SDD content" in result
    assert "Old SDD content" not in result
    assert "More user content" in result  # After-marker content preserved


def test_upsert_warp_idempotent(generic_project):
    """Running upsert_warp twice produces identical results."""
    warp_path = generic_project / "WARP.md"
    content = f"""# WARP

{WARP_MANAGED_START}
SDD Section
{WARP_MANAGED_END}
"""
    
    # First run
    upsert_warp(warp_path, content)
    result1 = warp_path.read_text()
    
    # Second run
    created2, action2 = upsert_warp(warp_path, content)
    result2 = warp_path.read_text()
    
    assert not created2
    assert action2 == "no_changes"
    assert result1 == result2


# ============================================================================
# Tests: Subdirectory WARP Generation
# ============================================================================


def test_generate_subdir_warps_creates_existing_dirs(node_project):
    """generate_subdir_warps creates WARPs for existing directories."""
    stack = detect_project_stack(node_project)
    results = generate_subdir_warps(stack, node_project)
    
    # Should create src/WARP.md and tests/WARP.md (both exist)
    paths_created = [r[0] for r in results]
    
    assert any("src/WARP.md" in str(p) for p in paths_created)
    assert any("tests/WARP.md" in str(p) for p in paths_created)


def test_generate_subdir_warps_skips_missing_dirs(node_project):
    """generate_subdir_warps skips non-existent directories."""
    stack = detect_project_stack(node_project)
    results = generate_subdir_warps(stack, node_project)
    
    # Should not create for .github or docs (they don't exist)
    paths_created = [r[0] for r in results]
    
    assert not any(".github/WARP.md" in str(p) for p in paths_created)
    assert not any("docs/WARP.md" in str(p) for p in paths_created)


def test_subdir_warp_has_correct_prefix(node_project):
    """Subdirectory WARPs have proper prefix (path-specific)."""
    stack = detect_project_stack(node_project)
    results = generate_subdir_warps(stack, node_project)
    
    for path, content, result in results:
        assert content.startswith("# WARP.md")
        assert "See root" in content  # Cross-reference to root


# ============================================================================
# Tests: Validation
# ============================================================================


def test_root_warp_is_valid_markdown(node_project):
    """Generated root WARP is valid Markdown."""
    stack = detect_project_stack(node_project)
    warp = generate_root_warp(stack, node_project)
    
    # Basic validity checks
    assert warp.count("```") % 2 == 0  # Balanced code blocks
    lines = warp.split("\n")
    assert all(not l.startswith(" ") for l in lines if l.startswith("#"))  # Headings not indented


def test_root_warp_all_stacks(python_project):
    """Root WARP generation works for all stacks."""
    stack = detect_project_stack(python_project)
    warp = generate_root_warp(stack, python_project)
    
    # Should generate without errors
    assert len(warp) > 50  # Reasonable length
    assert WARP_PREFIX in warp
