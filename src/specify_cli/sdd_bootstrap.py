#!/usr/bin/env python3
"""
Warpify Bootstrap Module - Bootstrap Spec-Driven Development artifacts.

This module provides:
- Warp-gate.md creation as single source of truth
- Constitution creation (stack-specific)
- Specs directory structure setup
- Base templates for specs/plans/tasks
- Agent command definitions copying
- Helper scripts population
"""

from typing import List, Tuple
from pathlib import Path
from datetime import datetime

from .project_detection import DetectedStack, SDDStatus


# ============================================================================
# Constants
# ============================================================================

CONSTITUTION_TEMPLATE = """# {{PROJECT_NAME}} Constitution

## Core Principles

### I. Spec-Driven Development (Mandatory)
All features begin with a specification in `specs/`. Code is an implementation of the spec, not the other way around.

### II. Test-First Development
Tests are written before or alongside implementation. Testing is non-negotiable for code quality.

### III. Code Quality Standards
- Clear, readable code with meaningful names
- Consistent style across the codebase
- Documentation for complex logic
{{STACK_SPECIFIC}}
### IV. Architecture & Organization
Code is organized by responsibility and functionality. Maintain clear separation of concerns.

### V. Collaboration & Communication
- Specifications and plans are the primary communication vehicles
- Use `/speckit.*` commands to structure development
- Keep artifacts up-to-date as you learn and iterate

## Development Workflow

1. **Specify** – Describe what to build (spec.md)
2. **Plan** – Design the technical approach (plan.md)
3. **Tasks** – Break into actionable items (tasks.md)
4. **Implement** – Build according to plan
5. **Test** – Validate against specification
6. **Review** – Align implementation with spec

## Quality Gates

- All public APIs documented
- Test coverage for critical paths
- Code passes linting and type checking where applicable
- Specs are updated if behavior changes during implementation

**Version:** 1.0 | **Ratified:** 2025-11-15 | **Last Amended:** 2025-11-15
"""

WARPSPACE_TEMPLATE = """# Warp-space.md – {{PROJECT_NAME}} Central Source of Truth

This file is the single source of truth for the project's Spec-Driven Development (SDD) architecture.

It references and coordinates all SDD artifacts stored in the `.warp-space/` directory.

---

## .warp-space Directory Structure

The `.warp-space/` directory contains all SDD governance and metadata:

```
.warp-space/
├── Warp-space.md             ← You are here (single source of truth)
├── core/
│   └── architecture.md       # Overall system design and principles
├── memory/
│   └── constitution.md       # Project principles, quality bars, constraints
├── commands/
│   └── <agent-name>.md       # Agent-specific command definitions
├── templates/
│   ├── spec-template.md      # Specification template
│   ├── plan-template.md      # Implementation plan template
│   └── tasks-template.md     # Task breakdown template
└── scripts/
    ├── bash/                 # Bash helper scripts
    └── powershell/           # PowerShell helper scripts
```

---

## Artifact Map

This section maps all SDD artifacts and their purposes:

### Constitution (.warp-space/memory/constitution.md)
**Purpose:** Encodes project-wide principles, quality standards, and constraints.

**Contains:**
- Core development principles (SDD, testing, code quality)
- Stack-specific guidance  
- Development workflow
- Quality gates and acceptance criteria

**When to Use:**
- Refer to when making design decisions
- Update when project standards change
- Ratified by team; changes require consensus

### Specifications (specs/)
**Purpose:** Functional requirements and user stories for individual features.

**Structure:**
```
specs/
├── 001-feature-name/
│   ├── spec.md          # WHAT and WHY the feature exists
│   ├── plan.md          # HOW to implement it
│   ├── tasks.md         # Ordered, traceable tasks
│   └── ...              # Supporting docs
```

### Templates (.warp-space/templates/)
**Purpose:** Standard formats for specs, plans, and tasks.

**Files:**
- `spec-template.md` – Use when creating a new feature specification
- `plan-template.md` – Use when designing technical approach
- `tasks-template.md` – Use when breaking work into tasks

### Agent Commands (.warp-space/commands/)
**Purpose:** Agent-specific command definitions and workflows.

### Helper Scripts (.warp-space/scripts/)
**Purpose:** Automation and utility scripts for SDD workflows.

---

## How to Use This Project

### For New Features
1. Create a directory in `specs/` (e.g., `specs/001-user-auth/`)
2. Use `/speckit.specify` to create `spec.md` (WHAT and WHY)
3. Use `/speckit.clarify` to record edge cases and decisions
4. Use `/speckit.plan` to design the technical approach in `plan.md`
5. Use `/speckit.tasks` to break into ordered tasks in `tasks.md`
6. Use `/speckit.implement` to execute the tasks
7. Validate that implementation matches the spec

---

## Metadata

**Created:** {{CREATED_DATE}}
**Last Updated:** {{CREATED_DATE}}
**SDD Version:** 1.0
**Project:** {{PROJECT_NAME}}
"""

