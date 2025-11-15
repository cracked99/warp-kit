#!/usr/bin/env python3
"""
End-to-End Validation Test Suite.

Tests the complete pipeline from project detection through SDD bootstrap,
validating across multiple project types and scenarios.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.project_detection import detect_project_stack, detect_sdd_artifacts
from specify_cli.warp_generation import generate_root_warp, generate_subdir_warps
from specify_cli.sdd_bootstrap import (
    create_or_update_constitution,
    setup_specs_directory,
)
from specify_cli.cli_integration import run_sdd_initialization, get_next_steps


# ============================================================================
# Project Fixtures
# ============================================================================


@pytest.fixture
def python_project():
    """Python project with src/ and tests/ directories."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pyproject.toml").write_text("[project]\nname = 'test-project'\n")
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "README.md").write_text("# Test Project\n\nA test Python project.\n")
        yield root


@pytest.fixture
def node_project():
    """Node.js project with src/, tests/, and config files."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "package.json").write_text('{"name": "test-project", "version": "1.0.0"}\n')
        (root / "tsconfig.json").write_text("{}\n")
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "README.md").write_text("# Test Project\n\nA test Node.js project.\n")
        yield root


@pytest.fixture
def go_project():
    """Go project with cmd/ and pkg/ directories."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "go.mod").write_text("module test-project\n")
        (root / "cmd").mkdir()
        (root / "pkg").mkdir()
        (root / "README.md").write_text("# Test Project\n\nA test Go project.\n")
        yield root


@pytest.fixture
def java_project():
    """Java project with Maven structure."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "pom.xml").write_text("<project></project>\n")
        (root / "src").mkdir()
        (root / "src" / "main").mkdir()
        (root / "src" / "test").mkdir()
        (root / "README.md").write_text("# Test Project\n\nA test Java project.\n")
        yield root


@pytest.fixture
def rust_project():
    """Rust project with Cargo structure."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "Cargo.toml").write_text("[package]\nname = 'test-project'\n")
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "README.md").write_text("# Test Project\n\nA test Rust project.\n")
        yield root


@pytest.fixture
def generic_project():
    """Generic project with no clear tech stack signals."""
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "src").mkdir()
        (root / "tests").mkdir()
        (root / "README.md").write_text("# Generic Project\n")
        yield root


# ============================================================================
# Detection & Artifact Tests
# ============================================================================


class TestProjectDetection:
    """Test project detection across different stack types."""
    
    def test_detect_python_stack(self, python_project):
        """Verify Python stack detection."""
        stack = detect_project_stack(python_project)
        assert stack is not None
        assert stack.id == "python"
        assert "pytest" in stack.test_framework or stack.test_framework in ("pytest", "unittest")
        assert stack.confidence_score > 0.5
    
    def test_detect_node_stack(self, node_project):
        """Verify Node.js stack detection."""
        stack = detect_project_stack(node_project)
        assert stack is not None
        assert stack.id == "node"
        assert stack.confidence_score > 0.5
    
    def test_detect_go_stack(self, go_project):
        """Verify Go stack detection."""
        stack = detect_project_stack(go_project)
        assert stack is not None
        assert stack.id == "go"
        assert stack.test_framework == "testing"
    
    def test_detect_java_stack(self, java_project):
        """Verify Java stack detection."""
        stack = detect_project_stack(java_project)
        assert stack is not None
        assert stack.id == "java"
        assert stack.confidence_score > 0.5
    
    def test_detect_rust_stack(self, rust_project):
        """Verify Rust stack detection."""
        stack = detect_project_stack(rust_project)
        assert stack is not None
        assert stack.id == "rust"
        assert "cargo" in stack.test_framework.lower()
    
    def test_detect_generic_fallback(self, generic_project):
        """Verify fallback to generic for unknown stacks."""
        stack = detect_project_stack(generic_project)
        assert stack is not None
        assert stack.id == "generic"  # Falls back to generic


