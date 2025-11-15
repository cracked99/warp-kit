# Implementation Plan: Project-Agnostic WARP + SDD Initialization

## Overview

This plan outlines the technical implementation strategy to enable `specify init` to autonomously detect project technology stacks and bootstrap complete SDD + WARP architectures. The implementation spans three new modules, CLI integration, comprehensive testing, and documentation updates.

## Architecture & Design

### 1. Detection Subsystem (`src/specify_cli/project_detection.py`)

**Purpose:** Autonomously detect project technology stack and infer development practices.

**Key Components:**

#### Data Structure: `DetectedStack`
```python
@dataclass
class DetectedStack:
    id: str  # "node", "python", "dotnet", "go", "java", "rust", "generic"
    name: str  # Display name, e.g., "Node.js / TypeScript"
    confidence_score: float  # 0.0 to 1.0
    signals: List[str]  # File/directory patterns that triggered detection
    test_framework: Optional[str]  # Inferred test framework
    source_dir: Optional[str]  # Primary source directory (e.g., "src")
    test_dir: Optional[str]  # Primary test directory (e.g., "tests")
    commands: Dict[str, str]  # "build", "lint", "test_all", "test_single" templates
    ci_present: bool  # Whether .github/workflows exists
```

#### Detection Algorithm

```
FOR each stack in [node, python, dotnet, go, java, rust]:
    score = 0
    signals = []
    
    FOR each file_pattern in stack.primary_signals:
        IF file_exists(root / file_pattern):
            score += weight.high
            signals.append(file_pattern)
    
    FOR each dir_pattern in directory_heuristics:
        IF dir_exists(root / dir_pattern):
            score += weight.low
            signals.append(dir_pattern)
    
    stack.confidence_score = score

winner = stack_with_max(scores)
IF winner.confidence_score < MIN_THRESHOLD:
    winner = "generic"

RETURN winner
```

**Stack-Specific Signal Weights:**

| Stack | Primary Signals | Weight | Secondary (Dirs) |
|-------|-----------------|--------|------------------|
| **Node.js** | package.json, yarn.lock, pnpm-lock.yaml | 0.7 | node_modules/, tsconfig.json |
| **Python** | pyproject.toml, requirements.txt, setup.py, poetry.lock, Pipfile | 0.7 | venv/, .venv/, src/, tests/ |
| **.NET** | *.csproj, *.sln, Directory.Build.props | 0.7 | bin/, obj/ |
| **Go** | go.mod, go.sum | 0.7 | vendor/ |
| **Java** | pom.xml, build.gradle, .gradle/ | 0.7 | target/, build/ |
| **Rust** | Cargo.toml | 0.7 | target/ |
| **Generic** | (fallback) | 0.0 | N/A |

**Test Framework Detection:**
- Scan lock files, import statements, and config files for test framework names
- Examples: pytest (Python), jest/mocha (Node.js), xunit (.NET), junit (Java)

#### Public Interface

```python
def detect_project_stack(root: Path) -> DetectedStack:
    """Detect the tech stack and infer development practices."""
    
def detect_sdd_artifacts(root: Path) -> SDDStatus:
    """
    Check for existing SDD artifacts.
    Returns: SDDStatus with flags for constitution, specs, .specify, WARP presence.
    """

@dataclass
class SDDStatus:
    has_constitution: bool
    has_specs: bool
    has_specify_dir: bool
    has_warp_root: bool
    has_warp_subdirs: Dict[str, bool]  # "src", "tests", ".github", etc.
    
    @property
    def is_sdd_enabled(self) -> bool:
        """True if at least constitution + specs are present."""
```

### 2. WARP Generation (`src/specify_cli/warp_generation.py`)

**Purpose:** Generate or update WARP.md files (root + subdirectories) based on detected stack and project state.

**Key Components:**

#### Root WARP Template Logic

