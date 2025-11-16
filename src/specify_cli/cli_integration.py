#!/usr/bin/env python3
"""
CLI Integration Module - Orchestrate project detection, WARP generation, and SDD bootstrap.

This module provides the orchestration layer that ties together:
1. Project stack detection
2. WARP.md generation
3. SDD artifact bootstrapping
"""

from pathlib import Path
from typing import Optional, Tuple

from .project_detection import detect_project_stack, detect_sdd_artifacts
from .warp_generation import generate_root_warp, generate_subdir_warps, upsert_warp
from .sdd_bootstrap import (
    create_warpspace,
    create_or_update_constitution,
    setup_specs_directory,
    setup_agent_commands,
    setup_warp_space_scripts,
    setup_warp_space_config,
    setup_warp_space_agents,
    setup_warp_space_core,
)


class InitializationResult:
    """Result of project initialization with SDD bootstrap."""
    
    def __init__(self):
        self.stack_detected: bool = False
        self.stack_id: Optional[str] = None
        self.stack_name: Optional[str] = None
        self.warp_created: bool = False
        self.warp_updated: bool = False
        self.constitution_created: bool = False
        self.constitution_preserved: bool = False
        self.specs_setup: bool = False
        self.agent_commands_setup: bool = False
        self.scripts_setup: bool = False
        self.messages: list = []
    
    def add_message(self, msg: str) -> None:
        """Add a status message."""
        self.messages.append(msg)
    
    def summary(self) -> str:
        """Generate a summary of what was done."""
        lines = [
            f"Stack detected: {self.stack_name or 'None'} ({self.stack_id or '?'})",
        ]
        
        if self.warp_created:
            lines.append("✓ Root WARP.md created")
        elif self.warp_updated:
            lines.append("✓ Root WARP.md updated")
        
        if self.constitution_created:
            lines.append("✓ Constitution created (memory/constitution.md)")
        elif self.constitution_preserved:
            lines.append("✓ Existing constitution preserved")
        
        if self.specs_setup:
            lines.append("✓ Specs directory structure created")
        if self.agent_commands_setup:
            lines.append("✓ Agent command directories set up")
        if self.scripts_setup:
            lines.append("✓ Helper scripts directories created")
        
        return "\n".join(lines)


