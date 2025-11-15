#!/usr/bin/env python3
"""
WARP Generation Module - Generate or update WARP.md files for projects.

This module provides:
- Root WARP.md generation with stack-specific guidance
- Subdirectory WARP.md generation (src/, tests/, .github/, docs/, scripts/)
- Marker-based idempotent updates (safe to run multiple times)
- README extraction and integration
- Agent-specific rule detection and referencing
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
from pathlib import Path
import re

from .project_detection import DetectedStack, SDDStatus


# ============================================================================
# Constants
# ============================================================================

WARP_PREFIX = """# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository."""

WARP_MANAGED_START = "<!-- specify-init:warp-managed:start -->"
WARP_MANAGED_END = "<!-- specify-init:warp-managed:end -->"


# ============================================================================
# Main WARP Generation Functions
# ============================================================================


def generate_root_warp(
    stack: DetectedStack,
    project_root: Path,
) -> str:
    """
    Generate complete root WARP.md content for a project.
    
    Includes:
    - Required prefix
    - Project overview (from README if present)
    - Technology stack section
    - Development commands
    - Architecture overview
    - Agent-specific rules references
    - Auto-managed SDD section with markers
    
    Args:
        stack: Detected project stack
        project_root: Root directory of the project
    
    Returns:
        Complete WARP.md content as string
    """
    
    sections = [WARP_PREFIX, ""]
    
    # Section 1: Project Overview
    readme_excerpt = _extract_readme_summary(project_root)
    if readme_excerpt:
        sections.append("## Project Overview")
        sections.append("")
        sections.append(readme_excerpt)
        sections.append("")
    
    # Section 2: Technology Stack
    sections.extend(_generate_tech_stack_section(stack))
    sections.append("")
    
    # Section 3: Development Commands
    sections.extend(_generate_commands_section(stack))
    sections.append("")
    
    # Section 4: Architecture Overview
    sections.extend(_generate_architecture_section(project_root, stack))
    sections.append("")
    
    # Section 5: Agent-Specific Rules
    agent_sections = _generate_agent_rules_section(project_root)
    if agent_sections:
        sections.extend(agent_sections)
        sections.append("")
    
    # Section 6: Auto-managed SDD section
    sections.append(WARP_MANAGED_START)
    sections.extend(_generate_sdd_section(stack))
    sections.append(WARP_MANAGED_END)
    
    return "\n".join(sections) + "\n"


def upsert_warp(
    path: Path,
    new_content: str,
) -> Tuple[bool, str]:
    """
    Create or update WARP file with idempotent semantics.
    
    Behavior:
    - If file doesn't exist: create with full content
    - If file exists without markers: append SDD section with markers
    - If file exists with markers: replace only marked content
    
    Args:
        path: Path to WARP.md file (e.g., WARP.md or src/WARP.md)
        new_content: New WARP content to write
    
    Returns:
        (was_created: bool, action: str) tuple for tracking
    """
    
    if not path.exists():
        # First creation: write full content
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_content)
        return (True, "created")
    
    existing = path.read_text()
    
    # Check if markers are present
    if WARP_MANAGED_START not in existing:
        # No markers: append new SDD section, preserve existing content
        if not existing.endswith("\n\n"):
            if existing.endswith("\n"):
                existing += "\n"
            else:
                existing += "\n\n"
        
        # Extract only the SDD section from new content
        sdd_section = _extract_sdd_section(new_content)
        
        result = (
            existing
            + WARP_MANAGED_START + "\n"
            + sdd_section
            + "\n" + WARP_MANAGED_END + "\n"
        )
        
        path.write_text(result)
        return (False, "appended_sdd_section")
    else:
        # Has markers: replace only marked content
        before_marker = existing.split(WARP_MANAGED_START)[0]
        after_marker_raw = existing.split(WARP_MANAGED_END)
        after_marker = after_marker_raw[1] if len(after_marker_raw) > 1 else ""
        
        sdd_section = _extract_sdd_section(new_content)
        
        result = (
            before_marker
            + WARP_MANAGED_START + "\n"
            + sdd_section
            + "\n" + WARP_MANAGED_END
            + after_marker
        )
        
        if result == existing:
            return (False, "no_changes")
        else:
            path.write_text(result)
            return (False, "updated_sdd_section")