```python
def generate_root_warp(
    stack: DetectedStack,
    project_root: Path,
    existing_warp: Optional[str] = None
) -> str:
    """Generate root WARP.md content."""
    
    # Always start with required prefix
    content = [
        "# WARP.md",
        "",
        "This file provides guidance to WARP (warp.dev) when working with code in this repository.",
        ""
    ]
    
    # Section 1: Project Overview
    readme_excerpt = extract_readme_summary(project_root)
    if readme_excerpt:
        content.append("## Project Overview")
        content.append("")
        content.append(readme_excerpt)
        content.append("")
    
    # Section 2: Technology Stack
    content.extend(generate_tech_stack_section(stack))
    
    # Section 3: Development Commands
    content.extend(generate_commands_section(stack))
    
    # Section 4: Architecture Overview
    content.extend(generate_architecture_section(project_root, stack))
    
    # Section 5: Agent-Specific Rules
    content.extend(generate_agent_rules_section(project_root))
    
    # Section 6: Spec-Driven Development & WARP Usage (AUTO-MANAGED)
    content.append("")
    content.append("<!-- specify-init:warp-managed:start -->")
    content.extend(generate_sdd_section(stack))
    content.append("<!-- specify-init:warp-managed:end -->")
    
    return "\n".join(content)
```

#### Subdirectory WARP Templates

For each key subdirectory (src/, tests/, .github/, docs/, scripts/), generate focused guidance:

**`src/WARP.md` (Code Organization):**
```markdown
# WARP.md – Source Code

Code in this directory is organized using [architecture pattern].

[2-3 paragraphs about how code is laid out, e.g., src/api/, src/domain/, src/infra/]

## Main Entrypoint
[src/main.py | src/index.ts | etc.]

See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.
```

**`tests/WARP.md` (Testing):**
```markdown
# WARP.md – Testing

Tests use [framework name] and are located in this directory.

## Running Tests

Run all tests:
\`\`\`bash
[test command from DetectedStack.commands["test_all"]]
\`\`\`

Run a single test:
\`\`\`bash
[test command from DetectedStack.commands["test_single"]]
\`\`\`

## Test Conventions
- Naming: [pattern]
- Location: [pattern]

See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.
```

Similarly for `.github/`, `docs/`, `scripts/`.

#### Update Semantics

```python
def upsert_warp(
    path: Path,
    new_content: str,
    auto_managed: bool = True
) -> (bool, str):
    """
    Create or update WARP file with idempotent semantics.
    
    Returns: (was_created: bool, action: str)
    """
    
    if not path.exists():
        # First creation: write full content
        path.write_text(new_content)
        return (True, "created")
    
    existing = path.read_text()
    
    if "<!-- specify-init:warp-managed:" not in existing:
        # No markers: append new SDD section
        if not existing.endswith("\n\n"):
            existing += "\n\n"
        
        sdd_section = extract_sdd_section(new_content)
        existing += "<!-- specify-init:warp-managed:start -->\n"
        existing += sdd_section
        existing += "\n<!-- specify-init:warp-managed:end -->\n"
        
        path.write_text(existing)
        return (False, "appended_sdd_section")
    else:
        # Has markers: replace only marked content
        before_marker = existing.split("<!-- specify-init:warp-managed:start -->")[0]
        after_marker = existing.split("<!-- specify-init:warp-managed:end -->")[1]
        
        sdd_section = extract_sdd_section(new_content)
        
        result = (
            before_marker
            + "<!-- specify-init:warp-managed:start -->\n"
            + sdd_section
            + "\n<!-- specify-init:warp-managed:end -->"
            + after_marker
        )
        
        if result != existing:
            path.write_text(result)
            return (False, "updated_sdd_section")
        else:
            return (False, "no_changes")
```

### 3. SDD Bootstrap (`src/specify_cli/sdd_bootstrap.py`)

**Purpose:** Create or augment SDD artifacts (constitution, specs, agent configs, scripts).

**Key Components:**

#### Constitution Generation

```python
def create_or_update_constitution(
    project_root: Path,
    stack: DetectedStack,
    sdd_status: SDDStatus
) -> (bool, str):
    """Create or update memory/constitution.md"""
    
    const_path = project_root / "memory" / "constitution.md"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "memory").mkdir(exist_ok=True)
    
    if const_path.exists():
        # Preserve existing; optionally append stack-specific section
        # (implementation detail: check if stack notes already present)
        return (False, "preserved")
    else:
        # Create from template, parameterized by stack
        template = load_constitution_template(stack.id)
        content = template.format(
            stack_name=stack.name,
            test_framework=stack.test_framework or "testing",
            has_ci="✓" if stack.ci_present else "✗"
        )
        const_path.write_text(content)
        return (True, "created")
```