SPECS_README = """# Specifications

This directory contains all feature specifications, implementation plans, and task breakdowns for this project.

## Structure

Each feature is organized in its own directory:

```
specs/
├── 001-feature-name/
│   ├── spec.md          # What should this feature do?
│   ├── plan.md          # How will we build it?
│   ├── tasks.md         # Ordered task breakdown
│   └── ...              # Supporting docs (contracts, research, etc.)
├── 002-another-feature/
│   └── ...
└── _templates/          # Base templates for new features
```

## Workflow

1. Create a new feature directory (or use `/speckit.specify`)
2. Write the functional specification (spec.md)
3. Clarify ambiguities with `/speckit.clarify`
4. Design the technical plan (plan.md)
5. Break into tasks (tasks.md)
6. Execute with `/speckit.implement`

## SDD Commands

- `/speckit.specify` – Create or refine a specification
- `/speckit.clarify` – Clarify ambiguous requirements
- `/speckit.plan` – Design the technical approach
- `/speckit.tasks` – Generate task breakdown
- `/speckit.implement` – Execute tasks
- `/speckit.analyze` – Cross-check artifact consistency
- `/speckit.checklist` – Generate quality checklists

## Tips

- Keep specs focused on WHAT and WHY, not HOW
- Use clarifications to record decisions
- Tasks should be granular and testable
- Reference the constitution for quality standards
"""

SPEC_TEMPLATE = """# {{FEATURE_NAME}} Specification

## Feature Overview

[Describe the feature in 2-3 sentences. What problem does it solve? Who is it for?]

## User Stories

### Story 1: [Descriptive Title]
**As a** [user type]  
**I want to** [capability]  
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Functional Requirements

### FR-1: [Requirement Name]
[Detailed description of what the system should do]

### FR-2: [Requirement Name]
[Detailed description]

## Non-Functional Requirements

### NFR-1: [Performance / Scale / Reliability]
[Specific metrics or standards]

## Clarifications Section

(To be populated as ambiguities arise)

## Out of Scope

- [Item that is NOT part of this feature]
- [Another out-of-scope item]
"""

PLAN_TEMPLATE = """# {{FEATURE_NAME}} Implementation Plan

## Overview

[Brief description of the technical approach]

## Architecture & Design

### Key Components
- [Component 1]: [Responsibility]
- [Component 2]: [Responsibility]

### Data Flow
[Describe how data moves through the system]

### External Dependencies
- [Dependency 1]: [Version/Notes]
- [Dependency 2]: [Version/Notes]

## Technical Details

### [Module/Layer Name]
[Implementation details for this part]

## Database/Data Model
[If applicable, describe the data schema]

## API Specification
[If applicable, describe endpoints and contracts]

## Implementation Phases
[Break down into logical phases if needed]

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| [Risk] | [Impact] | [How to mitigate] |

## Success Criteria
- [ ] All functional requirements implemented
- [ ] Tests pass
- [ ] Meets performance requirements
"""

TASKS_TEMPLATE = """# {{FEATURE_NAME}} Tasks

## Overview
[Brief summary of what needs to be done]

## Task List

### Phase 1: [Phase Name]

#### Task 1.1: [Task Title]
- **File(s)**: [Files to create/modify]
- **Dependencies**: [Prior tasks]
- **Acceptance Criteria**:
  - [ ] Criterion 1
  - [ ] Criterion 2

#### Task 1.2: [Task Title]
- **File(s)**: [Files]
- **Dependencies**: 1.1
- **Acceptance Criteria**:
  - [ ] Criterion 1

### Phase 2: [Phase Name]
[Similar structure for Phase 2]

## Testing Tasks
- [ ] Unit tests for [Component]
- [ ] Integration tests for [Component]
- [ ] Manual testing checklist

## Success Criteria
- [ ] All tasks completed
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Deployed/Merged
"""


# ============================================================================
# Bootstrap Functions
# ============================================================================