class TestSddArtifactDetection:
    """Test SDD artifact detection."""
    
    def test_detect_sdd_empty_project(self, python_project):
        """Verify SDD detection for non-SDD project."""
        status = detect_sdd_artifacts(python_project)
        assert status.has_constitution is False
        assert status.has_specs is False
        assert status.is_sdd_enabled is False
    
    def test_detect_sdd_partial(self, python_project):
        """Verify SDD detection for partially SDD-enabled project."""
        # Create only constitution
        memory_dir = python_project / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").touch()
        
        status = detect_sdd_artifacts(python_project)
        assert status.has_constitution is True
        assert status.has_specs is False
        assert status.is_sdd_enabled is False  # Needs both
    
    def test_detect_sdd_full(self, python_project):
        """Verify SDD detection for fully SDD-enabled project."""
        # Create constitution and specs
        (python_project / "memory").mkdir()
        (python_project / "memory" / "constitution.md").touch()
        (python_project / "specs").mkdir()
        (python_project / "specs" / "README.md").touch()
        
        status = detect_sdd_artifacts(python_project)
        assert status.has_constitution is True
        assert status.has_specs is True
        assert status.is_sdd_enabled is True


# ============================================================================
# Complete Pipeline Tests
# ============================================================================


class TestCompleteInitializationPipeline:
    """Test the complete end-to-end initialization pipeline."""
    
    def test_python_complete_pipeline(self, python_project):
        """Test complete pipeline for Python project."""
        result = run_sdd_initialization(python_project)
        
        # Verify detection
        assert result.stack_detected is True
        assert result.stack_id == "python"
        
        # Verify bootstrap
        assert result.constitution_created is True
        assert result.specs_setup is True
        assert result.agent_commands_setup is True
        assert result.scripts_setup is True
        
        # Verify artifacts exist
        assert (python_project / "memory" / "constitution.md").exists()
        assert (python_project / "specs" / "README.md").exists()
        assert (python_project / ".specify" / "templates").exists()
        
        # Verify constitution mentions Python
        const_content = (python_project / "memory" / "constitution.md").read_text()
        assert "pytest" in const_content or "Python" in const_content
    
    def test_node_complete_pipeline(self, node_project):
        """Test complete pipeline for Node.js project."""
        result = run_sdd_initialization(node_project)
        
        assert result.stack_detected is True
        assert result.stack_id == "node"
        assert result.constitution_created is True
        
        # Verify Node-specific content
        const_content = (node_project / "memory" / "constitution.md").read_text()
        assert "Node" in const_content or "TypeScript" in const_content or "Jest" in const_content
    
    def test_go_complete_pipeline(self, go_project):
        """Test complete pipeline for Go project."""
        result = run_sdd_initialization(go_project)
        
        assert result.stack_detected is True
        assert result.stack_id == "go"
        assert result.constitution_created is True
        
        # Verify Go-specific content
        const_content = (go_project / "memory" / "constitution.md").read_text()
        assert "Go" in const_content or "gofmt" in const_content
    
    def test_java_complete_pipeline(self, java_project):
        """Test complete pipeline for Java project."""
        result = run_sdd_initialization(java_project)
        
        assert result.stack_detected is True
        assert result.stack_id == "java"
        assert result.constitution_created is True
    
    def test_rust_complete_pipeline(self, rust_project):
        """Test complete pipeline for Rust project."""
        result = run_sdd_initialization(rust_project)
        
        assert result.stack_detected is True
        assert result.stack_id == "rust"
        assert result.constitution_created is True
        
        # Verify Rust-specific content
        const_content = (rust_project / "memory" / "constitution.md").read_text()
        assert "Rust" in const_content or "cargo" in const_content
    
    def test_generic_complete_pipeline(self, generic_project):
        """Test complete pipeline for generic project."""
        result = run_sdd_initialization(generic_project)
        
        assert result.stack_detected is True
        assert result.stack_id == "generic"
        assert result.constitution_created is True
        assert result.specs_setup is True


# ============================================================================
# Idempotency & Merge Tests
# ============================================================================


