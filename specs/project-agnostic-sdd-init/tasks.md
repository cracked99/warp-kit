# Tasks: Project-Agnostic WARP + SDD Initialization

## Task Groups Overview

| Group | Phase | Tasks | Estimated Effort |
|-------|-------|-------|------------------|
| **Detection Module** | Phase 1 | 1.1–1.5 | 2 days |
| **WARP Generation** | Phase 2 | 2.1–2.6 | 2 days |
| **SDD Bootstrap** | Phase 3 | 3.1–3.5 | 2 days |
| **CLI Integration** | Phase 4 | 4.1–4.3 | 1.5 days |
| **Testing** | Phase 5 | 5.1–5.4 | 2 days |
| **Documentation** | Phase 6 | 6.1–6.4 | 1.5 days |

---

## PHASE 1: Detection Module

### Task 1.1: Implement `project_detection.py` – Core Module Setup
**File:** `src/specify_cli/project_detection.py`  
**Dependencies:** None  
**Effort:** 4 hours

**Description:**
Create the base module with data structures and core detection logic.

**Subtasks:**
- [T] Define `DetectedStack` dataclass with fields: id, name, confidence_score, signals, test_framework, source_dir, test_dir, commands, ci_present
- [T] Define `SDDStatus` dataclass with fields: has_constitution, has_specs, has_specify_dir, has_warp_root, has_warp_subdirs, is_sdd_enabled property
- [T] Implement `detect_project_stack(root: Path) -> DetectedStack` function stub
- [T] Implement `detect_sdd_artifacts(root: Path) -> SDDStatus` function
- [T] Add stack definitions with file patterns and default commands for each stack (node, python, dotnet, go, java, rust, generic)
- [T] Implement confidence scoring algorithm
- [T] Test framework detection for each stack (pytest, jest, mocha, xunit, junit, etc.)

**Acceptance Criteria:**
- ✅ Module imports without errors
- ✅ Data structures have all required fields
- ✅ Functions have correct signatures matching spec
- ✅ Default commands exist for each stack
- ✅ Unit tests can be written against the interface

---

### Task 1.2: Implement Stack Detection Logic
**File:** `src/specify_cli/project_detection.py`  
**Dependencies:** Task 1.1  
**Effort:** 4 hours

**Description:**
Implement file-presence-based detection for all supported stacks.

**Subtasks:**
- [T] Implement Node.js detection: package.json, yarn.lock, pnpm-lock.yaml, tsconfig.json
- [T] Implement Python detection: pyproject.toml, requirements.txt, setup.py, poetry.lock, Pipfile
- [T] Implement .NET detection: *.csproj, *.sln, Directory.Build.props
- [T] Implement Go detection: go.mod, go.sum
- [T] Implement Java detection: pom.xml, build.gradle, .gradle/
- [T] Implement Rust detection: Cargo.toml
- [T] Implement directory-based refinement (src/, tests/, __tests__/, .github/workflows, docs/)
- [T] Implement confidence score aggregation and fallback to "generic"

**Acceptance Criteria:**
- ✅ Correctly identifies each stack in isolated test directories
- ✅ Confidence scores weighted appropriately (primary > secondary)
- ✅ Falls back to "generic" when ambiguous or no signals found
- ✅ Handles missing/inaccessible directories gracefully

---

### Task 1.3: Implement Test Framework Detection
**File:** `src/specify_cli/project_detection.py`  
**Dependencies:** Task 1.2  
**Effort:** 2 hours

**Description:**
Infer test frameworks from lock files, imports, and config files.

**Subtasks:**
- [T] Parse package.json / yarn.lock for jest, mocha, vitest, playwright, cypress
- [T] Parse requirements.txt / pyproject.toml for pytest, unittest, nose2
- [T] Parse .NET project files for xunit, nunit, mstest
- [T] Parse pom.xml / build.gradle for junit, testng
- [T] Scan for Go / Rust test files by convention (test files in same directories)
- [T] Select most prominent framework if multiple detected

**Acceptance Criteria:**
- ✅ Correctly identifies test frameworks in sample projects
- ✅ Handles missing test frameworks gracefully (returns None)
- ✅ Prefers most common/standard framework for each stack

---

### Task 1.4: Create Test Fixtures for Detection Module
**Files:** `tests/fixtures/`, `tests/test_detection.py`  
**Dependencies:** Tasks 1.1–1.3  
**Effort:** 3 hours