def create_warpspace(
    project_root: Path,
) -> Tuple[bool, str]:
    """
    Create or update .warp-space/Warp-space.md as the single source of truth.
    
    Also removes any legacy files/directories.
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        (was_created: bool, action: str) tuple
    """
    
    warp_space_dir = project_root / ".warp-space"
    warp_space_dir.mkdir(parents=True, exist_ok=True)
    
    warpspace_path = warp_space_dir / "Warp-space.md"
    
    # Remove legacy files if they exist
    warpgate_path = warp_space_dir / "Warp-gate.md"
    old_warpify_dir = project_root / ".warpify"
    if warpgate_path.exists():
        warpgate_path.unlink()
    if old_warpify_dir.exists():
        import shutil
        shutil.rmtree(old_warpify_dir)
    
    # Create or update Warp-space.md
    created_date = datetime.now().strftime("%Y-%m-%d")
    content = WARPSPACE_TEMPLATE.replace(
        "{{PROJECT_NAME}}", project_root.name
    ).replace(
        "{{CREATED_DATE}}", created_date
    )
    
    warpspace_path.write_text(content)
    return (True, "created")


def create_or_update_constitution(
    project_root: Path,
    stack: DetectedStack,
    sdd_status: SDDStatus,
) -> Tuple[bool, str]:
    """
    Create or update .warpify/memory/constitution.md with stack-specific principles.
    
    If constitution exists, it is preserved (not overwritten).
    
    Args:
        project_root: Root directory of the project
        stack: Detected project stack
        sdd_status: SDD artifact status
    
    Returns:
        (was_created: bool, action: str) tuple
    """
    
    memory_dir = project_root / ".warp-space" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    
    const_path = memory_dir / "constitution.md"
    
    if const_path.exists():
        # Preserve existing constitution
        return (False, "preserved")
    
    # Create stack-specific template
    stack_specific = _get_constitution_stack_notes(stack)
    
    content = CONSTITUTION_TEMPLATE.replace(
        "{{PROJECT_NAME}}", project_root.name
    ).replace(
        "{{STACK_SPECIFIC}}", stack_specific
    )
    
    const_path.write_text(content)
    return (True, "created")


def setup_specs_directory(project_root: Path) -> List[Tuple[bool, str]]:
    """
    Set up specs/ directory with README and .warp-space/templates.
    
    Creates:
    - specs/README.md
    - .warp-space/templates/{spec,plan,tasks}-template.md
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        List of (was_created, action) tuples
    """
    
    actions = []
    
    # Create specs/ directory
    specs_dir = project_root / "specs"
    specs_dir.mkdir(exist_ok=True)
    
    # Create specs/README.md
    specs_readme = specs_dir / "README.md"
    if not specs_readme.exists():
        specs_readme.write_text(SPECS_README)
        actions.append((True, "created_specs_readme"))
    else:
        actions.append((False, "specs_readme_exists"))
    
    # Create .warp-space/templates/
    templates_dir = project_root / ".warp-space" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    templates = [
        ("spec-template.md", SPEC_TEMPLATE),
        ("plan-template.md", PLAN_TEMPLATE),
        ("tasks-template.md", TASKS_TEMPLATE),
        ("agent-file-template.md", "# [PROJECT NAME] Development Guidelines\n\nAuto-generated from all feature plans."),
        ("checklist-template.md", "# [CHECKLIST TYPE] Checklist\n\nGenerated by /speckit.checklist command."),
    ]
    
    for template_name, template_content in templates:
        template_path = templates_dir / template_name
        if not template_path.exists():
            template_path.write_text(template_content)
            actions.append((True, f"created_{template_name}"))
        else:
            actions.append((False, f"{template_name}_exists"))
    
    return actions


def setup_agent_commands(project_root: Path) -> List[Tuple[bool, str]]:
    """
    Set up .warp-space/commands/ directory with agent command files.
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        List of (was_created, action) tuples
    """
    
    actions = []
    
    commands_dir = project_root / ".warp-space" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Agent commands to populate
    agent_commands = [
        ("constitution.md", "# /speckit.constitution\n\nCreate or refine project principles."),
        ("specify.md", "# /speckit.specify\n\nCreate or refine the specification."),
        ("clarify.md", "# /speckit.clarify\n\nClarify ambiguous requirements."),
        ("plan.md", "# /speckit.plan\n\nCreate the technical implementation plan."),
        ("tasks.md", "# /speckit.tasks\n\nGenerate implementation tasks."),
        ("implement.md", "# /speckit.implement\n\nExecute implementation tasks."),
        ("analyze.md", "# /speckit.analyze\n\nCross-artifact consistency check."),
        ("checklist.md", "# /speckit.checklist\n\nGenerate quality checklists."),
        ("taskstoissues.md", "# /speckit.taskstoissues\n\nConvert tasks into GitHub issues."),
    ]
    
    for cmd_name, cmd_content in agent_commands:
        cmd_path = commands_dir / cmd_name
        if not cmd_path.exists():
            cmd_path.write_text(cmd_content)
            actions.append((True, f"created_{cmd_name}"))
        else:
            actions.append((False, f"{cmd_name}_exists"))
    
    return actions