class TestIdempotency:
    """Test that operations are safe to run multiple times."""
    
    def test_initialization_idempotent_python(self, python_project):
        """Verify initialization is idempotent for Python."""
        # First run
        result1 = run_sdd_initialization(python_project)
        assert result1.constitution_created is True
        
        # Second run
        result2 = run_sdd_initialization(python_project)
        assert result2.constitution_preserved is True
        
        # Verify no duplication
        const = (python_project / "memory" / "constitution.md").read_text()
        assert const.count("## Core Principles") == 1
    
    def test_initialization_idempotent_node(self, node_project):
        """Verify initialization is idempotent for Node.js."""
        result1 = run_sdd_initialization(node_project)
        result2 = run_sdd_initialization(node_project)
        
        assert result1.constitution_created is True
        assert result2.constitution_preserved is True
    
    def test_specs_setup_idempotent(self, python_project):
        """Verify specs setup is idempotent."""
        setup_specs_directory(python_project)
        first_mtime = (python_project / "specs" / "README.md").stat().st_mtime
        
        setup_specs_directory(python_project)
        second_mtime = (python_project / "specs" / "README.md").stat().st_mtime
        
        # File should not be rewritten if already exists
        assert first_mtime == second_mtime
    
    def test_constitution_preserved_on_rerun(self, python_project):
        """Verify existing constitution is never overwritten."""
        # Initial run
        run_sdd_initialization(python_project)
        original = (python_project / "memory" / "constitution.md").read_text()
        
        # Add custom section
        (python_project / "memory" / "constitution.md").write_text(
            original + "\n## Custom Section\n\nUser-added content\n"
        )
        
        # Re-run initialization
        run_sdd_initialization(python_project)
        final = (python_project / "memory" / "constitution.md").read_text()
        
        # Custom section should still be there
        assert "Custom Section" in final
        assert "User-added content" in final


# ============================================================================
# Stack-Specific Tests
# ============================================================================


class TestStackSpecificBehavior:
    """Test stack-specific bootstrap behavior."""
    
    def test_python_commands_present(self, python_project):
        """Verify Python-specific commands in constitution."""
        run_sdd_initialization(python_project)
        const = (python_project / "memory" / "constitution.md").read_text()
        
        # Should mention pytest or Python testing
        assert any(term in const for term in ["pytest", "Python", "test"])
    
    def test_node_commands_present(self, node_project):
        """Verify Node-specific commands in constitution."""
        run_sdd_initialization(node_project)
        const = (node_project / "memory" / "constitution.md").read_text()
        
        # Should mention Node/TypeScript/Jest
        assert any(term in const for term in ["Node", "TypeScript", "Jest", "npm"])
    
    def test_go_commands_present(self, go_project):
        """Verify Go-specific commands in constitution."""
        run_sdd_initialization(go_project)
        const = (go_project / "memory" / "constitution.md").read_text()
        
        # Should mention Go testing
        assert any(term in const for term in ["Go", "gofmt", "testing"])
    
    def test_java_commands_present(self, java_project):
        """Verify Java-specific commands in constitution."""
        run_sdd_initialization(java_project)
        const = (java_project / "memory" / "constitution.md").read_text()
        
        # Should mention Java/JUnit
        assert any(term in const for term in ["Java", "JUnit", "Maven", "Gradle"])
    
    def test_rust_commands_present(self, rust_project):
        """Verify Rust-specific commands in constitution."""
        run_sdd_initialization(rust_project)
        const = (rust_project / "memory" / "constitution.md").read_text()
        
        # Should mention Rust/cargo
        assert any(term in const for term in ["Rust", "cargo", "clippy"])


# ============================================================================
# Artifact Quality Tests
# ============================================================================