**Description:**
Create synthetic project directories for testing detection logic.

**Subtasks:**
- [T] Create fixture: Node.js project (package.json, jest config, src/, tests/)
- [T] Create fixture: Python project (pyproject.toml, pytest.ini, src/, tests/)
- [T] Create fixture: .NET project (*.csproj, bin/, obj/)
- [T] Create fixture: Go project (go.mod, go.sum)
- [T] Create fixture: Java project (pom.xml, src/, target/)
- [T] Create fixture: Rust project (Cargo.toml, src/, target/)
- [T] Create fixture: Generic/ambiguous project (Dockerfile only)
- [T] Create fixture: Monorepo with Node + Python

**Acceptance Criteria:**
- ✅ Each fixture directory can be used by tests
- ✅ Fixtures are minimal but realistic
- ✅ Cleanup automatically after tests

---

### Task 1.5: Write Unit Tests for Detection Module
**File:** `tests/test_detection.py`  
**Dependencies:** Task 1.4  
**Effort:** 3 hours

**Description:**
Comprehensive unit tests for project detection.

**Test Cases:**
- [T] `test_detect_node_stack` – Verify Node.js detection
- [T] `test_detect_python_stack` – Verify Python detection
- [T] `test_detect_dotnet_stack` – Verify .NET detection
- [T] `test_detect_go_stack` – Verify Go detection
- [T] `test_detect_java_stack` – Verify Java detection
- [T] `test_detect_rust_stack` – Verify Rust detection
- [T] `test_detect_generic_fallback` – Empty/Dockerfile-only directories → generic
- [T] `test_detect_monorepo_confidence` – Node + Python → highest confidence wins
- [T] `test_test_framework_detection_pytest` – Python + pytest → pytest detected
- [T] `test_test_framework_detection_jest` – Node + jest → jest detected
- [T] `test_sdd_status_no_artifacts` – Non-SDD project → is_sdd_enabled = False
- [T] `test_sdd_status_full_sdd` – Full SDD project → is_sdd_enabled = True
- [T] `test_sdd_status_partial_sdd` – Only WARP present → is_sdd_enabled = False

**Acceptance Criteria:**
- ✅ All tests pass
- ✅ Coverage > 90% for detection module

---

## PHASE 2: WARP Generation

### Task 2.1: Implement `warp_generation.py` – Core Module Setup
**File:** `src/specify_cli/warp_generation.py`  
**Dependencies:** Task 1.1  
**Effort:** 3 hours

**Description:**
Create base module with WARP generation functions.

**Subtasks:**
- [T] Define `generate_root_warp(stack, project_root, existing_warp) -> str` function
- [T] Implement `extract_readme_summary(project_root) -> Optional[str]`
- [T] Implement `generate_tech_stack_section(stack) -> List[str]`
- [T] Implement `generate_commands_section(stack) -> List[str]`
- [T] Implement `generate_architecture_section(project_root, stack) -> List[str]`
- [T] Implement `generate_agent_rules_section(project_root) -> List[str]`
- [T] Implement `generate_sdd_section(stack) -> List[str]`
- [T] Define `upsert_warp(path, new_content, auto_managed) -> (bool, str)` function

**Acceptance Criteria:**
- ✅ All functions have correct signatures
- ✅ Functions return correct types
- ✅ Module imports without errors

---

### Task 2.2: Implement Root WARP Template Generation
**File:** `src/specify_cli/warp_generation.py`  
**Dependencies:** Task 2.1  
**Effort:** 4 hours

**Description:**
Generate complete root WARP.md content with stack-specific guidance.

**Subtasks:**
- [T] Implement `generate_tech_stack_section` – Stack name, key files, detection signals
- [T] Implement `generate_commands_section` – build, lint, test-all, test-single commands
- [T] Implement `generate_architecture_section` – Directory patterns, main entrypoint
- [T] Implement `generate_agent_rules_section` – References to CLAUDE.md, .cursorrules, etc.
- [T] Implement `generate_sdd_section` – SDD workflow overview, reference to `/speckit.*` commands
- [T] Implement README extraction (first h1/h2 + intro paragraph)
- [T] Ensure no generic boilerplate in output (no "write unit tests", etc.)

