from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_domain_does_not_import_infrastructure_or_api() -> None:
    forbidden = ("kernel.custody.infrastructure", "sqlalchemy", "fastapi", "api")

    for path in (ROOT / "kernel").rglob("domain/*.py"):
        source = path.read_text(encoding="utf-8")
        assert not any(term in source for term in forbidden), path


def test_governance_domain_does_not_import_identity() -> None:
    source = (ROOT / "kernel" / "governance" / "domain" / "policies.py").read_text(
        encoding="utf-8"
    )

    assert "kernel.identity" not in source


def test_read_model_does_not_import_write_service() -> None:
    source = (ROOT / "kernel" / "custody" / "application" / "projections.py").read_text(
        encoding="utf-8"
    )

    assert "DeclareCustodyAssertionService" not in source


def test_required_top_level_structure_exists() -> None:
    expected = {
        "kernel",
        "adapters",
        "api",
        "sdk",
        "docs",
        "scripts",
        "tests",
        "examples",
    }

    assert expected.issubset({path.name for path in ROOT.iterdir() if path.is_dir()})


def test_python_packages_have_readmes_with_mermaid_diagrams() -> None:
    package_dirs = {
        path.parent
        for path in ROOT.rglob("__init__.py")
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    }

    for package_dir in package_dirs:
        readme = package_dir / "README.md"
        assert readme.exists(), package_dir
        assert "```mermaid" in readme.read_text(encoding="utf-8"), readme
