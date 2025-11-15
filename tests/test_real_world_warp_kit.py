#!/usr/bin/env python3
"""
Real-world end-to-end validation test using warp-kit itself as the test bed.

This test validates the complete SDD initialization workflow by applying
it to the warp-kit repository itself, which is a Python/Spec-Kit project.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from specify_cli.project_detection import detect_project_stack, detect_sdd_artifacts
from specify_cli.cli_integration import run_sdd_initialization
from specify_cli.init_hook import should_init_sdd, run_sdd_init_hook


class TestWarpKitRealWorld:
    """Real-world validation using warp-kit as test bed."""
    
    def test_warp_kit_stack_detection(self):
        """Verify warp-kit is correctly detected as Python/Spec-Kit."""
        warp_kit = Path("/home/plasmadev/dev/warp-kit")
        
        assert warp_kit.exists(), "warp-kit directory must exist"
        
        # Detect stack
        stack = detect_project_stack(warp_kit)
        assert stack is not None
        assert stack.id == "python"
        assert stack.name == "Python"
        assert stack.confidence_score > 0.5
    
    def test_warp_kit_sdd_status(self):
        """Verify warp-kit SDD artifact detection."""
        warp_kit = Path("/home/plasmadev/dev/warp-kit")
        
        # Detect SDD artifacts
        status = detect_sdd_artifacts(warp_kit)
        
        # Warp-kit should have WARP and specs
        assert status.has_warp_root is True or status.has_specs is True
        assert status.has_constitution is True
    
    def test_warp_kit_should_skip_bootstrap(self):
        """Verify that warp-kit properly detects it's already SDD-enabled."""
        warp_kit = Path("/home/plasmadev/dev/warp-kit")
        
        should_run, reason = should_init_sdd(warp_kit, warp_spec_flag=False)
        
        # Already SDD-enabled, should skip
        assert should_run is False
        assert "SDD-enabled" in reason
    
    def test_warp_kit_force_bootstrap_with_flag(self):
        """Verify --warp-spec flag forces bootstrap even for SDD-enabled projects."""
        warp_kit = Path("/home/plasmadev/dev/warp-kit")
        
        should_run, reason = should_init_sdd(warp_kit, warp_spec_flag=True)
        
        # Explicit flag should enable
        assert should_run is True
        assert "explicitly requested" in reason
    
    def test_warp_kit_bootstrap_idempotent(self):
        """Test that bootstrapping warp-kit is safe (idempotent)."""
        warp_kit = Path("/home/plasmadev/dev/warp-kit")
        
        # Run initialization
        result = run_sdd_initialization(warp_kit)
        
        # Since it's already SDD-enabled, result may be None or show preservation
        if result:
            assert result.constitution_preserved is True or result.constitution_created is True
    
    def test_warp_kit_constitution_exists(self):
        """Verify warp-kit has a constitution file."""
        warp_kit = Path("/home/plasmadev/dev/warp-kit")
        const_path = warp_kit / "memory" / "constitution.md"
        
        assert const_path.exists(), "Constitution file should exist"
        
        content = const_path.read_text()
        # Warp-kit uses a template, so check for core principles
        assert "Core Principles" in content or "PRINCIPLE" in content


class TestRealWorldProjectBootstrap:
    """Test bootstrapping a real-world project scenario."""
    
    def test_bootstrap_existing_python_project(self):
        """Test bootstrapping an existing Python project."""
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Create a real Python project structure
            (project / "src").mkdir()
            (project / "tests").mkdir()
            (project / "pyproject.toml").write_text('[project]\nname = "test-project"\n')
            (project / "README.md").write_text("# Test Project\n")
            
            # Run SDD initialization
            result = run_sdd_initialization(project)
            
            # Should create SDD artifacts
            assert result.stack_detected is True
            assert result.stack_id == "python"
            assert result.constitution_created is True
            assert result.specs_setup is True
            
            # Verify artifacts exist
            assert (project / "memory" / "constitution.md").exists()
            assert (project / "specs" / "README.md").exists()
            assert (project / ".specify" / "templates").exists()
    
    def test_idempotent_bootstrap_twice(self):
        """Test that bootstrapping twice is truly idempotent."""
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Create project
            (project / "src").mkdir()
            (project / "pyproject.toml").touch()
            
            # First bootstrap
            result1 = run_sdd_initialization(project)
            assert result1.constitution_created is True
            
            const_content_1 = (project / "memory" / "constitution.md").read_text()
            
            # Second bootstrap
            result2 = run_sdd_initialization(project)
            assert result2.constitution_preserved is True
            
            const_content_2 = (project / "memory" / "constitution.md").read_text()
            
            # Content should be identical
            assert const_content_1 == const_content_2
            
            # No duplication
            assert const_content_2.count("## Core Principles") == 1
    
    def test_preserve_user_additions(self):
        """Test that user additions to constitution are preserved."""
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Create project
            (project / "src").mkdir()
            (project / "pyproject.toml").touch()
            
            # First bootstrap
            run_sdd_initialization(project)
            
            # User adds custom section
            const_path = project / "memory" / "constitution.md"
            original = const_path.read_text()
            custom = original + "\n## Custom Company Rules\n\nOur custom rules go here.\n"
            const_path.write_text(custom)
            
            # Second bootstrap
            run_sdd_initialization(project)
            
            # Custom section should still be there
            final = const_path.read_text()
            assert "Custom Company Rules" in final
            assert "Our custom rules go here" in final


class TestCompleteEndToEnd:
    """Complete end-to-end workflow validation."""
    
    def test_full_workflow_new_python_project(self):
        """Test complete workflow from detection through bootstrap."""
        with TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)
            
            # Step 1: Create a new Python project
            (project / "src").mkdir()
            (project / "src" / "main.py").write_text('print("Hello")')
            (project / "tests").mkdir()
            (project / "tests" / "test_main.py").write_text('def test_it(): pass')
            (project / "pyproject.toml").write_text('[project]\nname = "myproject"\n')
            (project / "README.md").write_text("# My Project\n")
            
            # Step 2: Detect stack
            stack = detect_project_stack(project)
            assert stack.id == "python"
            
            # Step 3: Check SDD status
            status = detect_sdd_artifacts(project)
            assert status.is_sdd_enabled is False
            
            # Step 4: Bootstrap SDD
            result = run_sdd_initialization(project)
            assert result.stack_detected is True
            assert result.constitution_created is True
            assert result.specs_setup is True
            assert result.agent_commands_setup is True
            assert result.scripts_setup is True
            
            # Step 5: Verify complete structure
            assert (project / "memory" / "constitution.md").exists()
            assert (project / "specs" / "README.md").exists()
            assert (project / ".specify" / "templates" / "spec-template.md").exists()
            assert (project / ".specify" / "templates" / "plan-template.md").exists()
            assert (project / ".specify" / "templates" / "tasks-template.md").exists()
            assert (project / ".specify" / "agents").exists()
            assert (project / ".specify" / "scripts" / "bash").exists()
            assert (project / ".specify" / "scripts" / "powershell").exists()
            
            # Step 6: Verify content quality
            const = (project / "memory" / "constitution.md").read_text()
            assert "pytest" in const or "Python" in const
            assert "Core Principles" in const
            assert "Development Workflow" in const
            
            specs_readme = (project / "specs" / "README.md").read_text()
            assert "SDD" in specs_readme or "Specifications" in specs_readme
            assert "specify" in specs_readme.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
