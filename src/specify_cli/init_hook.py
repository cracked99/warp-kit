#!/usr/bin/env python3
"""
Phase 6: CLI Integration Hook for specify init --warp-spec.

This module provides the integration point for the new project-agnostic
SDD initialization feature. It should be called from the main init command
after project setup but before template download.

Key responsibilities:
- Detect if SDD initialization should run
- Execute the pipeline with proper step tracking
- Display results and next steps to the user
"""

from pathlib import Path
from typing import Optional

from .project_detection import detect_project_stack, detect_sdd_artifacts
from .cli_integration import run_sdd_initialization, get_next_steps, InitializationResult


def should_init_sdd(project_path: Path, warp_spec_flag: bool = False) -> tuple:
    """
    Determine if SDD initialization should run.
    
    Args:
        project_path: Root directory of the project
        warp_spec_flag: Whether --warp-spec was explicitly passed
    
    Returns:
        Tuple of (should_run: bool, reason: str)
    """
    sdd_status = detect_sdd_artifacts(project_path)
    
    # If --warp-spec is explicitly set, always run
    if warp_spec_flag:
        return (True, "SDD initialization explicitly requested via --warp-spec")
    
    # If not SDD-enabled, auto-enable for non-template projects
    if not sdd_status.is_sdd_enabled:
        # Check if this looks like an existing project (has code/config files)
        has_code = any([
            (project_path / "src").exists(),
            (project_path / "pyproject.toml").exists(),
            (project_path / "package.json").exists(),
            (project_path / "go.mod").exists(),
            (project_path / "pom.xml").exists(),
            (project_path / "Cargo.toml").exists(),
        ])
        
        if has_code or list(project_path.glob("*")) != []:
            return (True, "Project detected - bootstrapping SDD")
        else:
            return (False, "Empty project - SDD will be initialized by template if available")
    
    # Already SDD-enabled
    return (False, "Project already SDD-enabled - skipping bootstrap")


def run_sdd_init_hook(
    project_path: Path,
    warp_spec_flag: bool = False,
    verbose: bool = False,
) -> Optional[InitializationResult]:
    """
    Execute SDD initialization for a project.
    
    This is the main hook to be called from the init command after determining
    the project path. It runs the complete pipeline and returns results.
    
    Args:
        project_path: Root directory of the project
        warp_spec_flag: Whether --warp-spec was explicitly passed
        verbose: Whether to print detailed output
    
    Returns:
        InitializationResult if SDD was initialized, None if skipped
    """
    
    should_run, reason = should_init_sdd(project_path, warp_spec_flag)
    
    if not should_run:
        if verbose:
            print(f"[cyan]SDD init skipped: {reason}[/cyan]")
        return None
    
    if verbose:
        print(f"[cyan]SDD initialization starting: {reason}[/cyan]")
    
    try:
        result = run_sdd_initialization(project_path, auto_enable=True)
        
        if verbose:
            print(f"[cyan]{result.summary()}[/cyan]")
        
        return result
    
    except Exception as e:
        if verbose:
            print(f"[yellow]Warning: SDD initialization encountered an error: {e}[/yellow]")
        return None


def get_sdd_next_steps(result: Optional[InitializationResult]) -> list:
    """
    Generate next steps for the user after initialization.
    
    Args:
        result: InitializationResult from SDD initialization, or None if skipped
    
    Returns:
        List of next steps to display to the user
    """
    
    if result is None:
        return []
    
    return get_next_steps(result)


def format_sdd_summary(result: Optional[InitializationResult]) -> str:
    """
    Format a user-friendly summary of SDD initialization.
    
    Args:
        result: InitializationResult from SDD initialization, or None if skipped
    
    Returns:
        Formatted summary string
    """
    
    if result is None:
        return ""
    
    lines = [
        "",
        "[bold cyan]Spec-Driven Development[/bold cyan]",
        "",
        result.summary(),
    ]
    
    return "\n".join(lines)
