from __future__ import annotations

from pathlib import Path

from app.agents import intake_agent
from app.agents.intake_agent import intake_agent_node
from app.models.state import ProjectState


def test_intake_agent_valid_inputs(
    sample_brief_file: Path, minimal_project_dir: Path, monkeypatch,
) -> None:
    monkeypatch.setattr(
        intake_agent,
        "_run_intake_reasoning",
        lambda validation_issues, project_type, model_name: "Mocked intake summary.",
    )

    state: ProjectState = {
        "user_request": "Analyze the project.",
        "brief_path": str(sample_brief_file),
        "project_path": str(minimal_project_dir),
    }

    result = intake_agent_node(state)

    assert result["validation_issues"] == []
    assert result["project_type"] == "Python"
    assert result["provided_inputs"] == [str(sample_brief_file), str(minimal_project_dir)]
    assert "intake_validation" in result["repo_findings"]
    assert result["repo_findings"]["intake_validation"]["brief_path_exists"] is True
    assert result["repo_findings"]["intake_validation"]["project_path_exists"] is True
    assert len(result["logs"]) == 1
    assert result["logs"][0]["agent"] == "IntakeAndScopeAgent"
    assert result["intake_summary"] == "Mocked intake summary."


def test_intake_agent_missing_brief(
    minimal_project_dir: Path, tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setattr(
        intake_agent,
        "_run_intake_reasoning",
        lambda validation_issues, project_type, model_name: "Mocked intake summary.",
    )

    missing_brief = tmp_path / "missing_brief.md"

    state: ProjectState = {
        "user_request": "Analyze the project.",
        "brief_path": str(missing_brief),
        "project_path": str(minimal_project_dir),
    }

    result = intake_agent_node(state)

    assert result["validation_issues"]
    assert any("Brief file not found" in issue for issue in result["validation_issues"])
    assert result["repo_findings"]["intake_validation"]["brief_path_exists"] is False
    assert result["logs"][0]["level"] == "WARNING"


def test_intake_agent_rejects_path_traversal(tmp_path: Path, monkeypatch) -> None:
    """Security / edge-case: path traversal attempt must not raise."""
    monkeypatch.setattr(
        intake_agent,
        "_run_intake_reasoning",
        lambda validation_issues, project_type, model_name: "Mocked intake summary.",
    )

    state: ProjectState = {
        "brief_path": "../../etc/passwd",
        "project_path": str(tmp_path),
        "logs": [],
    }

    result = intake_agent_node(state)

    assert any("not found" in issue.lower() for issue in result["validation_issues"])
    # Must NOT raise an exception; handles gracefully.
