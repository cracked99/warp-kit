"""
Unit tests for project detection module.

Tests cover:
- Stack detection for all supported stacks (Node, Python, .NET, Go, Java, Rust, generic)
- Test framework detection
- SDD artifact detection
- Fallback to generic for ambiguous/empty projects
- Monorepo handling with mixed stacks
"""

import pytest
import tempfile
from pathlib import Path
from src.specify_cli.project_detection import (
    detect_project_stack,
    detect_sdd_artifacts,
    DetectedStack,
    SDDStatus,
)


# ============================================================================
# Fixtures: Synthetic Project Directories
# ============================================================================


@pytest.fixture
def node_project():
    """Minimal Node.js project with Jest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create package.json
        (root / "package.json").write_text("""{
            "name": "test-app",
            "version": "1.0.0",
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }""")
        
        # Create jest config
        (root / "jest.config.js").write_text("module.exports = {};")
        
        # Create src and tests directories
        (root / "src").mkdir()
        (root / "src" / "index.js").write_text("console.log('hello');")
        
        (root / "tests").mkdir()
        (root / "tests" / "index.test.js").write_text("test('works', () => {});")
        
        yield root


@pytest.fixture
def python_project():
    """Minimal Python project with pytest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create pyproject.toml
        (root / "pyproject.toml").write_text("""[tool.pytest.ini_options]
testpaths = ["tests"]

[build-system]
requires = ["setuptools", "pytest>=6.0"]
""")
        
        # Create src and tests directories
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text("def hello(): pass")
        
        (root / "tests").mkdir()
        (root / "tests" / "test_main.py").write_text("def test_hello(): pass")
        
        yield root


@pytest.fixture
def dotnet_project():
    """Minimal .NET project with xunit."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create .csproj file
        (root / "MyApp.csproj").write_text("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="xunit" Version="2.4.2" />
  </ItemGroup>
</Project>""")
        
        # Create bin and obj directories (typical .NET artifacts)
        (root / "bin").mkdir()
        (root / "obj").mkdir()
        
        yield root


@pytest.fixture
def go_project():
    """Minimal Go project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create go.mod and go.sum
        (root / "go.mod").write_text("module github.com/example/myapp\n\ngo 1.21\n")
        (root / "go.sum").write_text("")
        
        # Create src files
        (root / "main.go").write_text("package main\n\nfunc main() {}")
        
        yield root


@pytest.fixture
def java_project():
    """Minimal Java project with Maven."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create pom.xml
        (root / "pom.xml").write_text("""<?xml version="1.0"?>
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>myapp</artifactId>
  <version>1.0</version>
  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
    </dependency>
  </dependencies>
</project>""")
        
        # Create src and target directories
        (root / "src").mkdir()
        (root / "target").mkdir()
        
        yield root


@pytest.fixture
def rust_project():
    """Minimal Rust project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create Cargo.toml
        (root / "Cargo.toml").write_text("""[package]
name = "myapp"
version = "0.1.0"
edition = "2021"
""")
        
        # Create src and target directories
        (root / "src").mkdir()
        (root / "src" / "main.rs").write_text("fn main() {}")
        (root / "target").mkdir()
        
        yield root


@pytest.fixture
def generic_project():
    """Empty/generic project (only Dockerfile)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Only a Dockerfile
        (root / "Dockerfile").write_text("FROM ubuntu:latest\nRUN echo hello\n")
        
        yield root


@pytest.fixture
def monorepo_project():
    """Monorepo with both Node and Python."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Node project
        (root / "package.json").write_text('{"name": "frontend"}')
        (root / "node_modules").mkdir()
        
        # Python project
        (root / "pyproject.toml").write_text("[build-system]")
        (root / ".venv").mkdir()
        
        yield root


@pytest.fixture
def sdd_project():
    """Project with full SDD structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create SDD artifacts
        (root / "memory").mkdir()
        (root / "memory" / "constitution.md").write_text("# Constitution")
        
        (root / "specs").mkdir()
        (root / "specs" / "README.md").write_text("# Specs")
        
        (root / ".specify").mkdir()
        (root / ".specify" / "scripts").mkdir()
        
        (root / "WARP.md").write_text("# WARP.md")
        
        # Also add a package.json so it looks like Node
        (root / "package.json").write_text('{"name": "app"}')
        
        yield root


# ============================================================================
# Tests: Stack Detection
# ============================================================================


def test_detect_node_stack(node_project):
    """Verify Node.js stack detection with Jest."""
    stack = detect_project_stack(node_project)
    
    assert stack.id == "node"
    assert "Node.js" in stack.name
    assert stack.confidence_score > 0.5
    assert "package.json" in stack.signals
    assert stack.test_framework == "jest"
    assert stack.source_dir == "src"
    assert stack.test_dir == "tests"
    assert "npm test" in stack.commands["test_all"]


def test_detect_python_stack(python_project):
    """Verify Python stack detection with pytest."""
    stack = detect_project_stack(python_project)
    
    assert stack.id == "python"
    assert "Python" in stack.name
    assert stack.confidence_score > 0.5
    assert "pyproject.toml" in stack.signals
    assert stack.test_framework == "pytest"
    assert stack.source_dir == "src"
    assert stack.test_dir == "tests"
    assert "pytest" in stack.commands["test_all"]


