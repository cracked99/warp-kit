# Warp-Space Setup Changes - `specify init --here`

## Summary

Implemented comprehensive changes to ensure that `.warp-space` directory structure is properly created and initialized when using the `specify init --here` command, ensuring users have a complete Spec-Driven Development environment.

## Changes Made

### 1. CLI Integration (`src/specify_cli/__init__.py`)

**Change:** Modified SDD initialization trigger to also run when `--here` flag is used

**File:** `src/specify_cli/__init__.py` (line 1166)

**Before:**
```python
if run_sdd_init_hook and warp_spec:
```

**After:**
```python
# Ensure SDD (warp-space) is initialized when explicitly requested or when using --here
if run_sdd_init_hook and (warp_spec or here):
```

**Impact:** Users now automatically get warp-space initialized when running `specify init --here`, without needing to explicitly pass `--warp-spec` flag.

---

### 2. CLI Integration - WARP Generation Fix (`src/specify_cli/cli_integration.py`)

**Changes:**
1. Added `upsert_warp` import from warp_generation module
2. Fixed function call signatures for `generate_root_warp` and `generate_subdir_warps`

**File:** `src/specify_cli/cli_integration.py` (lines 15, 116-126)

**Before:**
```python
from .warp_generation import generate_root_warp, generate_subdir_warps

# ...in run_sdd_initialization():
warp_path = generate_root_warp(project_root, detected_stack, sdd_status)
subdirs_created = generate_subdir_warps(project_root, detected_stack)
```

**After:**
```python
from .warp_generation import generate_root_warp, generate_subdir_warps, upsert_warp

# ...in run_sdd_initialization():
warp_content = generate_root_warp(detected_stack, project_root)
warp_path = project_root / "WARP.md"
was_created, action = upsert_warp(warp_path, warp_content)
if was_created:
    result.warp_created = True
else:
    result.warp_updated = True

subdirs_created = generate_subdir_warps(detected_stack, project_root)
```

**Impact:** Ensures WARP.md files are properly generated and upserted with correct parameter order.

---

### 3. Test Suite Updates (`tests/test_sdd_bootstrap.py`)

**Changes:** Updated all test references to use `.warp-space` instead of legacy `.specify` paths

**Key Updates:**

#### A. Import Statements
```python
from specify_cli.sdd_bootstrap import (
    create_warpspace,
    create_or_update_constitution,
    setup_specs_directory,
    setup_agent_commands,
    setup_warp_space_scripts,
    setup_warp_space_config,
)
```

#### B. Path Corrections
Updated all test assertions to use correct `.warp-space` paths:
- Constitution: `.warp-space/memory/constitution.md` (was: `memory/constitution.md`)
- Templates: `.warp-space/templates/` (was: `.specify/templates/`)
- Commands: `.warp-space/commands/` (was: `.specify/agents/`)
- Scripts: `.warp-space/scripts/` (was: `.specify/scripts/`)

#### C. Function Name Updates
- `setup_specify_scripts` → `setup_warp_space_scripts`
- Added calls to `create_warpspace()` and `setup_warp_space_config()`

#### D. Integration Test Update
```python
def test_full_bootstrap_creates_structure(temp_project_root, sample_stack, sample_sdd_status):
    """Test that running all bootstrap functions creates expected structure."""
    # Run all bootstrap functions
    create_warpspace(temp_project_root)
    create_or_update_constitution(temp_project_root, sample_stack, sample_sdd_status)
    setup_specs_directory(temp_project_root)
    setup_agent_commands(temp_project_root)
    setup_warp_space_scripts(temp_project_root)
    setup_warp_space_config(temp_project_root)
    
    # Verify correct directory structure
    expected_dirs = [
        ".warp-space/memory",
        "specs",
        ".warp-space/templates",
        ".warp-space/commands",
        ".warp-space/scripts/bash",
        ".warp-space/scripts/powershell",
    ]
    
    expected_files = [
        ".warp-space/Warp-space.md",
        ".warp-space/memory/constitution.md",
        "specs/README.md",
        ".warp-space/templates/spec-template.md",
        ".warp-space/templates/plan-template.md",
        ".warp-space/templates/tasks-template.md",
        ".warp-space/scripts/bash/README.md",
        ".warp-space/scripts/powershell/README.md",
    ]
```

---

## Directory Structure Created

When users run `specify init --here`, the following complete structure is now created:

```
.warp-space/
├── Warp-space.md                    # Single source of truth for SDD
├── memory/
│   └── constitution.md              # Project principles & quality standards
├── templates/
│   ├── spec-template.md             # Feature specification template
│   ├── plan-template.md             # Implementation plan template
│   ├── tasks-template.md            # Task breakdown template
│   ├── agent-file-template.md       # Agent context template
│   └── checklist-template.md        # Quality checklist template
├── commands/
│   ├── constitution.md              # /speckit.constitution command
│   ├── specify.md                   # /speckit.specify command
│   ├── clarify.md                   # /speckit.clarify command
│   ├── plan.md                      # /speckit.plan command
│   ├── tasks.md                     # /speckit.tasks command
│   ├── implement.md                 # /speckit.implement command
│   ├── analyze.md                   # /speckit.analyze command
│   ├── checklist.md                 # /speckit.checklist command
│   └── taskstoissues.md             # /speckit.taskstoissues command
├── scripts/
│   ├── bash/
│   │   └── README.md                # Bash helper scripts
│   └── powershell/
│       └── README.md                # PowerShell helper scripts
└── vscode-settings.json             # VS Code chat recommendations

specs/
└── README.md                        # SDD workflow guidance
```

---

## Workflow Impact

### Before
Users running `specify init --here` would get:
- Basic project files and structure
- Agent-specific command definitions (from template)
- No automatic warp-space initialization
- Users had to manually add `--warp-spec` or manually create `.warp-space` structure

### After
Users running `specify init --here` now get:
- Complete `.warp-space` directory structure
- Constitution with stack-specific principles
- All SDD templates and command definitions
- Ready-to-use specs/ directory
- Complete helper scripts framework
- Immediate ability to use `/speckit.*` commands

---

## Testing

All tests have been updated to verify:
1. `.warp-space` directory is created correctly
2. Constitution is properly stored in `.warp-space/memory/`
3. Templates are stored in `.warp-space/templates/`
4. Command definitions are in `.warp-space/commands/`
5. Scripts are organized in `.warp-space/scripts/{bash,powershell}/`
6. Full bootstrap creates complete SDD structure
7. All functions are idempotent (safe to run multiple times)

---

## Backward Compatibility

These changes maintain backward compatibility:
- Existing projects with `.specify` are not affected
- The SDD detection system recognizes both `.warp-space` and `.specify`
- New projects use the standard `.warp-space` structure
- Existing `--warp-spec` flag continues to work

---

## Files Modified

1. `src/specify_cli/__init__.py` - CLI initialization trigger
2. `src/specify_cli/cli_integration.py` - WARP generation fix
3. `tests/test_sdd_bootstrap.py` - Test suite updates for `.warp-space`

## Related Files (No Changes, Already Correct)

- `src/specify_cli/sdd_bootstrap.py` - Already uses `.warp-space`
- `src/specify_cli/warp_generation.py` - Already properly implemented
- `src/specify_cli/project_detection.py` - Already supports detection
- `src/specify_cli/init_hook.py` - Already properly implemented
