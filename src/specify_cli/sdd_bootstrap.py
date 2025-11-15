#!/usr/bin/env python3
"""
SDD Bootstrap Module - Bootstrap Spec-Driven Development artifacts.

This module provides:
- Constitution creation (stack-specific)
- Specs directory structure setup
- Base templates for specs/plans/tasks
- Agent command definitions copying
- Helper scripts population
"""

from typing import List, Tuple
from pathlib import Path

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


def create_or_update_constitution(
    project_root: Path,
    stack: DetectedStack,
    sdd_status: SDDStatus,
) -> Tuple[bool, str]:
    """
    Create or update memory/constitution.md with stack-specific principles.
    
    If constitution exists, it is preserved (not overwritten).
    
    Args:
        project_root: Root directory of the project
        stack: Detected project stack
        sdd_status: SDD artifact status
    
    Returns:
        (was_created: bool, action: str) tuple
    """
    
    memory_dir = project_root / "memory"
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
    Set up specs/ directory with README and templates.
    
    Creates:
    - specs/README.md
    - .specify/templates/{spec,plan,tasks}-template.md
    
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
    
    # Create .specify/templates/
    templates_dir = project_root / ".specify" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    templates = [
        ("spec-template.md", SPEC_TEMPLATE),
        ("plan-template.md", PLAN_TEMPLATE),
        ("tasks-template.md", TASKS_TEMPLATE),
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
    Set up .specify/agents/ directory with stub agent command files.
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        List of (was_created, action) tuples
    """
    
    actions = []
    
    agents_dir = project_root / ".specify" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    
    # Create placeholder for agent commands
    # In production, these would be copied from templates/commands/
    agent_stub = """# Agent Command Placeholder

This directory will contain agent-specific command definitions.
In a full implementation, these are populated from the main templates/commands/ directory.
"""
    
    stub_file = agents_dir / "README.md"
    if not stub_file.exists():
        stub_file.write_text(agent_stub)
        actions.append((True, "created_agents_readme"))
    else:
        actions.append((False, "agents_readme_exists"))
    
    return actions


def setup_specify_scripts(project_root: Path) -> List[Tuple[bool, str]]:
    """
    Set up .specify/scripts/ directories.
    
    Args:
        project_root: Root directory of the project
    
    Returns:
        List of (was_created, action) tuples
    """
    
    actions = []
    
    scripts_dir = project_root / ".specify" / "scripts"
    
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
