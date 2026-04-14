from __future__ import annotations

from pathlib import Path

from app.agents.repo_auditor_agent import repo_auditor_agent_node
from app.models.state import ProjectState


def test_repo_auditor_agent_minimal_project(minimal_project_dir: Path) -> None:
    state: ProjectState = {
        "project_path": str(minimal_project_dir),
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = repo_auditor_agent_node(state)

    assert result["repo_summary"] != ""
    assert "repo_audit" in result["repo_findings"]
    assert "configuration" in result["present_artifacts"]
    assert "documentation" in result["present_artifacts"]
    assert "source_code" in result["missing_artifacts"]
    assert "tests" in result["missing_artifacts"]
    assert result["logs"][-1]["agent"] == "RepositoryAndEvidenceAuditorAgent"


def test_repo_auditor_agent_richer_project(richer_project_dir: Path) -> None:
    state: ProjectState = {
        "project_path": str(richer_project_dir),
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = repo_auditor_agent_node(state)

    assert "configuration" in result["present_artifacts"]
    assert "documentation" in result["present_artifacts"]
    assert "source_code" in result["present_artifacts"]
    assert "tests" in result["present_artifacts"]
    assert result["missing_artifacts"] == []