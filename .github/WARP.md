# WARP.md – CI/CD, Release Automation, & Workflows

Warp agents MUST treat the **global rule "Spec-Driven Development (SDD) – Global Workflow"** and the **root `WARP.md`** as the baseline. This file provides specialized guidance for CI/CD.

---

## Scope & Purpose

This directory contains **GitHub Actions workflows** that automate linting, testing, documentation builds, and release packaging. Changes here affect how code flows from development to users.

**Contents**:
- **workflows/** – GitHub Actions CI/CD pipelines
  - `lint.yml` – Markdown linting via `markdownlint-cli2`
  - `release.yml` – Automated release process (template packaging, version bumping, GitHub Release)
  - `docs.yml` – Documentation build and deployment to GitHub Pages
- **scripts/** – Helper scripts invoked by workflows
  - `create-release-packages.sh` / `.ps1` – Build per-agent template ZIPs
  - `create-github-release.sh` – Publish release and artifacts
  - `get-next-version.sh` – Semantic version bumping
  - `update-version.sh` – Update version in `pyproject.toml`
  - `check-release-exists.sh` – Verify release already exists (prevent duplicates)

---

## Workflow Diagram

```
main branch commit
       ↓
   [lint.yml]
   ├→ Markdown linting
   └→ (PASS/FAIL)
       ↓ (if all checks pass)
   [release.yml] – MANUAL TRIGGER or automatic on merge to main
   ├→ Bump version (semantic versioning)
   ├→ Update pyproject.toml & CHANGELOG.md
   ├→ [create-release-packages.sh]
   │  ├→ Build ZIPs for each agent × script combination
   │  └→ Outputs to .genreleases/
   ├→ [create-github-release.sh]
   │  ├→ Creates GitHub Release tag
   │  └→ Uploads all ZIPs as artifacts
   └→ [docs.yml] (can run in parallel)
      ├→ Build DocFX docs
      └→ Deploy to GitHub Pages
```

---

## Key Workflows

### `lint.yml` – Continuous Linting

**Runs on**: Every push to any branch  
**Checks**: Markdown formatting via `markdownlint-cli2`  
**Fails if**: Markdown linting violations found  

**Local equivalent**:
```bash
markdownlint-cli2 '**/*.md'
```

### `release.yml` – Release & Package Generation

**Runs on**: Manual trigger or automatic on merge to `main`  
**Steps**:
1. Determine next semantic version (from previous tags)
2. Update `pyproject.toml` with new version
3. Build release packages for all agent × script combinations
4. Create GitHub Release with tag
5. Upload ZIPs as release assets

**Executed scripts**:
- `get-next-version.sh` – Reads existing tags, calculates next version
- `update-version.sh` – Updates `pyproject.toml`
- `create-release-packages.sh` – Main build script (per-agent ZIPs)
- `create-github-release.sh` – Creates release on GitHub

**Output**: GitHub Release with assets like `spec-kit-template-claude-sh-v0.0.23.zip`

### `docs.yml` – Documentation Build & Deploy

**Runs on**: Manual trigger or automatic on merge to `main`  
**Steps**:
1. Install DocFX
2. Build HTML documentation
3. Deploy to GitHub Pages

**Output**: Docs published at `https://github.github.io/spec-kit/`

---

## SDD-Aligned Workflow Modification Process

For **changes to CI or release scripts**:

1. **Update or create specs** describing the desired CI behavior or release process (e.g., new agent packages, new checks)
2. **Clarify edge cases**: what happens on failure, partial success, or when tools are missing
3. **Plan**: map specs to specific workflow files and steps
4. **Tasks**: enumerate workflow YAMLs and scripts to change, plus tests or dry runs
5. **Implement changes**, keeping them cross-platform where possible
6. **Validate** by:
   - Running workflows in a branch or PR
   - Confirming behavior matches spec and does not break existing flows

---

## Modification Checklist for Warp Agents

Before editing `.github/`, **explicitly confirm**:

- [ ] Which spec and plan govern the change (if missing, propose creating them)
- [ ] Compatibility with AGENT_CONFIG and `scripts/` and `templates/` logic
- [ ] Versioning and CHANGELOG implications are considered
- [ ] All supported agents are covered (per AGENTS.md)
- [ ] Changes have been tested in a feature branch or PR

---

## `create-release-packages.sh` – Deep Dive

This is the most complex script. It:

1. Defines `ALL_AGENTS` array (all supported agents)
2. For each agent:
   - For each script type (`sh` or `ps`):
     - Create a temporary build directory
     - Copy base templates
     - Process agent-specific commands (from `templates/commands/`)
     - Substitute placeholders (`{SCRIPT}`, `{ARGS}`, `__AGENT__`)
     - Convert format (Markdown for most, TOML for Gemini/Qwen)
     - Create agent folder structure (`.claude/`, `.gemini/`, etc.)
     - Zip the result
3. Output per-agent ZIPs to `.genreleases/`

**Key logic**:
- Template substitution uses `sed` to replace placeholders
- Agent-specific folders are created based on `AGENT_CONFIG` (from CLI)
- Format conversion uses `yq` (YAML/TOML) for Gemini and Qwen
- Each ZIP gets a unique name: `spec-kit-template-{agent}-{script}-v{version}.zip`

---

## When Adding a New Agent

Update these files:

1. **`src/specify_cli/__init__.py`** – Add to `AGENT_CONFIG`
2. **`.github/workflows/scripts/create-release-packages.sh`** – Add to `ALL_AGENTS` and case statement
3. **`.github/workflows/scripts/create-github-release.sh`** – Add to release artifact uploads
4. **`README.md`** – Update Supported AI Agents table
5. (Optionally) **`scripts/bash/update-agent-context.sh`** and **`scripts/powershell/`** – Add agent context update logic

---

## Troubleshooting

- **Lint fails**: Run `markdownlint-cli2 '**/*.md'` locally and fix warnings
- **Release fails**: Check the workflow run logs for details; common causes are version conflicts or missing scripts
- **Docs don't deploy**: Check GitHub Pages settings; should deploy from `gh-pages` branch
- **Package assets missing**: Check `.genreleases/` directory after `create-release-packages.sh` runs

---

## Testing Workflows Locally

Most scripts can be tested locally:

```bash
# Test markdown linting
markdownlint-cli2 '**/*.md'

# Test version bumping
bash .github/workflows/scripts/get-next-version.sh

# Test package creation (dry-run, or create in temp dir)
bash .github/workflows/scripts/create-release-packages.sh
```
