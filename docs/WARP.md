# WARP.md – Project Documentation

Warp agents MUST treat the **global rule "Spec-Driven Development (SDD) – Global Workflow"** and the **root `WARP.md`** as the baseline. This file provides specialized guidance for documentation.

---

## Scope & Purpose

This directory contains **user-facing documentation** built with DocFX and deployed to GitHub Pages. Changes here become the public face of Spec Kit.

**Contents**:
- `README.md` – Overview, methodology, quickstart
- `index.md` – Documentation landing page
- `installation.md` – Install instructions and prerequisites
- `quickstart.md` – Step-by-step guide to first SDD project
- `local-development.md` – Guide for contributors working on the CLI
- `upgrade.md` – Instructions for upgrading the CLI and migrating projects
- `toc.yml` – Table of contents (DocFX configuration)
- `docfx.json` – DocFX build configuration

---

## Documentation Philosophy

- **User-centric** – Assume readers are learning SDD for the first time
- **Example-driven** – Every concept includes concrete examples
- **Troubleshooting-focused** – Include common issues and solutions
- **Spec Kit-centric** – Emphasize the role of Spec Kit in enabling SDD

---

## Key Documents & Their Purpose

| Document | Audience | Purpose |
|----------|----------|---------|
| `README.md` | Everyone | Overview, methodology, quick links |
| `installation.md` | New users | Install CLI, check prerequisites |
| `quickstart.md` | Getting started | First SDD project walkthrough |
| `local-development.md` | Contributors | How to iterate on the CLI locally |
| `upgrade.md` | Existing users | How to upgrade CLI and update projects |

---

## Design Principles

Documentation must:
- **Clearly distinguish** between:
  - SDD artifacts (constitution/spec/plan/tasks) vs explanatory docs
- **Never diverge from the actual specs**; when behavior changes:
  - Specs & plans get updated first, then docs
- **Provide explicit links** or references to canonical specs where relevant

---

## SDD-Aligned Documentation Update Workflow

For **feature or behavior changes**:

1. **Confirm the relevant** `specs/<feature>/` files and constitution are updated
2. **Identify which docs** in `docs/` are impacted (quickstart, concepts, reference)
3. **Plan and create tasks** that map doc sections to spec items (to avoid drift)
4. **Implement doc changes** with clear headings, cross-links, and examples
5. **Validate** by:
   - Checking docs against current spec and code
   - Ensuring examples and code snippets are up to date

---

## Writing & Editing Guidelines

**Principles**:
- Keep language clear and avoid jargon (or define it when you use it)
- Use code blocks for CLI commands; include expected output when helpful
- Link to related sections and external resources
- Frontload the most important information

**Structure**:
- H1 (`#`) – Page title
- H2 (`##`) – Major sections
- H3 (`###`) – Subsections
- Use numbered lists for steps, bullet lists for concepts
- Use blockquotes (`>`) for tips, warnings, notes

**Example**:
```markdown
## Installation

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) for package management

### Install Specify

\`\`\`bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
\`\`\`

> **Tip:** Use `uv tool upgrade` to update later.
```

---

## Modification Checklist for Warp Agents

Before editing or creating docs, **explicitly confirm**:

- [ ] Which spec/plan/tasks the doc is derived from (if unclear, ask before writing)
- [ ] Whether specs and code have been updated first (docs follow, never lead)
- [ ] Whether examples and code snippets match current behavior
- [ ] Whether new links are valid and point to canonical sources
- [ ] If you discover inconsistencies between docs and specs, propose concrete updates to specs/plans

---

## Building & Deploying Docs

**Build locally**:
```bash
# Requires DocFX installed
docfx docs/docfx.json

# Outputs to docs/_site/
python -m http.server 8000 --directory docs/_site/
# Visit http://localhost:8000
```

**Automatic deployment**:
- When code is merged to `main`, `.github/workflows/docs.yml` builds and deploys to GitHub Pages
- Check GitHub Pages settings in repo settings if docs aren't showing up

---

## Common Doc Updates

- **New agent added?** Update `README.md` Supported AI Agents table and `installation.md` prerequisites
- **New CLI command?** Add to `README.md` CLI Reference and update `quickstart.md` if it's part of the flow
- **Bug fix with user workaround?** Add to `upgrade.md` or relevant guide
- **New `/speckit.*` command?** Document in `quickstart.md` and `README.md`

---

## Quality Checks

Before merging doc changes:

- Run `markdownlint-cli2 '**/*.md'` to check formatting
- Build locally with `docfx` and verify HTML renders correctly
- Click links to ensure they work (especially cross-doc links)
- Read the output once—does it flow logically?
- Verify examples run without errors on a fresh machine