#### Specs Directory Setup

```python
def setup_specs_directory(project_root: Path) -> List[(bool, str)]:
    """Ensure specs/ directory and boilerplate are in place."""
    
    specs_dir = project_root / "specs"
    specs_dir.mkdir(exist_ok=True)
    
    actions = []
    
    # Create README if missing
    readme_path = specs_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(SPECS_README_TEMPLATE)
        actions.append((True, "created_specs_readme"))
    else:
        actions.append((False, "specs_readme_exists"))
    
    # Create .specify/ templates if missing
    templates_dir = project_root / ".specify" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    for template_file in ["spec-template.md", "plan-template.md", "tasks-template.md"]:
        template_path = templates_dir / template_file
        if not template_path.exists():
            template_path.write_text(load_template(template_file))
            actions.append((True, f"created_{template_file}"))
        else:
            actions.append((False, f"{template_file}_exists"))
    
    return actions
```

#### Agent Commands Setup

```python
def setup_agent_commands(project_root: Path) -> List[(bool, str)]:
    """Copy agent command definitions to .specify/agents/"""
    
    agents_dir = project_root / ".specify" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    
    actions = []
    
    for agent_id, agent_config in AGENT_CONFIG.items():
        # For each agent, copy its command files
        for command_name in [
            "constitution", "specify", "clarify", "plan", 
            "tasks", "analyze", "checklist", "implement"
        ]:
            target_file = agents_dir / f"{agent_id}_{command_name}.md"
            
            if not target_file.exists():
                source_template = load_agent_command_template(agent_id, command_name)
                target_file.write_text(source_template)
                actions.append((True, f"created_{agent_id}_{command_name}"))
            else:
                actions.append((False, f"{agent_id}_{command_name}_exists"))
    
    return actions
```

#### Scripts Population

```python
def setup_specify_scripts(project_root: Path) -> List[(bool, str)]:
    """Copy helper scripts to .specify/scripts/"""
    
    scripts_dir = project_root / ".specify" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    actions = []
    
    # Copy bash scripts
    bash_dir = scripts_dir / "bash"
    bash_dir.mkdir(exist_ok=True)
    for script in ["common.sh", "create-new-feature.sh", "setup-plan.sh"]:
        # Copy from this repo's scripts/bash/
        ...
    
    # Copy PowerShell scripts
    ps_dir = scripts_dir / "powershell"
    ps_dir.mkdir(exist_ok=True)
    for script in ["common.ps1", "create-new-feature.ps1", "setup-plan.ps1"]:
        # Copy from this repo's scripts/powershell/
        ...
    
    return actions
```

### 4. CLI Integration (`src/specify_cli/__init__.py`)

**Purpose:** Integrate detection and bootstrap into the existing `specify init` command.

**Changes to `init()` function:**

```python
@app.command()
def init(
    project_name: str = typer.Argument(...),
    # ... existing options ...
    warp_spec: bool = typer.Option(
        False, 
        "--warp-spec",
        help="Autonomously detect tech stack and bootstrap WARP + SDD artifacts"
    ),
):
    """Initialize a new Specify project or add WARP + SDD to existing project."""
    
    # ... existing setup code ...
    
    # NEW: Detect project stack and SDD status
    from .project_detection import detect_project_stack, detect_sdd_artifacts
    from .warp_generation import generate_root_warp, upsert_warp
    from .sdd_bootstrap import create_or_update_constitution, setup_specs_directory
    
    detected_stack = detect_project_stack(project_path)
    sdd_status = detect_sdd_artifacts(project_path)
    
    # Decide whether to enable SDD pipeline
    enable_sdd = False
    if warp_spec:
        enable_sdd = True
    elif not sdd_status.is_sdd_enabled:
        enable_sdd = True  # Auto-enable for non-SDD projects
    
    if enable_sdd:
        tracker.add("detect-stack", "Detect project technology stack")
        tracker.complete("detect-stack", detected_stack.name)
        
        tracker.add("warp-gen", "Generate WARP.md guidance")
        # ... call warp generation ...
        tracker.complete("warp-gen", "created/updated")
        
        tracker.add("sdd-bootstrap", "Bootstrap Spec-Driven Development artifacts")
        # ... call SDD bootstrap ...
        tracker.complete("sdd-bootstrap", "completed")
    
    # ... rest of existing code ...
    
    # NEW: Print next steps summary
    if enable_sdd:
        print_sdd_next_steps(project_path, detected_stack)
```