class TestArtifactQuality:
    """Test quality of generated artifacts."""
    
    def test_constitution_has_required_sections(self, python_project):
        """Verify constitution contains all required sections."""
        run_sdd_initialization(python_project)
        const = (python_project / "memory" / "constitution.md").read_text()
        
        required_sections = [
            "Core Principles",
            "Spec-Driven Development",
            "Test",
            "Quality Gates",
            "Development Workflow",
        ]
        
        for section in required_sections:
            assert section in const, f"Missing section: {section}"
    
    def test_specs_readme_has_workflow_info(self, python_project):
        """Verify specs README explains SDD workflow."""
        run_sdd_initialization(python_project)
        readme = (python_project / "specs" / "README.md").read_text()
        
        # Should mention workflow and /speckit commands
        assert "Specifications" in readme
        assert any(cmd in readme for cmd in ["/speckit", "specify", "clarify", "plan"])
    
    def test_templates_contain_placeholders(self, python_project):
        """Verify templates contain proper placeholders."""
        run_sdd_initialization(python_project)
        
        templates = [
            "spec-template.md",
            "plan-template.md",
            "tasks-template.md",
        ]
        
        for template_name in templates:
            template_path = python_project / ".specify" / "templates" / template_name
            content = template_path.read_text()
            
            # Should have placeholders
            assert "{{" in content and "}}" in content
            
            # Should have sections
            assert "#" in content or "##" in content
    
    def test_no_forbidden_boilerplate_in_constitution(self, python_project):
        """Verify constitution doesn't contain forbidden generic advice."""
        run_sdd_initialization(python_project)
        const = (python_project / "memory" / "constitution.md").read_text()
        
        forbidden_phrases = [
            "write unit tests",
            "avoid secrets",
            "always use",
            "never use",
        ]
        
        # Should not contain these generic phrases (should be specific)
        for phrase in forbidden_phrases:
            assert phrase.lower() not in const.lower()


# ============================================================================
# Next Steps & Guidance Tests
# ============================================================================


class TestUserGuidance:
    """Test guidance provided to users after initialization."""
    
    def test_next_steps_generated(self, python_project):
        """Verify next steps are generated."""
        result = run_sdd_initialization(python_project)
        steps = get_next_steps(result)
        
        assert len(steps) > 0
        assert isinstance(steps, list)
    
    def test_next_steps_mention_speckit_commands(self, python_project):
        """Verify next steps reference /speckit commands."""
        result = run_sdd_initialization(python_project)
        steps = get_next_steps(result)
        steps_text = "\n".join(steps).lower()
        
        # Should mention key SDD commands
        assert any(cmd in steps_text for cmd in ["specify", "clarify", "plan", "tasks"])
    
    def test_next_steps_mention_artifacts(self, python_project):
        """Verify next steps reference created artifacts."""
        result = run_sdd_initialization(python_project)
        steps = get_next_steps(result)
        steps_text = "\n".join(steps).lower()
        
        # Should mention WARP and constitution
        assert any(artifact in steps_text for artifact in ["warp", "constitution", "spec"])


# ============================================================================
# Multi-Project Scenarios
# ============================================================================


class TestMultiProjectScenarios:
    """Test initialization across multiple projects."""
    
    def test_multiple_stacks_independent(self, python_project, node_project):
        """Verify initializing different stacks doesn't interfere."""
        result_python = run_sdd_initialization(python_project)
        result_node = run_sdd_initialization(node_project)
        
        assert result_python.stack_id == "python"
        assert result_node.stack_id == "node"
        
        # Each should have proper stack-specific constitution
        python_const = (python_project / "memory" / "constitution.md").read_text()
        node_const = (node_project / "memory" / "constitution.md").read_text()
        
        # Content should differ by stack
        assert "pytest" in python_const or "Python" in python_const
        assert "Node" in node_const or "TypeScript" in node_const or "Jest" in node_const
    
    def test_sequential_initialization(self):
        """Test initializing multiple projects sequentially."""
        projects = []
        stacks = ["python", "node", "go"]
        
        try:
            for i, stack_type in enumerate(stacks):
                tmpdir = TemporaryDirectory()
                root = Path(tmpdir.name)
                
                # Create minimal project files
                if stack_type == "python":
                    (root / "pyproject.toml").touch()
                elif stack_type == "node":
                    (root / "package.json").touch()
                elif stack_type == "go":
                    (root / "go.mod").touch()
                
                (root / "src").mkdir()
                
                # Initialize
                result = run_sdd_initialization(root)
                assert result.stack_detected is True
                projects.append((tmpdir, result))
        
        finally:
            for tmpdir, _ in projects:
                tmpdir.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