def generate_subdir_warps(
    stack: DetectedStack,
    project_root: Path,
) -> List[Tuple[Path, str, Tuple[bool, str]]]:
    """
    Generate WARP.md files for key subdirectories if they exist.
    
    Creates WARPs for: src/, tests/, .github/, docs/, scripts/
    
    Args:
        stack: Detected project stack
        project_root: Root directory of the project
    
    Returns:
        List of (path, content, upsert_result) tuples
    """
    
    results = []
    
    # Generate src/WARP.md if src/ exists
    if (project_root / "src").is_dir():
        content = _generate_src_warp(stack, project_root)
        result = upsert_warp(project_root / "src" / "WARP.md", content)
        results.append((project_root / "src" / "WARP.md", content, result))
    
    # Generate tests/WARP.md if tests/ or test/ or __tests__/ exists
    test_dirs = ["tests", "test", "__tests__"]
    for test_dir in test_dirs:
        if (project_root / test_dir).is_dir():
            content = _generate_tests_warp(stack, project_root, test_dir)
            result = upsert_warp(project_root / test_dir / "WARP.md", content)
            results.append((project_root / test_dir / "WARP.md", content, result))
            break  # Only generate for first matching test dir
    
    # Generate .github/WARP.md if .github/ exists
    if (project_root / ".github").is_dir():
        content = _generate_github_warp(project_root)
        result = upsert_warp(project_root / ".github" / "WARP.md", content)
        results.append((project_root / ".github" / "WARP.md", content, result))
    
    # Generate docs/WARP.md if docs/ exists
    if (project_root / "docs").is_dir():
        content = _generate_docs_warp(project_root)
        result = upsert_warp(project_root / "docs" / "WARP.md", content)
        results.append((project_root / "docs" / "WARP.md", content, result))
    
    # Generate scripts/WARP.md if scripts/ exists
    if (project_root / "scripts").is_dir():
        content = _generate_scripts_warp(project_root)
        result = upsert_warp(project_root / "scripts" / "WARP.md", content)
        results.append((project_root / "scripts" / "WARP.md", content, result))
    
    return results


# ============================================================================
# Section Generators
# ============================================================================


def _generate_tech_stack_section(stack: DetectedStack) -> List[str]:
    """Generate the Technology Stack section."""
    section = [
        "## Technology Stack",
        "",
        f"**Primary Stack:** {stack.name}",
    ]
    
    if stack.signals:
        section.append("")
        section.append("**Key Files/Indicators:**")
        for signal in stack.signals[:5]:  # Limit to first 5 signals
            section.append(f"- `{signal}`")
    
    if stack.test_framework:
        section.append("")
        section.append(f"**Test Framework:** {stack.test_framework}")
    
    return section


def _generate_commands_section(stack: DetectedStack) -> List[str]:
    """Generate the Development Commands section."""
    section = ["## Development Commands"]
    
    commands = stack.commands
    if not commands or all(cmd.startswith("[Your") for cmd in commands.values()):
        # Generic stack or incomplete commands - minimal section
        section.append("")
        section.append("Refer to your project's documentation for build, lint, and test commands.")
        return section
    
    section.append("")
    section.append("### Build")
    section.append(f"```bash")
    section.append(commands.get("build", ""))
    section.append("```")
    section.append("")
    
    section.append("### Lint / Format")
    section.append(f"```bash")
    section.append(commands.get("lint", ""))
    section.append("```")
    section.append("")
    
    section.append("### Run All Tests")
    section.append(f"```bash")
    section.append(commands.get("test_all", ""))
    section.append("```")
    section.append("")
    
    section.append("### Run a Single Test")
    section.append(f"```bash")
    section.append(commands.get("test_single", ""))
    section.append("```")
    
    return section


def _generate_architecture_section(project_root: Path, stack: DetectedStack) -> List[str]:
    """Generate the Architecture Overview section."""
    section = ["## Architecture Overview"]
    section.append("")
    
    # Describe directory structure
    dirs_found = []
    if (project_root / "src").is_dir():
        dirs_found.append("Source code")
    if (project_root / "tests").is_dir() or (project_root / "test").is_dir() or (project_root / "__tests__").is_dir():
        dirs_found.append("Tests")
    if (project_root / "docs").is_dir():
        dirs_found.append("Documentation")
    if (project_root / ".github" / "workflows").is_dir():
        dirs_found.append("CI/CD workflows")
    if (project_root / "scripts").is_dir():
        dirs_found.append("Build scripts")
    
    if dirs_found:
        section.append("**Key Directories:**")
        for d in dirs_found:
            section.append(f"- {d}")
    else:
        section.append("Refer to the directory structure for an overview of the codebase.")
    
    # Try to find main entrypoint
    entrypoint = _find_main_entrypoint(project_root, stack)
    if entrypoint:
        section.append("")
        section.append(f"**Main Entrypoint:** `{entrypoint}`")
    
    return section


