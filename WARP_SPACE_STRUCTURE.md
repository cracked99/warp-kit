# .warp-space Directory Structure

## Overview

`.warp-space` is a complete replacement for `.specify` that contains all Spec-Driven Development (SDD) infrastructure with additional Warp-specific context files.

## Directory Structure

```
.warp-space/
├── Warp-space.md              # Single source of truth (main reference document)
├── memory/
│   └── constitution.md         # Project principles and quality standards
├── commands/
│   ├── constitution.md         # /speckit.constitution command template
│   ├── specify.md              # /speckit.specify command template
│   ├── clarify.md              # /speckit.clarify command template
│   ├── plan.md                 # /speckit.plan command template
│   ├── tasks.md                # /speckit.tasks command template
│   ├── implement.md            # /speckit.implement command template
│   ├── analyze.md              # /speckit.analyze command template
│   ├── checklist.md            # /speckit.checklist command template
│   └── taskstoissues.md        # /speckit.taskstoissues command template
├── templates/
│   ├── spec-template.md        # Specification template (WHAT/WHY)
│   ├── plan-template.md        # Implementation plan template (HOW)
│   ├── tasks-template.md       # Task breakdown template
│   ├── agent-file-template.md  # Agent-generated guidelines template
│   └── checklist-template.md   # Quality checklist template
├── scripts/
│   ├── bash/
│   │   ├── check-prerequisites.sh
│   │   ├── common.sh
│   │   ├── create-new-feature.sh
│   │   ├── setup-plan.sh
│   │   ├── update-agent-context.sh
│   │   └── README.md
│   └── powershell/
│       ├── check-prerequisites.ps1
│       ├── common.ps1
│       ├── create-new-feature.ps1
│       ├── setup-plan.ps1
│       ├── update-agent-context.ps1
│       └── README.md
├── agents/
│   └── README.md              # Agent configuration reference
├── core/
│   └── architecture.md        # System architecture and design documentation
└── vscode-settings.json       # VS Code chat settings for command discovery
```

## Key Directories

### `/memory`
- Stores project governance and principles
- **constitution.md**: Canonical source of project rules, standards, and constraints
- Stack-specific guidance integrated into the template

### `/commands`
- Agent-specific command templates (9 total)
- Each command file (*.md) contains:
  - YAML frontmatter with description and handoffs
  - Execution outline
  - Script invocations for bash/powershell
- These are the actual /speckit.* commands agents can invoke

### `/templates`
- SDD artifact templates for specifications, plans, and tasks
- Used as boilerplate when creating new features
- Includes agent guidelines and quality checklists

### `/scripts`
- Helper automation for SDD workflows
- **bash/**: Shell scripts for POSIX-compatible systems
- **powershell/**: PS1 scripts for Windows systems
- Common functions:
  - `create-new-feature`: Branch and spec creation
  - `setup-plan`: Plan scaffolding
  - `check-prerequisites`: Dependency validation
  - `update-agent-context`: Agent guidance refresh

### `/agents`
- Agent-specific configurations and rules
- Reference documentation for supported AI coding assistants
- Extensible for new agent integrations

### `/core`
- Architecture and design documentation
- **architecture.md**: System overview and component descriptions
- Platform for documenting design decisions

### `vscode-settings.json`
- VS Code Chat configuration
- Command discovery recommendations
- Terminal approval for automation scripts

### `Warp-space.md` (root)
- Central reference document (single source of truth)
- Artifact map explaining all directories
- Workflow guidance for creating features
- Project metadata

## How This Replaces `.specify`

`.warp-space` maintains full compatibility with `.specify` structure while adding:

1. **Unified `.warp-space/` directory** instead of scattered locations
2. **Full command templates** instead of stubs
3. **Actual scripts** from spec-kit instead of placeholders
4. **Comprehensive architecture documentation** via `/core`
5. **Explicit agent support** via `/agents`
6. **Single source of truth** via `Warp-space.md`

## Creation Process

When `warp-kit init --here` is run:

1. Project stack is automatically detected
2. `.warp-space/` directory structure is created
3. All templates are copied from warp-kit package
4. Scripts from spec-kit are installed
5. Project constitution is generated (stack-specific)
6. Agent command definitions are populated
7. All directories and files are idempotently created (safe to run multiple times)

## Synchronization with spec-kit

All content in `.warp-space/` is kept in sync with the official spec-kit repository:

- ✅ 9 command files (bytewise identical)
- ✅ 5 template files (bytewise identical)
- ✅ 10 script files (bash & powershell)
- ✅ vscode-settings.json (synchronized)

This ensures warp-kit provides the complete, authentic spec-kit experience for SDD development.

## Next Steps

After `.warp-space` is created:

1. Review `.warp-space/Warp-space.md` for project reference
2. Customize `.warp-space/memory/constitution.md` for project principles
3. Use `/speckit.*` commands in your AI agent
4. Refer to `.warp-space/templates/` when creating new features
5. Use `.warp-space/scripts/` for automated SDD tasks
