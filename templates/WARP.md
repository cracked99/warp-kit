# WARP.md – SDD Templates & Command Definitions

Warp agents MUST treat the **global rule "Spec-Driven Development (SDD) – Global Workflow"** and the **root `WARP.md`** as the baseline. This file provides specialized guidance for templates.

---

## Scope & Purpose

This directory contains the **source templates** for all SDD artifacts and agent-specific command files. Changes here trigger the release workflow and affect all users of `specify init`.

**Contents**:
- Base templates for specs, plans, tasks, checklists, etc. (used by `/speckit.*` commands)
- Agent-specific command definitions (one per agent, e.g., `commands/specify.md`)
- VS Code settings baseline
- Agent file templates for markdown rendering

---

## How Templates Flow to Users

1. **Developer edits a template** (e.g., `spec-template.md`) in this directory
2. **Merge to `main`** triggers `.github/workflows/release.yml`
3. **CI script** (`.github/workflows/scripts/create-release-packages.sh`):
   - Reads templates from `templates/commands/`
   - Substitutes placeholders: `{SCRIPT}`, `{ARGS}`, `__AGENT__`
   - Converts to per-agent formats (Markdown for most, TOML for Gemini/Qwen)
   - Builds per-agent ZIPs (e.g., `spec-kit-template-claude-sh-v0.0.22.zip`)
4. **GitHub Release** publishes the ZIPs as release assets
5. **User runs** `specify init my-project --ai claude`
6. **CLI downloads** the appropriate ZIP and extracts it to the project
7. **User sees** agent-specific command files in `.claude/commands/` (or `.gemini/`, `.cursor/`, etc.)

---

## Template File Organization

```
templates/
├── spec-template.md           # Base template for specs
├── plan-template.md           # Base template for plans
├── tasks-template.md          # Base template for tasks
├── checklist-template.md      # Base template for checklists
├── agent-file-template.md     # Markdown wrapper for agent-specific commands
├── vscode-settings.json       # VS Code settings baseline (merged, not overwritten)
└── commands/                  # Agent-specific command definitions
    ├── constitution.md        # /speckit.constitution command
    ├── specify.md             # /speckit.specify command
    ├── clarify.md             # /speckit.clarify command
    ├── plan.md                # /speckit.plan command
    ├── tasks.md               # /speckit.tasks command
    ├── analyze.md             # /speckit.analyze command
    ├── checklist.md           # /speckit.checklist command
    ├── implement.md           # /speckit.implement command
    └── taskstoissues.md       # (Optional) Convert tasks to GitHub issues
```

---

## Design Principles

Templates must:
- **Preserve SDD phases** (constitution, spec, plan, tasks) in generated projects
- **Emit consistent directory structures and naming conventions**
- **Use correct argument placeholder formats** per agent (Markdown vs TOML)

Changes to templates must consider:
- **Backward compatibility** for existing users
- **Consistency with AGENT_CONFIG and AGENTS.md**
- **Alignment with documentation** in `docs/` and examples in `README.md`

---

## SDD-Aligned Template Modification Workflow

For **each change in templates**:

1. **Update or create a spec** describing the desired behavior for generated projects (e.g., new agent support, new SDD artifact)
2. **Clarify how the template will be used** by CLI commands, including error cases and configuration options
3. **Plan**: map spec to template structures, placeholder usage, and generation paths
4. **Tasks**: list files under `templates/` to modify and tests to run (e.g., snapshot tests, example generation)
5. **Implement** template changes, ensuring placeholder semantics are documented in comments where helpful
6. **Validate** by:
   - Generating sample projects
   - Confirming the generated artifacts follow SDD norms and match docs

---

## Modification Checklist for Warp Agents

Before editing templates, **explicitly confirm**:

- [ ] Which spec and plan govern this template change (if missing, propose creating them)
- [ ] Which agents and commands are impacted
- [ ] Placeholder formats and directory naming match AGENTS.md and AGENT_CONFIG
- [ ] Corresponding docs and CLI help texts will be updated
- [ ] Changes are backward compatible or breaking changes are clearly documented

---

## Important Notes

- **Never include user-generated content** (specs, plans, tasks, implementation) in release packages
- **Only include base templates and command definitions** – users fill in the rest
- **`.vscode/settings.json` is merged, not overwritten** – to preserve user customizations
- **Template changes are released** – test them thoroughly before merging to `main`

---

## Testing Template Changes

Before releasing:

1. Edit the template file locally
2. Run `specify init` with `--here --force` to test merge behavior
3. Verify placeholders are substituted correctly for multiple agents
4. Check that user specs/plans are not overwritten (should be safe in `specs/`)
5. Validate that generated command files work with their corresponding agents

---

## Agent Command File Structure

Command files use **frontmatter + body** format:

```markdown
---
name: "Specify"
description: "Create a functional specification"
---

# /speckit.specify

Create a functional specification for your feature...

[Detailed AI instructions here, may reference {ARGS}, {SCRIPT}, etc.]
```

**Placeholders** that the release script substitutes:
- `{SCRIPT}` → `sh` or `ps` (script type)
- `{ARGS}` → Agent-specific argument style (e.g., `$ARGUMENTS` for Claude, `{{args}}` for others)
- `__AGENT__` → Agent name from AGENT_CONFIG