**Acceptance Criteria:**
- ✅ Generated WARP starts with required prefix
- ✅ Stack-specific commands are present and correct
- ✅ No forbidden boilerplate appears
- ✅ Architecture description references directories, not individual files
- ✅ References to agent rules files when present

---

### Task 2.3: Implement Subdirectory WARP Generators
**File:** `src/specify_cli/warp_generation.py`  
**Dependencies:** Task 2.2  
**Effort:** 4 hours

**Description:**
Generate focused WARP.md files for key subdirectories.

**Subtasks:**
- [T] Implement `generate_src_warp(stack, project_root) -> str`
- [T] Implement `generate_tests_warp(stack, project_root) -> str`
- [T] Implement `generate_github_warp(project_root) -> str` (if .github/ exists)
- [T] Implement `generate_docs_warp(project_root) -> str` (if docs/ exists)
- [T] Implement `generate_scripts_warp(project_root) -> str` (if scripts/ exists)
- [T] Each subdir WARP references root WARP for SDD principles

**Acceptance Criteria:**
- ✅ Each subdir WARP is concise (2-3 paragraphs max)
- ✅ Includes actionable commands/patterns
- ✅ References root WARP appropriately
- ✅ No duplication of SDD principles

---

### Task 2.4: Implement WARP Update/Merge Semantics
**File:** `src/specify_cli/warp_generation.py`  
**Dependencies:** Task 2.3  
**Effort:** 3 hours

**Description:**
Implement idempotent WARP file creation and updates with marker-based merging.

**Subtasks:**
- [T] Implement `upsert_warp` – Create if missing
- [T] Implement `upsert_warp` – Append SDD section if WARP exists without markers
- [T] Implement `upsert_warp` – Replace only marked sections if markers present
- [T] Ensure no duplicate sections across multiple runs
- [T] Return (was_created, action_description) tuple for tracking
- [T] Add marker comments explaining that auto-managed sections should not be manually edited

**Acceptance Criteria:**
- ✅ First creation: full WARP with markers
- ✅ Second run: only marked sections regenerated, no duplicates
- ✅ WARP without markers: SDD section appended, existing content preserved
- ✅ Idempotent: running twice produces identical output

---

### Task 2.5: Write Unit Tests for WARP Generation
**File:** `tests/test_warp_generation.py`  
**Dependencies:** Tasks 2.1–2.4, 1.4  
**Effort:** 4 hours

**Description:**
Unit tests for WARP generation and idempotency.

**Test Cases:**
- [T] `test_generate_root_warp_node` – Node.js WARP has npm/jest commands
- [T] `test_generate_root_warp_python` – Python WARP has pytest commands
- [T] `test_generate_root_warp_no_boilerplate` – No forbidden text appears
- [T] `test_generate_subdir_warp_src` – src/WARP.md is concise and linked
- [T] `test_generate_subdir_warp_tests` – tests/WARP.md includes test framework
- [T] `test_upsert_warp_first_creation` – Creates file with markers
- [T] `test_upsert_warp_append_sdd_section` – Appends to existing WARP without markers
- [T] `test_upsert_warp_update_marked_section` – Updates only marked content
- [T] `test_upsert_warp_idempotent` – Running twice produces identical output
- [T] `test_warp_prefix_always_present` – Every WARP starts with required prefix

**Acceptance Criteria:**
- ✅ All tests pass
- ✅ Coverage > 90% for WARP generation module
- ✅ Idempotency guarantees verified

---

### Task 2.6: Integration Test: WARP Generation End-to-End
**File:** `tests/test_warp_generation_integration.py`  
**Dependencies:** Tasks 1.5, 2.5  
**Effort:** 2 hours

**Description:**
End-to-end tests for complete WARP generation pipeline.

**Test Cases:**
- [T] `test_warp_generation_node_project` – Full pipeline: detect → generate → verify
- [T] `test_warp_generation_python_project` – Full pipeline for Python
- [T] `test_warp_generation_monorepo_fallback_to_generic` – Mixed stacks fall back gracefully
- [T] `test_subdir_warps_created_for_existing_dirs` – Only generates WARPs for existing dirs

**Acceptance Criteria:**
- ✅ All integration tests pass
- ✅ Generated WARP files are valid Markdown
- ✅ All cross-links (e.g., root → subdir) are correct

---

## PHASE 3: SDD Bootstrap

