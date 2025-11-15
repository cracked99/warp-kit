# Project-Agnostic WARP + SDD Initialization

## Feature Overview

Extend the `specify init` command to work in **any project directory** (new or existing), autonomously detecting the technology stack and bootstrapping a complete Spec-Driven Development (SDD) architecture including tailored WARP.md guidance, project constitution, specifications framework, and agent-specific command definitions.

## User Stories

### Story 1: Bootstrap SDD in an Existing Node.js Project
**As a** developer with an existing Node.js project  
**I want to** run `specify init --warp-spec` in my project directory  
**So that** I immediately have WARP.md guidance tailored to Node.js, a constitution reflecting Node/npm/testing practices, and a specs/ directory ready for SDD workflows

**Acceptance Criteria:**
- Command auto-detects `package.json` and identifies the stack as Node.js
- Generated root WARP.md includes Node.js-specific commands (`npm run build`, `npm test`, etc.)
- Sub-WARP.md files are created for `src/`, `tests/`, `.github/` (if they exist)
- `memory/constitution.md` is created with Node.js/testing principles
- `specs/` directory structure and templates are initialized
- Existing project files (non-SDD) are never modified or deleted
- Command completes with summary of created artifacts and next steps

### Story 2: Bootstrap SDD in a Python Project
**As a** developer with an existing Python project (using `pyproject.toml` or `requirements.txt`)  
**I want to** run `specify init --warp-spec` in the project root  
**So that** I get Python-specific WARP guidance, a constitution aligned with Python practices, and SDD scaffolding

**Acceptance Criteria:**
- Command detects `pyproject.toml`, `setup.py`, or `requirements.txt` and identifies stack as Python
- Generated WARP.md includes Python-specific test commands (pytest, unittest patterns)
- Constitution reflects Python development practices (testing, linting, packaging)
- Command is idempotent—running it again adds no duplicates or errors
- Test framework detection (pytest, unittest) feeds into WARP guidance

### Story 3: Retrofit SDD into a Multi-Stack Monorepo
**As a** developer with a monorepo containing both Node and Python  
**I want to** run `specify init --warp-spec` to set up SDD at the root level  
**So that** the root WARP provides overarching guidance, and I can refine sub-WARPs manually if needed

**Acceptance Criteria:**
- Command detects the highest-confidence stack (or defaults to generic if ambiguous)
- Root WARP.md is created with generic/multi-language safe guidance
- Sub-WARPs can be customized per directory later by the user
- Command does not fail due to mixed stacks; instead, falls back gracefully

### Story 4: Autonomously Create SDD in a New Empty Directory
**As a** user bootstrapping a new project  
**I want to** run `specify init my-project --ai claude` (existing behavior) and have SDD + WARP set up by default  
**So that** new projects start SDD-ready without manual setup steps

**Acceptance Criteria:**
- When `specify init my-project` downloads a template, SDD bootstrap is automatically triggered
- WARP.md is generated based on tech hints in the template or defaults to generic
- Constitution, specs, agent configs are ready to use
- Existing template-download and git-init workflows are preserved

### Story 5: Update SDD Artifacts Without Losing User Edits
**As a** user with an existing SDD project  
**I want to** run `specify init --warp-spec` again (e.g., after adding new directories) and have WARP regenerated  
**So that** SDD artifacts stay in sync with project structure without losing my edits to specs, plans, or tasks

**Acceptance Criteria:**
- Auto-managed sections of WARP.md are updated; user-edited sections are preserved
- Existing `memory/constitution.md` is not overwritten
- Existing `specs/` feature specs are never deleted or modified
- Re-running the command is safe and idempotent (no duplicate sections)

## Functional Requirements

### FR-1: Technology Stack Detection
- **Detect via file presence:** Node.js (`package.json`), Python (`pyproject.toml`, `setup.py`, `requirements.txt`), .NET (`*.csproj`, `*.sln`), Go (`go.mod`), Java (`pom.xml`, `build.gradle`), Rust (`Cargo.toml`), and generic fallback
- **Refine via directory patterns:** `src/`, `tests/`, `__tests__/`, `.github/workflows`, `docs/` to infer conventions
- **Compute confidence scores:** Weight detection signals; use highest-confidence match; default to "generic" if all scores are low
- **Capture metadata:** Inferred test frameworks (pytest, jest, mocha, xunit, etc.), primary source and test directories, build commands

### FR-2: WARP.md Generation (Root + Subdirectories)
- **Root WARP.md:**
  - Always start with required prefix: `# WARP.md\n\nThis file provides guidance to WARP (warp.dev) when working with code in this repository.`
  - Extract project purpose/description from `README.md` (if present)
  - Include stack-specific development commands: build, lint, test-all, single-test invocation
  - For generic stacks: minimize command sections; focus on SDD guidance
  - Describe architecture at a high level using directory patterns, not individual files
  - Reference existing config files (CLAUDE.md, .cursorrules, .github/copilot-instructions.md) if present
  - No generic boilerplate (e.g., "write unit tests", "avoid secrets"); be specific to the project
  - Avoid repetition; cross-reference instead of duplicating information

- **Subdirectory WARP.md files** (created if directories exist):
  - `src/WARP.md`: Describe code organization (layers, modules) based on detected patterns; link to root WARP for SDD rules
  - `tests/WARP.md`: Test framework name, test command, single-test invocation pattern, naming conventions
  - `.github/WARP.md`: Role of CI/CD workflows, links to workflow files
  - `docs/WARP.md`: Documentation generation, integration with SDD (e.g., spec docs)
  - `scripts/WARP.md`: Purpose of scripts, integration with SDD workflows

