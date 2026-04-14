from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_brief_file(tmp_path: Path) -> Path:
    brief = tmp_path / "sample_assignment.md"
    brief.write_text(
        "\n".join(
            [
                "# Sample Assignment Brief",
                "",
                "Build a locally hosted Multi-Agent System.",
                "The system must use 4 agents.",
                "The system must use custom Python tools.",
                "The system must include logging or tracing.",
                "The system must include testing and evaluation.",
                "The system must not use paid APIs.",
            ]
        ),
        encoding="utf-8",
    )
    return brief


@pytest.fixture
def minimal_project_dir(tmp_path: Path) -> Path:
    project = tmp_path / "demo_project"
    project.mkdir()

    (project / "README.md").write_text(
        "# Demo Project\n\nThis is a sample repository.\n",
        encoding="utf-8",
    )
    (project / "requirements.txt").write_text(
        "pytest\nlanggraph\n",
        encoding="utf-8",
    )
    return project


@pytest.fixture
def richer_project_dir(tmp_path: Path) -> Path:
    project = tmp_path / "rich_project"
    project.mkdir()

    (project / "README.md").write_text(
        "# Rich Project\n\nMore complete sample repository.\n",
        encoding="utf-8",
    )
    (project / "requirements.txt").write_text(
        "pytest\nlanggraph\npydantic\n",
        encoding="utf-8",
    )

    src_dir = project / "app"
    src_dir.mkdir()
    (src_dir / "main.py").write_text(
        "def run():\n    return 'ok'\n",
        encoding="utf-8",
    )

    tests_dir = project / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_dummy.py").write_text(
        "def test_dummy():\n    assert True\n",
        encoding="utf-8",
    )

    docs_dir = project / "docs"
    docs_dir.mkdir()
    (docs_dir / "overview.md").write_text(
        "# Overview\n\nProject documentation.\n",
        encoding="utf-8",
    )

    return project