def setup_warp_space_scripts(project_root: Path) -> List[Tuple[bool, str]]:
    """
    Set up .warp-space/scripts/ directories.
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        List of (was_created, action) tuples
    """
    
    actions = []
    
    scripts_dir = project_root / ".warp-space" / "scripts"
    
    # Create bash and powershell subdirectories
    for script_type in ["bash", "powershell"]:
        subdir = scripts_dir / script_type
        subdir.mkdir(parents=True, exist_ok=True)
        
        # Create placeholder README
        readme = subdir / "README.md"
        if not readme.exists():
            readme.write_text(f"# {script_type.capitalize()} Scripts\n\nHelper scripts for SDD workflows.\n")
            actions.append((True, f"created_{script_type}_scripts_dir"))
        else:
            actions.append((False, f"{script_type}_scripts_dir_exists"))
    
    return actions


def setup_warp_space_config(project_root: Path) -> List[Tuple[bool, str]]:
    """
    Set up .warp-space configuration files (vscode-settings.json, WARP.md).
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        List of (was_created, action) tuples
    """
    
    actions = []
    
    warp_space_dir = project_root / ".warp-space"
    
    # Create vscode-settings.json
    vscode_settings_content = """{
    "chat.promptFilesRecommendations": {
        "speckit.constitution": true,
        "speckit.specify": true,
        "speckit.plan": true,
        "speckit.tasks": true,
        "speckit.implement": true
    },
    "chat.tools.terminal.autoApprove": {
        ".warp-space/scripts/bash/": true,
        ".warp-space/scripts/powershell/": true
    }
}"""
    
    vscode_path = warp_space_dir / "vscode-settings.json"
    if not vscode_path.exists():
        vscode_path.write_text(vscode_settings_content)
        actions.append((True, "created_vscode_settings"))
    else:
        actions.append((False, "vscode_settings_exists"))
    
    return actions


# ============================================================================
# Helper Functions
# ============================================================================


def _get_constitution_stack_notes(stack: DetectedStack) -> str:
    """Get stack-specific constitution notes."""
    
    notes = {
        "node": """
### Stack-Specific: Node.js / TypeScript
- Use consistent package management (npm/yarn/pnpm)
- Enforce TypeScript or JSDoc typing
- Use a linter (ESLint) and formatter (Prettier)
- Test framework: Jest, Mocha, or equivalent
- Maintain lockfiles in version control
""",
        "python": """
### Stack-Specific: Python
- Use type hints where possible (Python 3.10+)
- Test framework: pytest (preferred) or unittest
- Use a linter (ruff, pylint) and formatter (black)
- Maintain virtual environments
- Document with docstrings (Google or NumPy style)
""",
        "dotnet": """
### Stack-Specific: .NET / C#
- Follow C# naming conventions (PascalCase for types, camelCase for members)
- Test framework: xUnit, NUnit, or MSTest
- Use async/await patterns appropriately
- Maintain consistent project structure
- XML documentation comments for public APIs
""",
        "go": """
### Stack-Specific: Go
- Follow Go conventions (gofmt, godoc)
- Test framework: testing (built-in)
- Interface-based design where applicable
- Error handling best practices
- Keep dependencies minimal
""",
        "java": """
### Stack-Specific: Java
- Follow Java naming conventions
- Test framework: JUnit or TestNG
- Use build tools: Maven or Gradle
- Maintain clear package structure
- Document with Javadoc
""",
        "rust": """
### Stack-Specific: Rust
- Use cargo as build and package manager
- Test framework: cargo test (built-in)
- Follow Rust conventions (rustfmt, clippy)
- Ownership and borrowing best practices
- Document with doc comments
""",
        "generic": """
### Stack-Specific: Generic / Unknown
- Establish testing practices early
- Define code style guidelines
- Use linting and formatting tools
- Maintain consistency across the codebase
""",
    }
    
    return notes.get(stack.id, notes["generic"])
