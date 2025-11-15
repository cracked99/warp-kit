# Clarifications: Project-Agnostic WARP + SDD Initialization

This document captures answers to ambiguities and edge cases identified during spec refinement.

## Detection & Fallback Behavior

### Q1: What happens in a monorepo with multiple tech stacks?
**A:** The detection algorithm computes confidence scores for each stack. The highest-confidence stack is used for the root WARP. If multiple stacks have similar confidence (e.g., monorepo with 50% Node, 50% Python), the algorithm:
1. Weights primary build/config files (package.json, pyproject.toml) higher than tests
2. Selects the stack with the highest total confidence
3. Falls back to "generic" if no clear winner (confidence too low)

Users can then customize subdirectory WARPs manually if needed.

### Q2: What if a directory is completely empty or has only non-standard files (e.g., Dockerfile)?
**A:** The algorithm detects "generic" stack and generates minimal WARP guidance focused on SDD principles rather than specific build/test commands. Users can refine the WARP and specify their actual stack later.

### Q3: What test frameworks should be auto-detected?
**A:** For each stack:
- **Node.js:** jest, mocha, vitest, playwright, cypress
- **Python:** pytest, unittest
- **.NET:** xunit, nunit, mstest
- **Go:** testing (built-in)
- **Java:** junit, testng
- **Rust:** cargo test (built-in)

If multiple frameworks are detected in a single stack, the most prominent (by file count or config precedence) is used.

## SDD Artifact Behavior

### Q4: Should `specify init --warp-spec` create a sample feature spec by default?
**A:** **No.** Only create `specs/README.md` explaining the SDD workflow. Do not create `specs/example-feature/` or any working examples, as this may confuse users about what's their responsibility vs. what's boilerplate. If users want examples, they can reference external docs.

### Q5: When creating `memory/constitution.md`, should it be generic or stack-specific?
**A:** Stack-specific. For example:
- **Python projects:** Emphasize pytest, packaging discipline, virtual environments, type hints
- **Node.js projects:** Emphasize npm/yarn/pnpm practices, ESM/CommonJS alignment, test coverage
- **.NET projects:** Emphasize solution structure, NuGet practices, async patterns

All constitutions should still follow the same structure and core SDD principles.

### Q6: Should agent command definitions be copied or symlinked?
**A:** **Copy them.** Each project should have its own agent configs in `.specify/agents/` or similar, copied from this repo's templates. This makes projects self-contained and avoids path-dependency issues.

## Idempotency & Update Semantics

### Q7: If a user manually edits an auto-managed section of WARP.md (between markers), what happens on the next `--warp-spec` run?
**A:** The section is **regenerated from scratch**, replacing user edits. To prevent this:
1. Document clearly in the marker comment that the section is auto-managed
2. Show a warning/log message when regenerating: "Updated auto-managed WARP section. User edits between markers are not preserved."
3. Recommend users add custom sections outside the markers if they want to preserve edits

### Q8: Can `specify init --warp-spec` be run in a project that already has a fully-SDD structure?
**A:** **Yes, safely.** Because of marker-based updates:
- Existing specs/plans/tasks are never touched
- Constitution is preserved; new notes appended only if they don't exist
- WARP sections between markers are refreshed (preserving marker structure)
- No duplicate sections created

### Q9: What if someone has manually created `.specify/` or `specs/` directories with custom content?
**A:** Respect existing directories:
- Do not delete or overwrite `.specify/` subdirectories
- Do not delete feature directories under `specs/`
- Only add missing boilerplate (README, templates, scripts) if they don't exist
- Log/print which files were skipped because they already exist

## User Interaction & Automation

### Q10: Should `specify init --warp-spec` prompt before modifying an existing non-Spec-Kit project?
**A:** **No automatic prompt by default.** The flag `--warp-spec` is explicit intent. For added safety:
1. Log clearly what will be created/modified
2. Run in dry-run mode first (optional future enhancement)
3. Print summary at the end showing what was changed

If modifying an existing **SDD project**, use idempotent semantics (no prompt needed because no specs/plans are overwritten).