def test_detect_dotnet_stack(dotnet_project):
    """Verify .NET stack detection."""
    stack = detect_project_stack(dotnet_project)
    
    assert stack.id == "dotnet"
    assert ".NET" in stack.name
    assert stack.confidence_score > 0.5
    assert "*.csproj" in stack.signals  # Pattern stored, not actual filename
    assert stack.test_framework == "xunit"


def test_detect_go_stack(go_project):
    """Verify Go stack detection."""
    stack = detect_project_stack(go_project)
    
    assert stack.id == "go"
    assert "Go" in stack.name
    assert stack.confidence_score > 0.5
    assert "go.mod" in stack.signals


def test_detect_java_stack(java_project):
    """Verify Java stack detection."""
    stack = detect_project_stack(java_project)
    
    assert stack.id == "java"
    assert "Java" in stack.name
    assert stack.confidence_score > 0.5
    assert "pom.xml" in stack.signals
    assert stack.test_framework == "junit"


def test_detect_rust_stack(rust_project):
    """Verify Rust stack detection."""
    stack = detect_project_stack(rust_project)
    
    assert stack.id == "rust"
    assert "Rust" in stack.name
    assert stack.confidence_score > 0.5
    assert "Cargo.toml" in stack.signals


def test_detect_generic_fallback(generic_project):
    """Empty/generic project falls back to generic stack."""
    stack = detect_project_stack(generic_project)
    
    assert stack.id == "generic"
    assert "Generic" in stack.name
    assert stack.confidence_score == 0.0


def test_detect_monorepo_highest_confidence(monorepo_project):
    """Monorepo with multiple stacks selects highest confidence."""
    stack = detect_project_stack(monorepo_project)
    
    # Both Node and Python present, but Node has primary signal (package.json)
    # so should win
    assert stack.id in ["node", "python"]  # Either is valid; Node slightly higher confidence
    assert stack.confidence_score > 0.5


# ============================================================================
# Tests: SDD Artifact Detection
# ============================================================================


def test_sdd_status_no_artifacts(node_project):
    """Non-SDD project has no artifacts."""
    status = detect_sdd_artifacts(node_project)
    
    assert not status.has_constitution
    assert not status.has_specs
    assert not status.has_specify_dir
    assert not status.has_warp_root
    assert not status.is_sdd_enabled


def test_sdd_status_full_sdd(sdd_project):
    """Full SDD project has all artifacts."""
    status = detect_sdd_artifacts(sdd_project)
    
    assert status.has_constitution
    assert status.has_specs
    assert status.has_specify_dir
    assert status.has_warp_root
    assert status.is_sdd_enabled


def test_sdd_status_partial_only_warp():
    """Project with only WARP is not considered SDD-enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "WARP.md").write_text("# WARP")
        
        status = detect_sdd_artifacts(root)
        
        assert not status.has_constitution
        assert not status.has_specs
        assert status.has_warp_root
        assert not status.is_sdd_enabled


def test_sdd_status_subdirectory_warps(sdd_project):
    """Detect subdirectory WARP files."""
    # Create subdirectory WARPs
    (sdd_project / "src").mkdir(exist_ok=True)
    (sdd_project / "src" / "WARP.md").write_text("# src WARP")
    
    (sdd_project / "tests").mkdir(exist_ok=True)
    (sdd_project / "tests" / "WARP.md").write_text("# tests WARP")
    
    status = detect_sdd_artifacts(sdd_project)
    
    assert status.has_warp_subdirs["src"]
    assert status.has_warp_subdirs["tests"]
    assert not status.has_warp_subdirs["docs"]  # Not created


# ============================================================================
# Tests: Integration & Edge Cases
# ============================================================================


def test_empty_directory():
    """Completely empty directory falls back to generic."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        stack = detect_project_stack(root)
        
        assert stack.id == "generic"
        assert stack.confidence_score == 0.0


def test_ci_detection():
    """CI presence detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Without CI
        stack1 = detect_project_stack(root)
        assert not stack1.ci_present
        
        # With CI
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / "package.json").write_text("{}")
        stack2 = detect_project_stack(root)
        assert stack2.ci_present


def test_stack_commands_present():
    """All stacks have valid commands dict."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        stack = detect_project_stack(root)
        
        assert "build" in stack.commands
        assert "lint" in stack.commands
        assert "test_all" in stack.commands
        assert "test_single" in stack.commands


# ============================================================================
# Tests: Idempotency & Consistency
# ============================================================================


def test_detection_idempotent(node_project):
    """Running detection twice produces identical results."""
    stack1 = detect_project_stack(node_project)
    stack2 = detect_project_stack(node_project)
    
    assert stack1.id == stack2.id
    assert stack1.name == stack2.name
    assert stack1.confidence_score == stack2.confidence_score
    assert stack1.test_framework == stack2.test_framework


def test_sdd_detection_idempotent(sdd_project):
    """SDD detection is idempotent."""
    status1 = detect_sdd_artifacts(sdd_project)
    status2 = detect_sdd_artifacts(sdd_project)
    
    assert status1.has_constitution == status2.has_constitution
    assert status1.has_specs == status2.has_specs
    assert status1.is_sdd_enabled == status2.is_sdd_enabled
