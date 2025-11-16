#!/usr/bin/env python3
"""Verify that warp-space is properly created during --here initialization."""

import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from specify_cli.project_detection import DetectedStack, SDDStatus
from specify_cli.sdd_bootstrap import (
    create_warpspace,
    create_or_update_constitution,
    setup_specs_directory,
    setup_agent_commands,
    setup_warp_space_scripts,
    setup_warp_space_config,
)

def test_warpspace_creation():
    """Test warp-space creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create sample stack
        stack = DetectedStack(
            id="python",
            name="Python",
            confidence_score=0.90,
            signals=["pyproject.toml"],
            test_framework="pytest",
            source_dir="src",
            test_dir="tests",
            commands={},
            ci_present=False,
        )
        
        sdd_status = SDDStatus(
            has_constitution=False,
            has_specs=False,
            has_specify_dir=False,
            has_warp_root=False,
            has_warp_subdirs={},
        )
        
        # Run bootstrap functions
        print("Testing warp-space creation...")
        create_warpspace(project_root)
        create_or_update_constitution(project_root, stack, sdd_status)
        setup_specs_directory(project_root)
        setup_agent_commands(project_root)
        setup_warp_space_scripts(project_root)
        setup_warp_space_config(project_root)
        
        # Verify structure
        expected_paths = [
            ".warp-space/Warp-space.md",
            ".warp-space/memory/constitution.md",
            ".warp-space/templates/spec-template.md",
            ".warp-space/templates/plan-template.md",
            ".warp-space/templates/tasks-template.md",
            ".warp-space/commands",
            ".warp-space/scripts/bash/README.md",
            ".warp-space/scripts/powershell/README.md",
            "specs/README.md",
        ]
        
        print("\nVerifying directory structure:")
        all_exist = True
        for path_str in expected_paths:
            path = project_root / path_str
            exists = path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {path_str}")
            if not exists:
                all_exist = False
        
        if all_exist:
            print("\n✓ All warp-space files and directories created successfully!")
            return True
        else:
            print("\n✗ Some files or directories are missing!")
            return False

if __name__ == "__main__":
    success = test_warpspace_creation()
    sys.exit(0 if success else 1)
