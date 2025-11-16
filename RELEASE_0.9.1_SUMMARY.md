# Release 0.9.1 Summary

**Release Date:** 2025-11-16  
**Version:** 0.9.1  
**Git Tag:** v0.9.1  
**Status:** ✅ Released and Installed

---

## What's New

### Feature: Automatic Warp-Space Initialization on `--here`

Users running `specify init --here` in existing projects now automatically get a complete Spec-Driven Development (SDD) infrastructure without needing additional flags or manual setup.

#### Key Improvements

✅ **Automatic SDD Setup** - `.warp-space` directory structure is now automatically created when using `--here`  
✅ **Better Existing Project Support** - Existing projects can now be bootstrapped with full SDD capabilities  
✅ **Reduced Friction** - Users don't need to remember `--warp-spec` flag for existing projects  
✅ **Complete Infrastructure** - All templates, commands, and configuration created automatically  

---

## Technical Changes

### 1. CLI Integration Update
- **File:** `src/specify_cli/__init__.py` (line 1166)
- **Change:** SDD initialization now triggered by both `--warp-spec` and `--here` flags
- **Impact:** Automatic warp-space setup for existing projects

### 2. WARP Generation Fix
- **File:** `src/specify_cli/cli_integration.py` (lines 15, 116-126)
- **Changes:**
  - Added `upsert_warp` import
  - Fixed function call signatures
  - Corrected parameter ordering
- **Impact:** Proper WARP.md file generation

### 3. Test Suite Update
- **File:** `tests/test_sdd_bootstrap.py`
- **Changes:**
  - Updated all tests for `.warp-space` paths
  - Updated function imports and calls
  - Enhanced integration tests
- **Impact:** Reliable test coverage for new functionality

---

## Release Artifacts

### Files Modified
1. ✅ `pyproject.toml` - Version bumped to 0.9.1
2. ✅ `CHANGELOG.md` - Release notes added
3. ✅ `src/specify_cli/__init__.py` - CLI trigger fix
4. ✅ `src/specify_cli/cli_integration.py` - WARP generation fix
5. ✅ `tests/test_sdd_bootstrap.py` - Test suite updates

### Documentation Created
1. 📄 `WARP_SPACE_SETUP_CHANGES.md` - Detailed change descriptions
2. 📄 `IMPLEMENTATION_NOTES.md` - Technical architecture
3. 📄 `RELEASE_0.9.1_SUMMARY.md` - This file

---

## Installation

### Uninstall Previous Version
```bash
uv tool uninstall warp-kit
```

### Install New Version
```bash
uv tool install warp-kit --from git+https://github.com/cracked99/warp-kit.git@v0.9.1
```

### Verify Installation
```bash
warp-kit version
# Expected: CLI Version 0.9.1
```

---

## GitHub Release

**Tag:** v0.9.1  
**Branch:** feature/add-warp-sdd-rules  
**Repository:** https://github.com/cracked99/warp-kit

### Release Notes

Automatic `.warp-space` initialization when using `specify init --here` command:
- Automatically initialize `.warp-space` when using `'specify init --here'`
- Fixed WARP generation function call signatures
- Updated test suite for `.warp-space` directory structure
- Added comprehensive documentation of changes
- Fixes initialization of SDD infrastructure in existing projects

---

## Usage Example

### Before (0.9.0)
```bash
# Users had to explicitly add --warp-spec
$ specify init --here --warp-spec
```

### After (0.9.1)
```bash
# Just use --here, warp-space is automatic
$ specify init --here
```

---

## Backward Compatibility

✅ All changes are backward compatible:
- Existing `.specify` projects continue to work
- The `--warp-spec` flag still works (becomes redundant)
- No breaking changes to public APIs
- Existing WARP.md files not overwritten unnecessarily

---

## Testing

All tests have been updated and verified:
- ✅ Constitution creation tests
- ✅ Specs directory setup tests
- ✅ Template creation tests
- ✅ Agent commands setup tests
- ✅ Script setup tests
- ✅ Full bootstrap integration tests
- ✅ Idempotency verification

---

## Commit Information

**Commit Hash:** 919bd91  
**Message:** Release 0.9.1: Automatic warp-space initialization for --here command

**Changes:** 7 files changed, 462 insertions(+), 46 deletions(-)

---

## Installation Status

✅ **Installation Successful**

```
CLI Version:      0.9.1
Template Version: 0.8.0
Released:         2025-11-16
Python:           3.13.7
Platform:         Linux
```

---

## Next Steps

1. ✅ Release created and published to GitHub
2. ✅ Version installed via uv
3. 📝 Share release notes with team
4. 📝 Update documentation websites
5. 📝 Monitor for feedback on new automatic initialization

---

## Support

For issues or questions about this release, please refer to:
- 📖 `WARP_SPACE_SETUP_CHANGES.md` - Detailed technical changes
- 📖 `IMPLEMENTATION_NOTES.md` - Architecture and design
- 📖 GitHub Issues: https://github.com/cracked99/warp-kit/issues
