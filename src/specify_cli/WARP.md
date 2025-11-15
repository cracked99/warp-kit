# WARP.md – Specify CLI Implementation

Warp agents MUST treat the **global rule "Spec-Driven Development (SDD) – Global Workflow"** and the **root `WARP.md`** as the baseline. This file provides specialized guidance for the CLI implementation.

---

## Scope & Purpose

This directory contains the **core Specify CLI implementation** – a single, monolithic Python module (`__init__.py`) responsible for:

- Parsing CLI arguments and options via `typer`
- Downloading templates from GitHub Releases API
- Extracting and merging templates into project directories
- Managing agent configuration (15+ AI assistants)
- Rendering interactive UI with arrow-key selection
- Handling file permissions, JSON merging, and git initialization

---

## Architecture Overview

### Key Classes & Components

| Component | Purpose |
|-----------|---------|
| **AGENT_CONFIG** dict (lines 126–217) | Authoritative registry for all supported agents |
| **StepTracker** class | Renders hierarchical progress tree with status symbols |
| **select_with_arrows()** | Interactive selection UI with arrow keys and Rich rendering |
| **download_template_from_github()** | Fetches release metadata and downloads ZIP from GitHub |
| **download_and_extract_template()** | Extracts ZIP, handles nested dirs, merges `.vscode/settings.json` |
| **merge_json_files()** | Deep merges JSON (dictionaries recursive, lists replaced) |
| **ensure_executable_scripts()** | Sets execute bits on `.sh` files on POSIX systems |
| **init_git_repo()** | Runs `git init`, `git add .`, `git commit` |

### Commands

| Command | Responsibility |
|---------|-----------------|
| `specify init` | Bootstrap a new project or merge templates into current directory |
| `specify check` | Verify installed tools (git, agents, code editors) |
| `specify version` | Display CLI and template version info |

---

## Critical Design Principles

### 1. AGENT_CONFIG is Authoritative

- Dictionary keys **must** match actual CLI tool executable names (e.g., `"cursor-agent"`, not `"cursor"`)
- This allows `check_tool()` to use `shutil.which(key)` directly
- **Eliminates special-case mappings** throughout the codebase
- When adding new agents, use the real CLI name as the key; the `name` field is for display

### 2. No Special-Case Logic for Agent Names

- ❌ Bad: `if agent == "cursor": real_name = "cursor-agent"`
- ✅ Good: Use `"cursor-agent"` as the key from the start

### 3. Template Download Pattern

- CLI only **downloads** pre-built release packages; it does not generate them
- Template generation happens in CI (`.github/workflows/release.yml`)
- This keeps the CLI simple and the build system as the source of truth

### 4. Error Handling & User Feedback

- Use `rich.Panel` for error messages with context
- Parse GitHub rate-limit headers and provide actionable troubleshooting
- On network failures, show detailed error panels with rate-limit info and suggestions
- On extraction failures, clean up partial directories and show helpful recovery steps

---

## SDD-Aligned Modification Workflow

For **adding or modifying CLI commands or agent support**:

1. **Update or create specs** under `specs/` that describe the new behavior or agent
2. **Clarify edge cases** (error modes, validation, CLI UX) and document them in the spec
3. **Update or write a plan** mapping specs to:
   - CLI commands, options, files to change
   - Data flows between CLI and templates/scripts
4. **Produce tasks** with explicit file paths and tests (e.g., unit tests for command behavior)
5. **Implement changes**, keeping AGENT_CONFIG and docstrings in sync with AGENTS.md
6. **Validate** via tests and manual CLI runs, mapping results back to spec items

---

## Modification Checklist for Warp Agents

Before editing this directory, **explicitly confirm**:

- [ ] Which spec and plan govern the change (if not found, propose creating them)
- [ ] Whether AGENTS.md and AGENT_CONFIG must be updated together
- [ ] Whether versioning and CHANGELOG updates are required (per AGENTS.md rule)
- [ ] Which tests (and workflow steps in `.github/`) must pass

---

## Known Limitations

- **No automated tests** – CI runs linting only; tests should be added
- **Single large module** – Consider future refactoring into submodules (but respect existing architecture)
- **GitHub-only templates** – No easy way to use local or custom template sources without code changes

---

## Testing Changes Locally

```bash
# Run CLI directly
python -m src.specify_cli --help
python -m src.specify_cli init demo --ai claude --ignore-agent-tools

# Test with uvx (simulates user experience)
uvx --from . specify init test-proj --ai copilot --script sh

# Editable install in venv
uv venv && source .venv/bin/activate
uv pip install -e .
specify --help
```

---

## Design Decisions to Respect

1. **AGENT_CONFIG is single source of truth** – Do not hard-code agent names or paths elsewhere
2. **Version and CHANGELOG updates are required** for any change to `__init__.py`
3. **No special-case agent handling** – Prefer extending configuration-driven design
4. **Rich.Panel and StepTracker for UX** – Keep terminal output consistent and accessible