def _generate_agent_rules_section(project_root: Path) -> List[str]:
    """Generate section referencing existing agent-specific rules."""
    section = []
    
    agent_files = {
        "CLAUDE.md": "Claude Code",
        ".cursor/rules/": "Cursor",
        ".cursorrules": "Cursor",
        ".github/copilot-instructions.md": "GitHub Copilot",
    }
    
    found_agents = []
    for file_pattern, agent_name in agent_files.items():
        path = project_root / file_pattern
        if path.exists() or (file_pattern.endswith("/") and path.parent.is_dir()):
            found_agents.append((agent_name, file_pattern))
    
    if found_agents:
        section.append("## Agent-Specific Rules")
        section.append("")
        for agent_name, file_path in found_agents:
            section.append(f"When using {agent_name}, see `{file_path}` for additional guidance.")
    
    return section


def _generate_sdd_section(stack: DetectedStack) -> List[str]:
    """Generate the Spec-Driven Development section (auto-managed)."""
    section = [
        "",
        "## Spec-Driven Development",
        "",
        "This project uses Spec-Driven Development (SDD) as its foundational methodology.",
        "All feature development is guided by specifications, plans, and tasks stored in the `specs/` directory.",
        "",
        "### Key SDD Resources",
        "- `memory/constitution.md` – Project principles and development standards",
        "- `specs/` – Feature specifications, technical plans, and task breakdowns",
        "",
        "### Available Commands",
        "Use these commands in your AI coding agent to work with SDD:",
        "- `/speckit.constitution` – Create or refine project principles",
        "- `/speckit.specify` – Define a feature specification",
        "- `/speckit.clarify` – Clarify ambiguous requirements",
        "- `/speckit.plan` – Create technical implementation plan",
        "- `/speckit.tasks` – Break plan into actionable tasks",
        "- `/speckit.implement` – Execute implementation tasks",
        "- `/speckit.analyze` – Cross-check artifact consistency",
        "- `/speckit.checklist` – Generate quality checklists",
    ]
    
    return section


# ============================================================================
# Subdirectory WARP Generators
# ============================================================================


def _generate_src_warp(stack: DetectedStack, project_root: Path) -> str:
    """Generate src/WARP.md content."""
    section = [
        "# WARP.md – Source Code",
        "",
        "Source code in this directory is organized using layered architecture.",
    ]
    
    # Analyze subdirectories
    src_subdirs = []
    for item in (project_root / "src").iterdir():
        if item.is_dir() and not item.name.startswith("."):
            src_subdirs.append(item.name)
    
    if src_subdirs:
        section.append("")
        section.append("**Directories:**")
        for subdir in sorted(src_subdirs)[:5]:  # Limit to 5
            section.append(f"- `{subdir}/`")
    
    # Find main entrypoint
    entrypoint = _find_main_entrypoint(project_root, stack)
    if entrypoint:
        section.append("")
        section.append(f"**Main Entrypoint:** `{entrypoint}`")
    
    section.append("")
    section.append("See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.")
    
    return "\n".join(section) + "\n"


def _generate_tests_warp(stack: DetectedStack, project_root: Path, test_dir: str) -> str:
    """Generate tests/WARP.md content."""
    test_framework = stack.test_framework or "testing"
    
    section = [
        "# WARP.md – Testing",
        "",
        f"Tests in this directory use {test_framework}.",
    ]
    
    section.append("")
    section.append("## Running Tests")
    section.append("")
    section.append("**All tests:**")
    section.append("```bash")
    section.append(stack.commands.get("test_all", ""))
    section.append("```")
    section.append("")
    section.append("**Single test:**")
    section.append("```bash")
    section.append(stack.commands.get("test_single", ""))
    section.append("```")
    section.append("")
    section.append("## Test Conventions")
    section.append("")
    
    if stack.id == "node":
        section.append("- Naming: `*.test.js` or `*.spec.js`")
        section.append(f"- Location: `{test_dir}/`")
    elif stack.id == "python":
        section.append("- Naming: `test_*.py`")
        section.append(f"- Location: `{test_dir}/`")
    elif stack.id == "dotnet":
        section.append("- Naming: `*Tests.cs`")
        section.append(f"- Location: `{test_dir}/`")
    elif stack.id == "go":
        section.append("- Naming: `*_test.go`")
        section.append("- Location: Same directory as source files or `{test_dir}/`")
    else:
        section.append("Refer to your project's testing conventions.")
    
    section.append("")
    section.append("See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.")
    
    return "\n".join(section) + "\n"


