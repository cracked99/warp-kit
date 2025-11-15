# WARP.md – Helper Scripts & Automation Tooling

Warp agents MUST treat the **global rule "Spec-Driven Development (SDD) – Global Workflow"** and the **root `WARP.md`** as the baseline. This file provides specialized guidance for scripts.

---

## Scope & Purpose

This directory contains **cross-platform automation scripts** used by `/speckit.*` commands and CI/CD workflows to set up and manage SDD projects. These scripts run **inside** user projects after `specify init` completes or during release workflows.

**Contents**:
- **bash/** – POSIX shell scripts (bash/zsh) for Linux/macOS
- **powershell/** – PowerShell scripts for Windows

Scripts are included in every initialized project under `.specify/scripts/` and are invoked by `/speckit.*` slash commands or CI workflows.

---

## Script Inventory

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `check-prerequisites.sh/ps1` | Verify required tools (git, python, docker, etc.) | `/speckit.constitution` or manual |
| `common.sh/ps1` | Shared helper functions (logging, error handling) | All other scripts source this |
| `create-new-feature.sh/ps1` | Set up new feature branch and spec directory | Manual or `/speckit.specify` |
| `setup-plan.sh/ps1` | Create plan and supporting docs for a feature | `/speckit.plan` |
| `update-agent-context.sh/ps1` | Update agent-specific context files (e.g., `CLAUDE.md`) | `/speckit.implement` |

---

## Design Principles

Scripts must:
- **Be idempotent** – safe to run multiple times
- **Respect AGENT_CONFIG and AGENTS.md** as sources of truth for agents
- **Be cross-platform** where defined (e.g., bash + PowerShell variants)
- **Avoid embedding logic** that should live in the CLI; scripts should orchestrate, not re-implement core behavior

---

## SDD-Aligned Script Modification Workflow

For **new or modified scripts**:

1. **Draft or update specs** describing what the script automates (e.g., updating agent context, creating releases)
2. **Clarify assumptions** (environment, tools installed, OS support)
3. **Plan**: define data flow, entrypoints, and interactions with `.github/`, `templates/`, and `src/specify_cli/`
4. **Tasks**: list script files, test cases (e.g., dry-run mode, unit tests if scripted in Python), and docs to update
5. **Implement script changes** with clear comments and error handling
6. **Validate** by:
   - Running scripts in a controlled environment
   - Confirming behavior aligns with spec and does not corrupt repo state

---

## Modification Checklist for Warp Agents

Before editing `scripts/`, **explicitly confirm**:

- [ ] Which CI workflows and CLI behaviors depend on the script
- [ ] AGENTS.md and AGENT_CONFIG are consistent with any hard-coded agent lists in scripts
- [ ] A documented way to test the script safely exists
- [ ] Both bash and PowerShell variants are updated (if applicable)
- [ ] Changes are backward compatible or breaking changes are documented

---

## Cross-Platform Compatibility

**Bash Scripts** (`scripts/bash/`):
- Must be POSIX-compliant (use `#!/bin/bash` shebang)
- Test with both `bash` and `zsh`
- Use `${VAR}` syntax, not `$VAR` (for consistency)
- Avoid Bashisms (e.g., `[[`, `+=`, process substitution)

**PowerShell Scripts** (`scripts/powershell/`):
- Use `#!/usr/bin/env pwsh` shebang
- Use `param()` for arguments, not positional parsing
- Use `$ErrorActionPreference = 'Stop'` for strict error handling
- Test with both `powershell` (Windows) and `pwsh` (cross-platform)

---

## Script Behavior Overview

### `check-prerequisites.sh/ps1`

**Checks for**:
- `git` version control
- `python` (3.11+)
- Optional tools (docker, node, etc. depending on project)

**Outputs**:
- List of installed tools and versions
- Warnings for missing tools
- Exit 0 if all required tools present, 1 if missing

### `create-new-feature.sh/ps1`

**Does**:
1. Prompts user for feature name (e.g., "001-user-auth")
2. Creates `specs/001-user-auth/` directory structure
3. Copies base templates into the feature directory
4. (Optionally) Creates a git branch for the feature

**Output**:
- New feature directory ready for specification work
- User sees path to `specs/001-user-auth/spec.md`

### `setup-plan.sh/ps1`

**Does**:
1. Reads existing `specs/<feature>/spec.md`
2. Creates `specs/<feature>/plan.md` and supporting docs
3. Sets up structure for contracts, data-model, research, quickstart

**Output**:
- Feature plan structure created
- Ready for `/speckit.plan` command to fill in content

### `update-agent-context.sh/ps1`

**Does**:
1. Reads current specs, plan, tasks from `specs/`
2. Generates or updates agent-specific context file (e.g., `CLAUDE.md`)
3. Includes relevant spec/plan/task excerpts so agent has full context

**Output**:
- Updated `CLAUDE.md`, `.cursor/context.md`, etc.
- Agent has full project context without needing to manually copy specs

---

## When Adding New Scripts

1. Create both `.sh` (for bash) and `.ps1` (for PowerShell) versions
2. Add to `check-prerequisites.sh/ps1` list if it's a prerequisite
3. Update templates/commands to reference the new script
4. Add to this `WARP.md`
5. Test both versions before merging
6. Merge to `main` → next release will include the scripts

---

## Testing Scripts Locally

```bash
# Test bash script locally
bash scripts/bash/check-prerequisites.sh

# Test PowerShell script
pwsh scripts/powershell/check-prerequisites.ps1

# Run linting (optional, on bash scripts)
shellcheck scripts/bash/*.sh

# For integration tests, run scripts inside a test project
cd /tmp/test-project
bash /path/to/spec-kit/scripts/bash/create-new-feature.sh
```

---

## Interaction with Other Components

**With `.github/` workflows**: Scripts are invoked by `release.yml` and other automation  
**With `templates/`**: Scripts read and process template files  
**With `src/specify_cli/`**: Scripts complement the CLI and are bundled in release packages  
**With `docs/`**: Script behavior should be documented if user-facing

---

## Error Handling & Logging

All scripts should:
- Define clear error messages for failure cases
- Use consistent logging/output format (sourced from `common.sh` or `common.ps1`)
- Exit with meaningful exit codes (0 = success, 1 = failure, specific codes for specific errors)
- Avoid silent failures; always communicate status to the user