### Q11: Should the command list next steps (e.g., "Run `/speckit.specify` next")?
**A:** **Yes.** After completion, print:
```
✅ Spec-Driven Development initialized!

Created/Updated:
  • WARP.md (root guidance and tech stack specifics)
  • memory/constitution.md (project principles)
  • specs/ (specifications framework)
  • .specify/ (SDD tooling)

Next Steps:
  1. Review memory/constitution.md to refine project principles
  2. Use /speckit.specify to create your first feature spec
  3. Use /speckit.plan to design implementation
  4. Use /speckit.tasks to break down work
  5. Use /speckit.implement to execute tasks

Available /speckit.* commands:
  /speckit.specify   - Create a feature specification
  /speckit.clarify   - Clarify ambiguous requirements
  /speckit.plan      - Create technical implementation plan
  /speckit.tasks     - Break plan into actionable tasks
  /speckit.implement - Execute implementation tasks
  /speckit.analyze   - Cross-check artifact consistency
  /speckit.checklist - Generate quality checklists
```

## WARP.md Content

### Q12: For subdirectory WARPs (e.g., `src/WARP.md`), what level of detail is appropriate?
**A:** Follow this pattern:
- **Concise.** 1-2 paragraphs per section; avoid verbosity
- **Actionable.** Point to specific files/patterns (e.g., "Controllers in `src/api/controllers`")
- **Linked.** Reference root `WARP.md` for SDD rules rather than repeating them
- **Example:** For `tests/WARP.md` in a pytest project:

```markdown
# WARP.md – Testing

Tests in this directory use [pytest](https://pytest.org/).

## Running Tests

Single test:
\`\`\`bash
pytest tests/test_foo.py::test_example
\`\`\`

All tests:
\`\`\`bash
pytest
\`\`\`

See root [`WARP.md`](../WARP.md) for SDD principles and overall project guidance.
```

### Q13: Should root WARP.md mention every subdirectory or just key ones?
**A:** Only key ones. Mention: `src/`, `tests/`, `.github/`, `docs/`, `scripts/` if they exist. Skip less common directories (e.g., `build/`, `dist/`, `node_modules/`).

## Backward Compatibility

### Q14: If a user runs the old `specify init my-project --ai claude` without `--warp-spec`, what happens?
**A:** Depends on context:
- **For new empty directories:** SDD + WARP setup is auto-enabled (desired: all new projects are SDD-ready by default)
- **For non-SDD existing directories:** SDD setup is auto-enabled (desired: retrofit capability)
- **For already-SDD projects:** Skip SDD setup (no-op, safe)

Existing template download, agent selection, and git init workflows are **always** preserved.

## Testing & Validation

### Q15: How should tests validate "idempotency"?
**A:** For each test scenario:
1. Run `specify init --warp-spec` once → capture created files and their content
2. Run `specify init --warp-spec` again → capture created files and their content
3. Assert: content is identical (no duplicates, no drift)
4. Assert: only auto-managed sections changed (if at all)
5. Assert: specs/plans/tasks were never touched

### Q16: Should we test against real projects or synthetic fixtures?
**A:** Both:
- **Synthetic fixtures:** Minimal, controlled test cases (e.g., a directory with only `package.json`)
- **Real projects:** Clone or use open-source repos (e.g., a small Node.js lib, Python package) to validate realistic scenarios

## Version & Documentation

### Q17: What version bump is appropriate?
**A:** **Minor bump** (0.0.22 → 0.1.0) because:
- New public-facing feature: `--warp-spec` flag
- Enhanced `specify init` behavior
- No breaking changes to existing workflows

### Q18: Where should the feature be documented?
**A:** 
- **README.md:** Brief mention that Specify now supports project-agnostic SDD initialization
- **docs/project-agnostic-sdd-init.md:** New guide with examples for Node, Python, .NET, etc.
- **AGENTS.md:** No changes needed (agent config remains same)
- **WARP.md (root):** Note that the SDD bootstrap now handles arbitrary projects