### Task 3.1: Implement `sdd_bootstrap.py` – Core Module Setup
**File:** `src/specify_cli/sdd_bootstrap.py`  
**Dependencies:** Tasks 1.1, 2.1  
**Effort:** 3 hours

**Description:**
Create base module with SDD bootstrap functions.

**Subtasks:**
- [T] Define function stubs: create_or_update_constitution, setup_specs_directory, setup_agent_commands, setup_specify_scripts
- [T] Load constitution templates for each stack from `templates/` or create defaults
- [T] Load specs README template
- [T] Load template files (spec-template.md, plan-template.md, tasks-template.md)
- [T] Load agent command templates for all agents in AGENT_CONFIG
- [T] Implement helper: `copy_script_file(source, target)`

**Acceptance Criteria:**
- ✅ Module imports without errors
- ✅ All templates are accessible
- ✅ AGENT_CONFIG is used as single source of truth

---

### Task 3.2: Implement Constitution Generation
**File:** `src/specify_cli/sdd_bootstrap.py`  
**Dependencies:** Task 3.1  
**Effort:** 2 hours

**Description:**
Create or update `memory/constitution.md` with stack-specific principles.

**Subtasks:**
- [T] Load constitution templates for each stack (node, python, dotnet, go, java, rust, generic)
- [T] Create templates emphasizing:
  - Python: pytest, packaging, virtual environments, type hints
  - Node: npm/yarn/pnpm, ESM/CommonJS, test coverage
  - .NET: solution structure, NuGet, async patterns
  - Go/Java/Rust: language-specific best practices