## Implementation Phases

### Phase 1: Detection Module (Days 1-2)
- Implement `project_detection.py`
- Unit tests for each supported stack
- Edge case handling (monorepos, empty dirs, ambiguous stacks)

### Phase 2: WARP Generation (Days 2-3)
- Implement `warp_generation.py`
- Root WARP templates for each stack
- Subdirectory WARP generators
- Update semantics with marker-based merging
- Unit tests for WARP generation and idempotency

### Phase 3: SDD Bootstrap (Days 3-4)
- Implement `sdd_bootstrap.py`
- Constitution template generation
- Specs directory setup
- Agent command copying
- Script population
- Unit tests

### Phase 4: CLI Integration (Day 4-5)
- Integrate detection + bootstrap into `init()`
- Add `--warp-spec` flag
- Add tracker phases
- Print next steps summary
- Manual testing

### Phase 5: Testing & Validation (Days 5-6)
- Create test fixtures for each stack
- Pytest integration tests
- CLI integration tests via Typer's CliRunner
- Idempotency validation
- Manual validation on real projects

### Phase 6: Documentation & Release (Day 6-7)
- Update README.md
- Create docs/project-agnostic-sdd-init.md guide
- Update WARP.md and src/specify_cli/WARP.md
- Bump version in pyproject.toml
- Update CHANGELOG.md
- Test full release workflow

## Critical Design Decisions

1. **Detection Confidence Scoring:** Highest-confidence match wins; falls back to generic if low confidence
2. **WARP Marker-Based Updates:** Allows safe re-running without duplicates
3. **Idempotent Operations:** All bootstrap actions check for existence before creating
4. **Non-Destructive Merging:** Existing user specs/plans/tasks are never touched
5. **Backward Compatibility:** Existing `specify init` workflows unaffected unless `--warp-spec` or non-SDD auto-trigger

## Success Criteria

- ✅ Auto-detection accurately identifies Node.js, Python, .NET, Go, Java, Rust, and generic stacks
- ✅ Generated WARP.md follows all user constraints (prefix, no boilerplate, big-picture architecture)
- ✅ SDD artifacts (constitution, specs, templates, agents, scripts) are created and idempotent
- ✅ `--warp-spec` flag works for new and existing projects
- ✅ Running `specify init --warp-spec` twice produces identical results (idempotency)
- ✅ Existing specs/plans/tasks are never overwritten
- ✅ All tests pass (unit, integration, CLI)
- ✅ Manual validation on sample projects confirms expected behavior
- ✅ Documentation is complete and examples are accurate

## Data Flow Diagram

```
specify init --warp-spec [project-path]
    │
    ├─→ detect_project_stack(path)
    │   └─→ returns DetectedStack (id, name, confidence, signals, commands, etc.)
    │
    ├─→ detect_sdd_artifacts(path)
    │   └─→ returns SDDStatus (has_constitution, has_specs, has_warp, etc.)
    │
    ├─→ generate_root_warp(stack, path)
    │   └─→ upsert_warp(WARP.md, content)
    │
    ├─→ generate_subdir_warps(stack, path)
    │   ├─→ upsert_warp(src/WARP.md, ...)
    │   ├─→ upsert_warp(tests/WARP.md, ...)
    │   └─→ upsert_warp(...WARP.md, ...)
    │
    ├─→ create_or_update_constitution(stack, sdd_status)
    │
    ├─→ setup_specs_directory(path)
    │
    ├─→ setup_agent_commands(path)
    │
    ├─→ setup_specify_scripts(path)
    │
    └─→ print_sdd_next_steps(path, stack)
```

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Over-eager WARP generation overwrites user content | Use marker-based updates; only auto-managed sections regenerated |
| Detection fails on unusual projects | Fallback to "generic" stack; users can manually refine |
| Idempotency breaks on partial failures | All operations check for existence; safe to re-run |
| Breaking existing workflows | Auto-detection only triggers for non-SDD projects unless `--warp-spec` explicit |
| Performance degradation | Stack detection < 1 sec, WARP gen < 2 sec, total bootstrap < 10 sec |

