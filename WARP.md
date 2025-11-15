# WARP.md – Spec Kit & Specify CLI

**This project follows Spec-Driven Development (SDD).** Warp agents MUST treat the global rule **"Spec-Driven Development (SDD) – Global Workflow"** as the baseline. This `WARP.md` provides spec-kit-specific specialization.

---

## Project Overview

**Spec Kit** is an open-source toolkit that implements Spec-Driven Development. It consists of:

- **Specify CLI** – A bootstrapper that initializes SDD projects for 15+ AI coding assistants (Claude Code, Copilot, Cursor, Gemini CLI, Windsurf, etc.).
- **Templates & Scripts** – SDD artifact templates, agent-specific command definitions, and helper automation.
- **Documentation** – Comprehensive guides on SDD methodology and Spec Kit usage.

This project demonstrates how SDD works in practice and enables others to use SDD in their own projects.

### Project Structure & SDD Artifacts

| Directory | Role in SDD | Purpose |
|-----------|------------|---------|
| `memory/constitution.md` | Constitution | Project principles, quality bars, design constraints |
| `specs/<feature>/` | Spec, Plan, Tasks | Feature specifications, implementation plans, task breakdowns |
| `src/specify_cli/` | Implementation | CLI logic, agent configuration, template scaffolding |
| `templates/` | Implementation | SDD templates and agent-specific command definitions |
| `docs/` | Documentation | User guides, how-to docs, and conceptual explanations |
| `.github/` | Automation | CI/CD workflows, release packaging, and tooling |
| `scripts/` | Implementation | Cross-platform helper scripts for releases and automation |

---

## Key SDD Principles for This Project

### 1. Specifications Are Canonical

- The `memory/constitution.md` file encodes project-wide principles (code quality, testing standards, user experience, constraints).
- Feature work lives in `specs/<feature>/` with:
  - `spec.md` – WHAT the feature should do and WHY.
  - `plan.md` – HOW to implement it (architecture, data models, APIs).
  - `tasks.md` – Ordered, traceable implementation tasks.
- **Code must conform to specs, not the other way around.** When code and specs disagree, update the specs first (unless the spec is clearly outdated).

### 2. Separation of Concerns

- **Specifications** (WHAT/WHY) must not dictate technology choices; they focus on outcomes.
- **Plans** (HOW) connect specs to concrete technical decisions.
- **Implementation** must stay traceable to both.

### 3. AGENT_CONFIG & AGENTS.md as Single Sources of Truth

- The `AGENT_CONFIG` dictionary in `src/specify_cli/__init__.py` is the authoritative registry for all supported AI agents.
- `AGENTS.md` documents how to add new agents; it must stay in sync with `AGENT_CONFIG`.
- Keys in `AGENT_CONFIG` must match actual CLI tool names (e.g., `"cursor-agent"`, not `"cursor"`).

### 4. Multi-Phase SDD Workflow

For any new feature or significant change in this project:

1. **Constitution** – Does the change align with `memory/constitution.md`? If not, propose updates.
2. **Spec** – What behavior or capability is being added? Create or refine `specs/<feature>/spec.md`.
3. **Clarification** – Identify ambiguities (edge cases, error modes, performance, multi-agent support).
4. **Plan** – Design the implementation: CLI changes, template updates, automation changes.
5. **Tasks** – Break the plan into ordered, testable tasks with file paths and success criteria.
6. **Implementation** – Code changes, template updates, script changes, aligned with tasks.
7. **Validation** – Verify implementation matches spec and passes tests; update docs if needed.

### 5. Documentation vs. Specs

- **Specs** (`specs/<feature>/`) are the source of truth for WHAT the system does.
- **Docs** (`docs/`) are explanatory; they explain SDD concepts and how to use Spec Kit.
- When behavior changes, update specs and plans first, then docs.

---

## Modification Guidelines for Warp Agents

### Before Making Changes

- **Identify affected SDD artifacts** – Which specs, plans, tasks, or constitution does this touch?
- **Check for existing specs** – If work is already specified in `specs/`, read it first.
- **Clarify the WHAT and WHY** – Understand the goal and context from the spec or constitution.

### During Changes

- **Label your responses with the SDD phase** you're operating in (e.g., `[Phase: Spec]`, `[Phase: Implementation]`).
- **Refer back to specs and plans** – Explain which spec items or plan sections your implementation is addressing.
- **Keep changes focused** – Prefer small, traceable changes over large refactors.
- **Update specs/plans/tasks alongside code** – Never silently change behavior without updating artifacts.

### After Changes

- **Validate against the spec** – Does the implementation match the spec items? Are acceptance criteria met?
- **Update documentation** if public behavior changed.
- **Add tests** to cover new or modified behavior.
- **Update version & CHANGELOG** if modifying `src/specify_cli/` (per AGENTS.md rule).

---

## Directory-Specific Rules

Each key directory has its own `WARP.md` with specialized guidance:

- **`src/specify_cli/WARP.md`** – CLI implementation, agent support, configuration.
- **`templates/WARP.md`** – Template and command definitions for agents.
- **`docs/WARP.md`** – Documentation, user guides, and conceptual docs.
- **`.github/WARP.md`** – CI/CD workflows, release packaging, automation.
- **`scripts/WARP.md`** – Helper scripts and cross-platform tooling.

When working in a subdirectory, Warp will load both the root `WARP.md` and the subdirectory-specific `WARP.md`, with subdirectory rules taking precedence.

---

## Communication Style

- **Concise yet complete** – Explain the SDD phase and which specs/plans/tasks you're referencing.
- **Actionable checklists** – When responding to change requests, include a checklist of what needs updating (specs, docs, tests, CHANGELOG, etc.).
- **Call out drift** – If you notice code and specs diverging, propose concrete edits to realign them.
- **Avoid "vibe coding"** – Every change should be traceable to a spec, plan, or task.

---

## Quick Reference

| Command | What It Does |
|---------|-------------|
| `specify init <project>` | Bootstrap a new SDD project for a chosen AI agent |
| `specify check` | Verify installed tools (git, agents, code editors) |
| `specify version` | Display CLI and template version info |

For SDD-enabled projects (bootstrapped with Specify CLI), agents can use:

- `/speckit.constitution` – Create or refine project principles
- `/speckit.specify` – Create or refine the spec
- `/speckit.clarify` – Clarify ambiguous requirements
- `/speckit.plan` – Create the technical implementation plan
- `/speckit.tasks` – Generate implementation tasks
- `/speckit.analyze` – Cross-artifact consistency check
- `/speckit.checklist` – Generate quality/acceptance checklists
- `/speckit.implement` – Execute implementation tasks

---

## Related Artifacts

- **`memory/constitution.md`** – Project principles and quality bars
- **`AGENTS.md`** – Comprehensive guide to adding new agent support
- **`README.md`** – User-facing overview and methodology guide
- **`docs/`** – Full documentation site (built with DocFX)
- **`pyproject.toml`** – Package metadata and versioning
- **`CHANGELOG.md`** – Release notes and version history