def _generate_github_warp(project_root: Path) -> str:
    """Generate .github/WARP.md content."""
    section = [
        "# WARP.md – CI/CD & Automation",
        "",
        "This directory contains GitHub Actions workflows for CI/CD automation.",
    ]
    
    # List workflow files if they exist
    workflows_dir = project_root / ".github" / "workflows"
    if workflows_dir.is_dir():
        workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        if workflows:
            section.append("")
            section.append("**Workflows:**")
            for workflow in sorted(workflows)[:5]:
                section.append(f"- `{workflow.name}`")
    
    section.append("")
    section.append("**Typical roles:**")
    section.append("- Linting and code quality checks")
    section.append("- Running tests on pull requests")
    section.append("- Deploying releases")
    section.append("")
    section.append("See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.")
    
    return "\n".join(section) + "\n"


def _generate_docs_warp(project_root: Path) -> str:
    """Generate docs/WARP.md content."""
    section = [
        "# WARP.md – Documentation",
        "",
        "Documentation for this project is maintained in this directory.",
    ]
    
    # List doc files if they exist
    docs_dir = project_root / "docs"
    if docs_dir.is_dir():
        doc_files = list(docs_dir.glob("*.md"))
        if doc_files:
            section.append("")
            section.append("**Key Documents:**")
            for doc in sorted(doc_files)[:5]:
                section.append(f"- `{doc.name}`")
    
    section.append("")
    section.append("See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.")
    
    return "\n".join(section) + "\n"


def _generate_scripts_warp(project_root: Path) -> str:
    """Generate scripts/WARP.md content."""
    section = [
        "# WARP.md – Scripts & Automation",
        "",
        "Helper scripts for building, testing, and managing this project.",
    ]
    
    # List script files if they exist
    scripts_dir = project_root / "scripts"
    if scripts_dir.is_dir():
        scripts = []
        for item in scripts_dir.iterdir():
            if item.is_file() and (item.suffix in [".sh", ".ps1", ".py", ".js"] or item.name.startswith(".")):
                scripts.append(item.name)
        
        if scripts:
            section.append("")
            section.append("**Scripts:**")
            for script in sorted(scripts)[:5]:
                section.append(f"- `{script}`")
    
    section.append("")
    section.append("See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.")
    
    return "\n".join(section) + "\n"


# ============================================================================
# Helper Functions
# ============================================================================


def _extract_readme_summary(project_root: Path) -> Optional[str]:
    """
    Extract project summary from README.md (first heading + intro).
    
    Returns the first heading and first paragraph (up to 3 sentences).
    """
    readme_path = project_root / "README.md"
    
    if not readme_path.exists():
        return None
    
    try:
        content = readme_path.read_text()
        lines = content.split("\n")
        
        # Find first heading and intro
        summary_lines = []
        in_intro = False
        sentence_count = 0
        
        for line in lines:
            # Skip initial whitespace
            if not summary_lines and line.strip() == "":
                continue
            
            # Capture heading
            if line.startswith("#") and not in_intro:
                summary_lines.append(line.strip())
                in_intro = True
                continue
            
            # Capture intro paragraph
            if in_intro and line.strip() and not line.startswith("#"):
                summary_lines.append(line.strip())
                # Count sentences (rough heuristic)
                sentence_count += line.count(".") + line.count("!") + line.count("?")
                if sentence_count >= 3:
                    break
            elif in_intro and not line.strip():
                # End of intro paragraph
                if summary_lines:
                    break
        
        if summary_lines:
            return "\n".join(summary_lines[:3])  # Limit to 3 lines
    
    except Exception:
        pass
    
    return None


def _extract_sdd_section(warp_content: str) -> str:
    """Extract just the SDD section from full WARP content."""
    if WARP_MANAGED_START in warp_content:
        start_idx = warp_content.find(WARP_MANAGED_START)
        end_idx = warp_content.find(WARP_MANAGED_END)
        if start_idx >= 0 and end_idx > start_idx:
            # Extract the section between markers (without markers)
            section = warp_content[
                start_idx + len(WARP_MANAGED_START):end_idx
            ].strip()
            return section
    
    # If no markers, return everything after "## Spec-Driven Development"
    if "## Spec-Driven Development" in warp_content:
        idx = warp_content.find("## Spec-Driven Development")
        return warp_content[idx:].strip()
    
    return ""


def _find_main_entrypoint(project_root: Path, stack: DetectedStack) -> Optional[str]:
    """Find the main entrypoint file for the project."""
    candidates = {
        "node": ["src/index.js", "src/index.ts", "index.js", "app.js"],
        "python": ["src/main.py", "main.py", "app.py", "src/__main__.py"],
        "dotnet": ["Program.cs", "src/Program.cs"],
        "go": ["main.go", "cmd/main.go"],
        "java": ["src/Main.java", "Main.java"],
        "rust": ["src/main.rs"],
    }
    
    search_list = candidates.get(stack.id, [])
    
    for candidate in search_list:
        path = project_root / candidate
        if path.exists() and path.is_file():
            return candidate
    
    return None