def run_sdd_initialization(
    project_root: Path,
    auto_enable: bool = True,
    skip_warp: bool = False,
) -> InitializationResult:
    """
    Run complete SDD initialization pipeline for a project.
    
    This is the main orchestration function that:
    1. Detects the project tech stack
    2. Generates or updates WARP.md files
    3. Bootstraps SDD artifacts (constitution, specs, templates, scripts)
    
    Args:
        project_root: Root directory of the project
        auto_enable: If True, enable SDD pipeline even for non-SDD projects
        skip_warp: If True, skip WARP generation (e.g., if doing bootstrap-only)
    
    Returns:
        InitializationResult with status and messages
    """
    
    result = InitializationResult()
    
    # Phase 1: Detect project stack
    detected_stack = detect_project_stack(project_root)
    result.stack_detected = detected_stack is not None
    result.stack_id = detected_stack.id if detected_stack else None
    result.stack_name = detected_stack.name if detected_stack else None
    result.add_message(f"Detected stack: {detected_stack.name} (confidence: {detected_stack.confidence_score:.1%})")
    
    # Phase 2: Detect existing SDD artifacts
    sdd_status = detect_sdd_artifacts(project_root)
    is_sdd_enabled = sdd_status.is_sdd_enabled
    
    if is_sdd_enabled:
        result.add_message("Project is already SDD-enabled")
    else:
        result.add_message("Project is not SDD-enabled - bootstrapping")
    
    # Phase 3: Generate WARP.md files (unless skipped)
    if not skip_warp and detected_stack:
        try:
            # Generate root WARP
            warp_content = generate_root_warp(detected_stack, project_root)
            warp_path = project_root / "WARP.md"
            was_created, action = upsert_warp(warp_path, warp_content)
            if was_created:
                result.warp_created = True
            else:
                result.warp_updated = True
            result.add_message(f"Generated root WARP.md")
            
            # Generate subdirectory WARPs
            subdirs_created = generate_subdir_warps(detected_stack, project_root)
            if subdirs_created:
                result.add_message(f"Generated {len(subdirs_created)} subdirectory WARP files")
        
        except Exception as e:
            result.add_message(f"Warning: WARP generation failed: {e}")
    
    # Phase 4: Bootstrap SDD artifacts
    if detected_stack:
        try:
            # Warp-space.md (single source of truth)
            create_warpspace(project_root)
            result.add_message("Created .warp-space/Warp-space.md (single source of truth)")
            
            # Constitution
            was_created, action = create_or_update_constitution(
                project_root, detected_stack, sdd_status
            )
            if was_created:
                result.constitution_created = True
                result.add_message("Created constitution (.warp-space/memory/constitution.md)")
            else:
                result.constitution_preserved = True
                result.add_message("Preserved existing constitution")
            
            # Specs directory
            specs_actions = setup_specs_directory(project_root)
            if any(created for created, _ in specs_actions):
                result.specs_setup = True
                result.add_message("Set up .warp-space/specs/ directory with templates")
            
            # Agent commands
            agent_actions = setup_agent_commands(project_root)
            if any(created for created, _ in agent_actions):
                result.agent_commands_setup = True
                result.add_message("Set up agent command directories")
            
            # Scripts
            script_actions = setup_warp_space_scripts(project_root)
            if any(created for created, _ in script_actions):
                result.scripts_setup = True
                result.add_message("Set up helper scripts directories")
            
            # Configuration files
            config_actions = setup_warp_space_config(project_root)
            if any(created for created, _ in config_actions):
                result.add_message("Created configuration files")
            
            # Agents directory
            agents_actions = setup_warp_space_agents(project_root)
            if any(created for created, _ in agents_actions):
                result.add_message("Set up agent configuration directory")
            
            # Core architecture directory
            core_actions = setup_warp_space_core(project_root)
            if any(created for created, _ in core_actions):
                result.add_message("Set up core architecture directory")
        
        except Exception as e:
            result.add_message(f"Warning: SDD bootstrap failed: {e}")
    
    return result


def should_run_sdd_pipeline(project_root: Path) -> Tuple[bool, str]:
    """
    Determine whether to run the SDD initialization pipeline.
    
    Returns:
        Tuple of (should_run: bool, reason: str)
    """
    
    sdd_status = detect_sdd_artifacts(project_root)
    
    # Always run if not already SDD-enabled
    if not sdd_status.is_sdd_enabled:
        return (True, "Project not SDD-enabled - running initialization")
    
    # For already SDD-enabled projects, check if updates are needed
    detected_stack = detect_project_stack(project_root)
    if detected_stack:
        return (True, "Project SDD-enabled but stack detected - updating artifacts")
    
    return (False, "Project already SDD-enabled with no stack changes detected")


def get_next_steps(result: InitializationResult) -> list:
    """
    Generate a list of recommended next steps after initialization.
    
    Args:
        result: InitializationResult from initialization
    
    Returns:
        List of suggested next steps as strings
    """
    
    steps = [
        "✓ Review .warp-space/Warp-space.md (single source of truth)",
        "✓ Review .warp-space/memory/constitution.md for project principles",
    ]
    
    if result.specs_setup:
        steps.append("✓ Check .warp-space/specs/README.md for SDD workflow guidance")
    
    steps.extend([
        "",
        "Next steps:",
        "1. Run '/speckit.specify' to create your first feature specification",
        "2. Use '/speckit.clarify' to resolve ambiguities",
        "3. Create a plan with '/speckit.plan'",
        "4. Break into tasks with '/speckit.tasks'",
        "5. Execute with '/speckit.implement'",
    ])
    
    return steps
