#!/usr/bin/env python3
"""
Project Detection Module - Autonomously detect project technology stacks and SDD artifacts.

This module provides:
- Technology stack detection (Node.js, Python, .NET, Go, Java, Rust, generic)
- Test framework inference
- SDD artifact detection (constitution, specs, WARP files)
- Confidence-based stack selection with fallback to generic
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from pathlib import Path
from enum import Enum


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class DetectedStack:
    """Represents a detected project technology stack with metadata."""
    
    id: str  # "node", "python", "dotnet", "go", "java", "rust", "generic"
    name: str  # Display name, e.g., "Node.js / TypeScript"
    confidence_score: float  # 0.0 to 1.0
    signals: List[str]  # File/directory patterns that triggered detection
    test_framework: Optional[str] = None  # Inferred test framework
    source_dir: Optional[str] = None  # Primary source directory (e.g., "src")
    test_dir: Optional[str] = None  # Primary test directory (e.g., "tests")
    commands: Dict[str, str] = field(default_factory=dict)  # "build", "lint", "test_all", "test_single"
    ci_present: bool = False  # Whether .github/workflows exists


@dataclass
class SDDStatus:
    """Represents the SDD initialization status of a project."""
    
    has_constitution: bool
    has_specs: bool
    has_specify_dir: bool
    has_warp_root: bool
    has_warp_subdirs: Dict[str, bool]  # "src", "tests", ".github", etc.
    
    @property
    def is_sdd_enabled(self) -> bool:
        """True if at least constitution + specs are present."""
        return self.has_constitution and self.has_specs


# ============================================================================
# Stack Definitions
# ============================================================================


STACK_DEFINITIONS = {
    "node": {
        "name": "Node.js / TypeScript",
        "primary_signals": [
            "package.json",
            "yarn.lock",
            "pnpm-lock.yaml",
        ],
        "secondary_signals": [
            "tsconfig.json",
            "node_modules/",
        ],
        "test_frameworks": [
            "jest",
            "mocha",
            "vitest",
            "playwright",
            "cypress",
        ],
        "commands": {
            "build": "npm run build",
            "lint": "npm run lint",
            "test_all": "npm test",
            "test_single": "npm test -- --testNamePattern='...'",
        },
    },
    "python": {
        "name": "Python",
        "primary_signals": [
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            "poetry.lock",
            "Pipfile",
        ],
        "secondary_signals": [
            "venv/",
            ".venv/",
            "src/",
            "tests/",
        ],
        "test_frameworks": [
            "pytest",
            "unittest",
            "nose2",
        ],
        "commands": {
            "build": "python -m build",
            "lint": "ruff check .",
            "test_all": "pytest",
            "test_single": "pytest tests/test_*.py::test_*",
        },
    },
    "dotnet": {
        "name": ".NET / C#",
        "primary_signals": [
            "*.csproj",
            "*.sln",
            "Directory.Build.props",
        ],
        "secondary_signals": [
            "bin/",
            "obj/",
        ],
        "test_frameworks": [
            "xunit",
            "nunit",
            "mstest",
        ],
        "commands": {
            "build": "dotnet build",
            "lint": "dotnet format --verify-no-changes",
            "test_all": "dotnet test",
            "test_single": "dotnet test --filter=...",
        },
    },
    "go": {
        "name": "Go",
        "primary_signals": [
            "go.mod",
            "go.sum",
        ],
        "secondary_signals": [
            "vendor/",
        ],
        "test_frameworks": [
            "testing",  # Built-in
        ],
        "commands": {
            "build": "go build ./...",
            "lint": "golangci-lint run",
            "test_all": "go test ./...",
            "test_single": "go test ./... -run=TestName",
        },
    },
    "java": {
        "name": "Java",
        "primary_signals": [
            "pom.xml",
            "build.gradle",
            ".gradle/",
        ],
        "secondary_signals": [
            "src/",
            "target/",
            "build/",
        ],
        "test_frameworks": [
            "junit",
            "testng",
        ],
        "commands": {
            "build": "mvn clean install",  # Maven example
            "lint": "mvn checkstyle:check",
            "test_all": "mvn test",
            "test_single": "mvn test -Dtest=TestClass#testMethod",
        },
    },
    "rust": {
        "name": "Rust",
        "primary_signals": [
            "Cargo.toml",
        ],
        "secondary_signals": [
            "target/",
        ],
        "test_frameworks": [
            "cargo test",  # Built-in
        ],
        "commands": {
            "build": "cargo build --release",
            "lint": "cargo clippy",
            "test_all": "cargo test",
            "test_single": "cargo test test_name",
        },
    },
    "generic": {
        "name": "Generic / Unknown",
        "primary_signals": [],
        "secondary_signals": [],
        "test_frameworks": [],
        "commands": {
            "build": "[Your project's build command]",
            "lint": "[Your project's lint command]",
            "test_all": "[Your project's test command]",
            "test_single": "[Your project's single test command]",
        },
    },
}


# ============================================================================
# Detection Functions
# ============================================================================


def detect_project_stack(root: Path) -> DetectedStack:
    """
    Detect the technology stack of a project based on file presence.
    
    Uses a confidence-scoring algorithm that:
    1. Scans for primary signals (build files, manifests) - high weight
    2. Scans for secondary signals (directories, config files) - low weight
    3. Selects the highest-confidence stack
    4. Falls back to "generic" if no clear winner
    
    Args:
        root: Path to the project root directory
    
    Returns:
        DetectedStack with id, name, confidence_score, signals, and commands
    """
    
    scores: Dict[str, float] = {}
    detected_signals: Dict[str, List[str]] = {}
    
    # Score each stack
    for stack_id, definition in STACK_DEFINITIONS.items():
        if stack_id == "generic":
            continue  # Skip generic for now, use as fallback
        
        score = 0.0
        signals = []
        
        # Check primary signals (higher weight)
        for signal in definition["primary_signals"]:
            if _signal_exists(root, signal):
                score += 0.7
                signals.append(signal)
        
        # Check secondary signals (lower weight)
        for signal in definition["secondary_signals"]:
            if _signal_exists(root, signal):
                score += 0.2
                signals.append(signal)
        
        scores[stack_id] = score
        detected_signals[stack_id] = signals
    
    # Find winner (highest confidence)
    winner_id = max(scores, key=scores.get) if scores else None
    winner_score = scores.get(winner_id, 0.0) if winner_id else 0.0
    
    # Fallback to generic if confidence too low
    MIN_CONFIDENCE_THRESHOLD = 0.5
    if winner_score < MIN_CONFIDENCE_THRESHOLD:
        winner_id = "generic"
        winner_score = 0.0
    
    definition = STACK_DEFINITIONS[winner_id]
    
    # Detect test framework
    test_framework = _detect_test_framework(root, winner_id)
    
    # Detect source and test directories
    source_dir = _detect_source_dir(root, winner_id)
    test_dir = _detect_test_dir(root, winner_id)
    
    # Check for CI
    ci_present = (root / ".github" / "workflows").exists()
    
    return DetectedStack(
        id=winner_id,
        name=definition["name"],
        confidence_score=winner_score,
        signals=detected_signals.get(winner_id, []),
        test_framework=test_framework,
        source_dir=source_dir,
        test_dir=test_dir,
        commands=definition["commands"].copy(),
        ci_present=ci_present,
    )


def detect_sdd_artifacts(root: Path) -> SDDStatus:
    """
    Detect existing SDD artifacts in a project.
    
    Checks for:
    - .warp-space/Warp-space.md (single source of truth)
    - .warp-space/memory/constitution.md
    - specs/ directory
    - .warp-space/ directory
    - WARP.md (root and subdirectories)
    
    Args:
        root: Path to the project root directory
    
    Returns:
        SDDStatus indicating which SDD artifacts are present
    """
    
    has_warpspace = (root / ".warp-space" / "Warp-space.md").exists()
    has_constitution = (root / ".warp-space" / "memory" / "constitution.md").exists()
    has_specs = (root / "specs").is_dir()
    has_warp_space_dir = (root / ".warp-space").is_dir()
    has_warp_root = (root / "WARP.md").exists()
    
    # Check for subdirectory WARPs
    has_warp_subdirs = {}
    for subdir in ["src", "tests", ".github", "docs", "scripts"]:
        subdir_warp = root / subdir / "WARP.md"
        has_warp_subdirs[subdir] = subdir_warp.exists()
    
    return SDDStatus(
        has_constitution=has_constitution,
        has_specs=has_specs,
        has_specify_dir=has_warp_space_dir,  # Still use this field for backward compat
        has_warp_root=has_warp_root,
        has_warp_subdirs=has_warp_subdirs,
    )


# ============================================================================
# Helper Functions
# ============================================================================


def _signal_exists(root: Path, signal: str) -> bool:
    """Check if a signal (file or directory pattern) exists in root."""
    try:
        if signal.startswith("*."):
            # Glob pattern like "*.csproj"
            matches = list(root.glob(signal))
            return len(matches) > 0
        else:
            # Regular file or directory
            path = root / signal
            return path.exists()
    except Exception:
        return False


def _detect_test_framework(root: Path, stack_id: str) -> Optional[str]:
    """
    Infer the test framework from lock files, manifests, or config files.
    
    Args:
        root: Project root
        stack_id: Detected stack ID
    
    Returns:
        Test framework name or None if not detected
    """
    
    definition = STACK_DEFINITIONS.get(stack_id, {})
    test_frameworks = definition.get("test_frameworks", [])
    
    if not test_frameworks:
        return None
    
    # Strategy: scan common files for test framework references
    
    if stack_id == "node":
        # Check package.json for dev dependencies
        pkg_json = root / "package.json"
        if pkg_json.exists():
            content = pkg_json.read_text()
            for fw in test_frameworks:
                if fw in content:
                    return fw
    
    elif stack_id == "python":
        # Check requirements.txt and pyproject.toml
        requirements = root / "requirements.txt"
        pyproject = root / "pyproject.toml"
        
        for file in [requirements, pyproject]:
            if file.exists():
                content = file.read_text()
                for fw in test_frameworks:
                    if fw in content:
                        return fw
    
    elif stack_id == "dotnet":
        # Check .csproj files for test references
        for csproj in root.glob("**/*.csproj"):
            content = csproj.read_text()
            for fw in test_frameworks:
                if fw.lower() in content.lower():
                    return fw
    
    # Default: return first framework if any detected
    return test_frameworks[0] if test_frameworks else None


def _detect_source_dir(root: Path, stack_id: str) -> Optional[str]:
    """
    Detect the primary source code directory.
    
    Args:
        root: Project root
        stack_id: Detected stack ID
    
    Returns:
        Directory name (e.g., "src") or None
    """
    
    common_source_dirs = ["src", "lib", "source"]
    
    for dir_name in common_source_dirs:
        if (root / dir_name).is_dir():
            return dir_name
    
    return None


def _detect_test_dir(root: Path, stack_id: str) -> Optional[str]:
    """
    Detect the primary test directory.
    
    Args:
        root: Project root
        stack_id: Detected stack ID
    
    Returns:
        Directory name (e.g., "tests", "__tests__") or None
    """
    
    common_test_dirs = [
        "tests",
        "test",
        "__tests__",
        "spec",
        "specs",
    ]
    
    for dir_name in common_test_dirs:
        if (root / dir_name).is_dir():
            return dir_name
    
    return None