- [T] Implement `create_or_update_constitution(project_root, stack, sdd_status)`
- [T] If constitution missing: create from stack-specific template
- [T] If constitution exists: preserve existing (don't overwrite)

**Acceptance Criteria:**
- ✅ Constitution created for new projects
- ✅ Existing constitutions preserved
- ✅ Stack-specific principles are evident in templates

---

### Task 3.3: Implement Specs Directory Setup
**File:** `src/specify_cli/sdd_bootstrap.py`  
**Dependencies:** Task 3.1  
**Effort:** 2 hours

**Description:**
Set up `specs/` directory structure and templates.

**Subtasks:**
- [T] Create `specs/` directory if missing
- [T] Create `specs/README.md` explaining Spec → Plan → Tasks flow
- [T] Create `.specify/templates/` directory
- [T] Copy / create base templates: spec-template.md, plan-template.md, tasks-template.md
- [T] Do NOT create sample feature specs (per clarification Q4)
- [T] Do NOT delete or modify existing feature specs

**Acceptance Criteria:**
- ✅ specs/README.md explains SDD workflow and `/speckit.*` commands
- ✅ All templates have Clarifications, Acceptance Criteria, Task Dependencies sections
- ✅ Existing feature specs are never touched

---

### Task 3.4: Implement Agent Commands Setup
**File:** `src/specify_cli/sdd_bootstrap.py`  
**Dependencies:** Task 3.1  
**Effort:** 2 hours

**Description:**
Copy agent-specific command definitions to `.specify/agents/`.

**Subtasks:**
- [T] For each agent in AGENT_CONFIG:
  - [T] For each command (constitution, specify, clarify, plan, tasks, analyze, checklist, implement):
    - [T] Copy template from `templates/commands/` to `.specify/agents/`
    - [T] File naming: `.specify/agents/{agent_id}_{command_name}.md`
- [T] Skip files that already exist (idempotency)

**Acceptance Criteria:**
- ✅ All agent command files created
- ✅ Files are skipped if they already exist (no overwrites)
- ✅ AGENT_CONFIG is used as single source of truth for agent list

---

### Task 3.5: Implement Scripts Population
**File:** `src/specify_cli/sdd_bootstrap.py`  
**Dependencies:** Task 3.1  
**Effort:** 2 hours

**Description:**
Populate `.specify/scripts/` with helper scripts.

**Subtasks:**
- [T] Create `.specify/scripts/bash/` directory
- [T] Copy bash scripts: common.sh, create-new-feature.sh, setup-plan.sh from `scripts/bash/`
- [T] Create `.specify/scripts/powershell/` directory
- [T] Copy PowerShell scripts: common.ps1, create-new-feature.ps1, setup-plan.ps1 from `scripts/powershell/`
- [T] Ensure scripts are executable on POSIX systems (chmod +x)
- [T] Skip if files already exist

**Acceptance Criteria:**
- ✅ All scripts copied to correct locations
- ✅ Bash scripts are executable
- ✅ PowerShell scripts are present (executable on Windows)
- ✅ Existing scripts are never overwritten

---

### Task 3.6: Write Unit Tests for SDD Bootstrap
**File:** `tests/test_sdd_bootstrap.py`  
**Dependencies:** Tasks 3.1–3.5, 1.4  
**Effort:** 3 hours

**Description:**
Unit tests for SDD bootstrap operations.

**Test Cases:**
- [T] `test_create_constitution_new_project` – Constitution created with stack-specific principles
- [T] `test_create_constitution_existing_preserved` – Existing constitution is preserved
- [T] `test_setup_specs_directory` – specs/ and templates created
- [T] `test_setup_agent_commands` – Agent command files created
- [T] `test_setup_specify_scripts` – Script files created
- [T] `test_idempotent_bootstrap_first_run` – Bootstrap runs once successfully
- [T] `test_idempotent_bootstrap_second_run` – Running again creates no new files, no errors
- [T] `test_skip_existing_files` – Existing files are not overwritten

**Acceptance Criteria:**
- ✅ All tests pass
- ✅ Coverage > 85% for bootstrap module
- ✅ Idempotency verified

---

## PHASE 4: CLI Integration

### Task 4.1: Add `--warp-spec` Flag to `specify init`
**File:** `src/specify_cli/__init__.py`  
**Dependencies:** Tasks 1.1, 2.1, 3.1  
**Effort:** 1 hour

**Description:**
Add the `--warp-spec` command-line option to the init command.

**Subtasks:**
- [T] Add `warp_spec: bool = typer.Option(False, "--warp-spec", help="...")` parameter
- [T] Update docstring to document new option
- [T] Ensure backward compatibility: existing workflows unaffected when flag not used

**Acceptance Criteria:**
- ✅ Flag is recognized by CLI
- ✅ `specify init --help` shows the new option
- ✅ Default value is False
- ✅ Existing commands still work without the flag

---

### Task 4.2: Integrate Detection & Bootstrap into `init()`
**File:** `src/specify_cli/__init__.py`  
**Dependencies:** Task 4.1  
**Effort:** 3 hours

**Description:**
Integrate detection, WARP generation, and SDD bootstrap into the init workflow.

**Subtasks:**
- [T] Import detection, warp_generation, and sdd_bootstrap modules
- [T] After determining project_path, call `detect_project_stack(project_path)`
- [T] Call `detect_sdd_artifacts(project_path)` to determine SDD status
- [T] Decide whether to enable SDD pipeline:
  - If `--warp-spec` explicit: enable
  - If non-SDD project: enable
  - If SDD-enabled project: skip (unless --warp-spec)
- [T] Add tracker phases: "Detect project tech stack", "Generate WARP.md", "Bootstrap SDD artifacts"
- [T] Call WARP generation and bootstrap functions
- [T] Print summary of created/updated artifacts

**Acceptance Criteria:**
- ✅ Detection runs without errors
- ✅ WARP and SDD artifacts are created in correct locations
- ✅ Tracker shows progress for each phase
- ✅ Existing template download and git workflows still work

---

### Task 4.3: Implement Next Steps Summary Output
**File:** `src/specify_cli/__init__.py`  
**Dependencies:** Task 4.2  
**Effort:** 1.5 hours

**Description:**
Print user-friendly summary after SDD bootstrap completes.

**Subtasks:**
- [T] Create `print_sdd_next_steps(project_path, detected_stack)` function
- [T] Display created/updated artifacts (WARP.md, constitution, specs, etc.)
- [T] List next steps (review constitution, run `/speckit.specify`, etc.)
- [T] Display available `/speckit.*` commands
- [T] Use Rich formatting for clear, readable output

**Acceptance Criteria:**
- ✅ Output is formatted nicely and easy to read
- ✅ Lists all created artifacts
- ✅ Provides clear next steps
- ✅ Shows available commands

---

## PHASE 5: Testing

### Task 5.1: Create CLI Integration Test Suite
**File:** `tests/test_cli_integration.py`  
**Dependencies:** All previous tasks  
**Effort:** 3 hours

**Description:**
End-to-end CLI tests using Typer's CliRunner.

**Test Cases:**
- [T] `test_init_empty_dir_with_warp_spec` – `specify init . --here --warp-spec` in empty dir
- [T] `test_init_node_project_with_warp_spec` – Node.js project → WARP generated
- [T] `test_init_python_project_with_warp_spec` – Python project → WARP generated
- [T] `test_init_without_warp_spec_non_sdd_project` – Non-SDD project auto-enables SDD
- [T] `test_init_without_warp_spec_sdd_project` – SDD project skips bootstrap
- [T] `test_init_new_project_default` – `specify init my-project` still works as before
- [T] `test_init_idempotent` – Running twice produces identical results

**Acceptance Criteria:**
- ✅ All CLI tests pass
- ✅ WARP and SDD artifacts are created in correct locations
- ✅ Idempotency verified through CLI

---

### Task 5.2: Manual Validation on Real Sample Projects
**File:** Manual testing checklist  
**Dependencies:** All implementation tasks  
**Effort:** 4 hours

**Description:**
Manual testing on realistic sample projects.

**Test Scenarios:**
- [T] Sample Node.js project (express app with jest)
  - Run `specify init . --here --warp-spec`
  - Verify: WARP.md, constitution, specs, agents created
  - Verify: npm commands in WARP are correct
  - Run again: verify idempotency
  
- [T] Sample Python project (Flask with pytest)
  - Run `specify init . --here --warp-spec`
  - Verify: WARP.md, constitution, specs, agents created
  - Verify: pytest commands in WARP are correct
  - Run again: verify idempotency
  
- [T] Sample .NET project (ASP.NET Core with xunit)
  - Run `specify init . --here --warp-spec`
  - Verify: WARP.md, constitution, specs, agents created
  - Verify: dotnet test commands in WARP
  
- [T] Monorepo (Node + Python)
  - Run `specify init . --here --warp-spec`
  - Verify: WARP generated with highest-confidence stack
  - Verify: Falls back to generic if ambiguous

**Acceptance Criteria:**
- ✅ All sample projects handled correctly
- ✅ WARP files are valid Markdown
- ✅ Commands in WARP are accurate for each stack
- ✅ Idempotency holds across all scenarios

---

### Task 5.3: Performance Benchmarking
**File:** `tests/test_performance.py`  
**Dependencies:** All implementation tasks  
**Effort:** 1.5 hours

**Description:**
Verify performance meets NFR-3 targets.

**Benchmarks:**
- [T] Stack detection completes in < 1 second
- [T] WARP generation completes in < 2 seconds
- [T] Total SDD bootstrap completes in < 10 seconds

**Acceptance Criteria:**
- ✅ Detection: < 1 sec
- ✅ WARP generation: < 2 sec
- ✅ Bootstrap: < 10 sec
- ✅ Benchmarks documented

---

### Task 5.4: Validation Checklist & Sign-Off
**File:** `VALIDATION.md`  
**Dependencies:** All testing tasks  
**Effort:** 1 hour

**Description:**
Document validation results and sign-off.

**Checklist:**
- [T] All unit tests pass (detection, WARP, bootstrap)
- [T] All integration tests pass (CLI)
- [T] Manual validation on all stack types
- [T] Idempotency verified
- [T] Performance benchmarks met
- [T] No regressions to existing `specify init` workflows
- [T] Coverage > 85% for new modules

**Acceptance Criteria:**
- ✅ All checklist items completed
- ✅ Issues documented (if any)
- ✅ Ready for documentation & release

---

## PHASE 6: Documentation & Release

### Task 6.1: Update Project Documentation
**Files:** `README.md`, `docs/project-agnostic-sdd-init.md`  
**Dependencies:** All implementation tasks  
**Effort:** 2 hours

**Description:**
Update user-facing documentation.

**Subtasks:**
- [T] Update `README.md`: Add brief mention of project-agnostic SDD initialization
- [T] Create `docs/project-agnostic-sdd-init.md` with:
  - Overview of the feature
  - Usage examples for Node.js, Python, .NET, Go, Java, Rust
  - Explanation of `--warp-spec` flag
  - Example output and next steps
- [T] Update `README.md` to reference new doc

**Acceptance Criteria:**
- ✅ Documentation is clear and includes examples
- ✅ Links to new doc are correct
- ✅ Examples are accurate and tested

---

### Task 6.2: Update WARP Rules
**Files:** `WARP.md`, `src/specify_cli/WARP.md`  
**Dependencies:** All implementation tasks  
**Effort:** 1.5 hours

**Description:**
Document the new SDD bootstrap architecture in WARP rules.

**Subtasks:**
- [T] Update root `WARP.md`: Add "Project-Agnostic SDD Initialization" section
- [T] Update `src/specify_cli/WARP.md`: Document new modules (project_detection, warp_generation, sdd_bootstrap)
- [T] Add guidance for future changes: Keep AGENT_CONFIG, templates, and bootstrap in sync
- [T] Note that marker-based updates are used for WARP idempotency

**Acceptance Criteria:**
- ✅ WARP rules document the new architecture
- ✅ Future maintainers understand the design
- ✅ No contradictions with spec/plan

---

### Task 6.3: Bump Version & Update Changelog
**Files:** `pyproject.toml`, `CHANGELOG.md`  
**Dependencies:** All implementation tasks  
**Effort:** 1 hour

**Description:**
Update version number and release notes.

**Subtasks:**
- [T] Bump version in `pyproject.toml`: 0.0.22 → 0.1.0 (minor bump)
- [T] Add entry to `CHANGELOG.md`:
  - "Project-Agnostic SDD Initialization" heading
  - New `--warp-spec` flag
  - Auto-detection of tech stacks
  - WARP generation for root + subdirectories
  - SDD artifact bootstrap
  - Examples of usage

**Acceptance Criteria:**
- ✅ Version bumped to 0.1.0
- ✅ CHANGELOG entry is clear and comprehensive
- ✅ Release workflow can pick up new version

---

### Task 6.4: Test Full Release Workflow
**File:** Manual release testing  
**Dependencies:** Task 6.3  
**Effort:** 1.5 hours

**Description:**
Verify the complete release pipeline works.

**Subtasks:**
- [T] Push changes to a feature branch
- [T] Verify CI/linting passes
- [T] Merge to main (or simulate)
- [T] Verify release workflow creates version tag and GitHub Release
- [T] Verify template ZIPs include new modules (project_detection.py, etc.)
- [T] Test installing released version with `uv tool install`
- [T] Test `specify init` with new feature on fresh environment

**Acceptance Criteria:**
- ✅ CI/CD passes without errors
- ✅ Release artifacts created correctly
- ✅ New version installable and functional
- ✅ Documentation deployed

---

## Task Dependencies & Critical Path

```
1.1 → 1.2 → 1.3 → 1.4 → 1.5 (Detection)
      ↓           ↓
      2.1 ────→ 2.2 → 2.3 → 2.4 → 2.5 → 2.6 (WARP)
      ↓
      3.1 ────→ 3.2 → 3.3 → 3.4 → 3.5 → 3.6 (SDD Bootstrap)
      ↓
      4.1 ────→ 4.2 → 4.3 (CLI Integration)
      ↓
      5.1 → 5.2 → 5.3 → 5.4 (Testing)
      ↓
      6.1 → 6.2 → 6.3 → 6.4 (Documentation & Release)
```

**Critical Path:** 1.1–1.5 → 2.1–2.6 → 3.1–3.6 → 4.1–4.3 → 5.1–5.4 → 6.1–6.4

**Parallelizable Groups:** 
- 1.1–1.5 can be blocked and reviewed before 2.1 starts
- 2.1–2.6 can be blocked and reviewed before 3.1 starts
- 3.1–3.6 can be blocked and reviewed before 4.1 starts

---

## Success Criteria Checklist

- [ ] All unit tests pass (detection, WARP, bootstrap)
- [ ] All CLI integration tests pass
- [ ] Manual validation on Node, Python, .NET, Go, Java, Rust, generic projects
- [ ] Idempotency: running `specify init --warp-spec` twice produces identical results
- [ ] No regressions to existing `specify init` workflows
- [ ] Performance: detection < 1s, WARP gen < 2s, bootstrap < 10s
- [ ] WARP.md files follow all user constraints (prefix, no boilerplate, architecture overview)
- [ ] SDD artifacts (constitution, specs, templates, agents, scripts) created
- [ ] Documentation complete and examples accurate
- [ ] Version bumped, CHANGELOG updated
- [ ] Full release workflow tested and passes
- [ ] Code coverage > 85% for new modules

