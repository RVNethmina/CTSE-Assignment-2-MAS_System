from __future__ import annotations

from pathlib import Path

from app.agents import repo_auditor_agent
from app.agents.repo_auditor_agent import repo_auditor_agent_node
from app.models.state import ProjectState
from app.tools.repo_audit import audit_repository


def test_repo_auditor_agent_minimal_project(
    minimal_project_dir: Path, monkeypatch,
) -> None:
    monkeypatch.setattr(
        repo_auditor_agent,
        "_run_audit_reasoning",
        lambda repo_summary, missing_artifacts, model_name: "Mocked audit summary.",
    )

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
    assert result["audit_summary"] == "Mocked audit summary."


def test_repo_auditor_agent_richer_project(
    richer_project_dir: Path, monkeypatch,
) -> None:
    monkeypatch.setattr(
        repo_auditor_agent,
        "_run_audit_reasoning",
        lambda repo_summary, missing_artifacts, model_name: "Mocked audit summary.",
    )

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
    # Only check that the 4 basic artifacts are not missing;
    # the agent also appends insufficient_agents, missing_tools, etc.
    assert "source_code" not in result["missing_artifacts"]
    assert "tests" not in result["missing_artifacts"]
    assert "documentation" not in result["missing_artifacts"]
    assert "configuration" not in result["missing_artifacts"]


def test_repo_auditor_agent_missing_path(monkeypatch) -> None:
    """Security / edge-case: nonexistent project path should not raise."""
    monkeypatch.setattr(
        repo_auditor_agent,
        "_run_audit_reasoning",
        lambda repo_summary, missing_artifacts, model_name: "Mocked audit summary.",
    )

    state: ProjectState = {
        "project_path": "/this/does/not/exist",
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = repo_auditor_agent_node(state)

    # Should not raise; should record the issue.
    assert any("not found" in issue for issue in result["validation_issues"])
    assert result["repo_summary"] != ""


def test_repo_audit_ignores_generated_and_vendor_directories(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "README.md").write_text("# Project\n", encoding="utf-8")
    (project / "requirements.txt").write_text("pytest\n", encoding="utf-8")

    ignored_agent_dir = project / ".venv" / "app" / "agents"
    ignored_agent_dir.mkdir(parents=True)
    (ignored_agent_dir / "fake_agent.py").write_text("# generated\n", encoding="utf-8")

    ignored_test_dir = project / ".pytest_cache" / "tests"
    ignored_test_dir.mkdir(parents=True)
    (ignored_test_dir / "test_fake.py").write_text("def test_fake(): pass\n", encoding="utf-8")

    ignored_output_dir = project / "outputs"
    ignored_output_dir.mkdir()
    (ignored_output_dir / "rescue_report.json").write_text("{}", encoding="utf-8")

    ignored_sample_agent_dir = project / "sample_data" / "sample_project" / "app" / "agents"
    ignored_sample_agent_dir.mkdir(parents=True)
    (ignored_sample_agent_dir / "sample_agent.py").write_text("# sample\n", encoding="utf-8")

    result = audit_repository(str(project))

    assert result.agent_file_count == 0
    assert result.test_file_count == 0
    assert result.has_output_writer_evidence is False
