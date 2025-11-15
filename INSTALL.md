# Installation Guide - Warp Kit v0.4.0

## Quick Install (Recommended)

### Option 1: Using `uv` (Fastest)

```bash
uv tool install git+https://github.com/cracked99/warp-kit@v0.4.0
```

### Option 2: Using `pip`

```bash
pip install git+https://github.com/cracked99/warp-kit@v0.4.0
```

### Option 3: Using `pipx`

```bash
pipx install git+https://github.com/cracked99/warp-kit@v0.4.0
```

---

## Development Install

If you want to develop on the project or contribute:

### Prerequisites
- Python 3.11+
- Git

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/cracked99/warp-kit.git
   cd warp-kit
   ```

2. **Checkout the release tag:**
   ```bash
   git checkout v0.4.0
   ```

3. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Verify installation:**
   ```bash
   warp-kit --version
   warp-kit check
   ```

---

## Verify Installation

After installation, verify that the CLI works:

```bash
# Check version and system info
warp-kit version

# Verify tools are installed
warp-kit check

# See available commands
warp-kit --help
```

---

## Usage with --warp-spec Flag

The v0.4.0 release adds the `--warp-spec` flag for autonomous SDD initialization:

```bash
# Initialize current project with SDD
warp-kit init --here --warp-spec

# Create new project with SDD
warp-kit init my-project --warp-spec

# See full options
warp-kit init --help
```

---

## What's New in v0.4.0

✅ **Autonomous Stack Detection** - Detects Python, Node, Go, Java, Rust, .NET  
✅ **WARP.md Generation** - Creates project guidance files  
✅ **SDD Bootstrap** - Sets up constitution, specs, templates  
✅ **Non-Destructive** - Preserves all existing content  
✅ **Idempotent** - Safe to run multiple times  
✅ **143 Passing Tests** - Comprehensive test coverage  

---

## Uninstall

```bash
# Using pip
pip uninstall warp-kit

# Using pipx
pipx uninstall warp-kit

# Using uv
uv tool uninstall warp-kit
```

---

## Troubleshooting

### Python Version Error
If you get a Python version error, ensure you have Python 3.11 or later:
```bash
python --version  # Should show 3.11.0 or higher
```

### Installation from Git Fails
Make sure you have git installed:
```bash
git --version
```

### Command Not Found
If `warp-kit` command is not found after installation:
- With `pip`: Ensure the installation directory is in your PATH
- With `pipx`: Run `pipx ensurepath`
- With `uv`: The tool is managed by uv automatically

### SSL/Certificate Issues
The CLI uses `truststore` for SSL verification. If you have certificate issues:
```bash
pip install --upgrade truststore
```

---

## For More Information

- **Documentation:** See `docs/` directory or visit the GitHub repo
- **Report Issues:** https://github.com/cracked99/warp-kit/issues
- **Contributing:** Check CONTRIBUTING.md in the repository

---

**Release:** v0.4.0  
**Released:** 2025-11-15  
**Status:** Stable