- **Update Semantics:**
  - First creation: generate full WARP using auto-managed markers (`<!-- specify-init:warp-managed:start/end -->`)
  - If WARP exists without markers: append a new "Spec-Driven Development & WARP usage" section with markers, preserving existing content
  - If WARP exists with markers: replace only marked sections, leave user content untouched
  - Never create duplicate sections across multiple runs

### FR-3: SDD Artifact Bootstrap
- **`memory/constitution.md`:**
  - If missing: create from a templated default that reflects detected stack practices (e.g., TDD if tests present, CI expectations if `.github/workflows/` exists)
  - If present: preserve user content; optionally append stack-specific notes in auto-managed markers
  - Establish project principles around code quality, testing, and SDD discipline

- **`specs/` directory structure:**
  - Ensure `specs/` exists
  - Create `specs/README.md` explaining Spec → Plan → Tasks flow and `/speckit.*` commands
  - Optionally create a sample feature spec (e.g., `specs/example-feature/{spec,plan,tasks}.md`) without interfering with user work
  - Do **not** modify or delete existing feature specs

- **Base templates for specs/plans/tasks:**
  - Add files under `.specify/templates/` or `specs/_templates/` with standard SDD structure
  - Include sections for Clarifications, Acceptance Criteria, Task Dependencies, etc.

- **Agent-specific command definitions:**
  - Use `AGENT_CONFIG` as single source of truth
  - Generate or copy agent command files (Markdown format) to a standard location (e.g., `.specify/agents/<agent-id>/` or similar)
  - Reuse templates from this repo's `templates/commands/` directory

- **`.specify/scripts/` population:**
  - Add helper scripts (bash/PowerShell) that orchestrate SDD workflows
  - Adapt existing scripts from `scripts/bash/` and `scripts/powershell/` in this repo
  - Scripts assist with `/speckit.specify`, `/speckit.plan`, `/speckit.tasks` workflows

- **Idempotency:**
  - Only create files/directories if they don't exist
  - Never overwrite user-authored files unless explicitly marked as auto-generated
  - Safe to run multiple times

### FR-4: Command-Line Interface
- **Preserve existing `specify init` behavior:**
  - All current options (`--ai`, `--script`, `--ignore-agent-tools`, `--no-git`, `--here`, `--force`, `--skip-tls`, `--debug`, `--github-token`) remain unchanged
  - Existing workflows (agent selection, template download, git init) continue to work

- **Add `--warp-spec` flag:**
  - Boolean flag (default: False)
  - When passed: **always** run stack detection, WARP generation, and SDD bootstrap (even for already-SDD projects, but using idempotent updates)
  - When not passed:
    - For **new or non-SDD projects**: auto-enable SDD pipeline by default
    - For **already-SDD projects**: skip SDD pipeline unless `--warp-spec` is explicit
    - Optional: short confirmation prompt before modifying existing non-Spec-Kit projects (spec clarification to decide)

- **Integration with `StepTracker`:**
  - Add phases: "Detecting project tech stack", "Generating WARP.md guidance", "Bootstrapping Spec-Driven Development artifacts"
  - Show progress for each phase with clear status updates

- **Output and Next Steps:**
  - After completion, display summary of created/updated artifacts
  - List available `/speckit.*` commands for next steps
  - For existing projects, note what was added vs. preserved

### FR-5: Project-Agnostic Scope
- **Work in any project directory:**
  - New empty directories
  - Existing non-Spec-Kit projects (Node, Python, .NET, etc.)
  - Existing SDD-enabled projects (augmentation only)
  - Monorepos or unusual layouts (fallback to generic if ambiguous)

- **Auto-detection of project state:**
  - Determine if project is non-SDD, partially SDD, or fully SDD
  - Decide appropriate action (full bootstrap, partial bootstrap, update, skip)

- **Non-destructive merging:**
  - Preserve all existing user files and specs
  - Enhance WARP/constitution with auto-managed sections
  - No overwriting of user specs/plans/tasks

## Non-Functional Requirements

### NFR-1: Supported Technology Stacks
- Node.js / TypeScript
- Python (including various packaging systems)
- .NET / C# (including ASP.NET)
- Go
- Java (Maven/Gradle)
- Rust
- Generic / Unknown (fallback)

### NFR-2: Backward Compatibility
- Existing `specify init` usage patterns remain fully functional
- Template download, agent selection, and git initialization work as before
- No breaking changes to CLI or templates

### NFR-3: Performance
- Stack detection completes in under 1 second for typical projects
- WARP generation completes in under 2 seconds
- Total SDD bootstrap completes in under 10 seconds (excluding template download/extraction)

### NFR-4: Error Handling
- Gracefully fall back to "generic" stack if detection is ambiguous
- Never crash on unusual project layouts
- Provide helpful error messages and recovery suggestions
- Handle missing directories or unreadable files gracefully

### NFR-5: Testing
- Unit tests for detection logic, WARP generation, and SDD bootstrap
- Integration tests for CLI via Typer's CliRunner
- Test fixtures for each supported stack
- Validation that idempotency guarantees hold

## Clarifications Section

(To be populated by `/speckit.clarify` command)

## Out of Scope

- Modifying existing project build configurations (Makefile, package.json, pyproject.toml, etc.)
- Enforcing or changing project structure beyond creating SDD directories
- AI-driven code analysis or intelligent refactoring
- Integration with external package registries or dependency managers
- Automatic test discovery or code coverage analysis
