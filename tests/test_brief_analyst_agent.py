from __future__ import annotations

from pathlib import Path

from app.agents import brief_analyst_agent
from app.models.state import ProjectState


def test_brief_analyst_agent_with_mocked_llm(
    sample_brief_file: Path,
    minimal_project_dir: Path,
    monkeypatch,
) -> None:
    def fake_llm_extraction(brief_text: str, model_name: str) -> dict[str, object]:
        return {
            "brief_summary": "Mocked summary for the assignment brief.",
            "brief_requirements": [
                "Use 4 agents",
                "Use custom Python tools",
                "Include testing and evaluation",
            ],
            "technical_constraints": [
                "Run locally",
                "Do not use paid APIs",
            ],
            "grading_signals": [
                "Architecture quality matters",
                "Testing quality matters",
            ],
        }

    monkeypatch.setattr(
        brief_analyst_agent,
        "_run_llm_extraction",
        fake_llm_extraction,
    )

    state: ProjectState = {
        "user_request": "Analyze the brief.",
        "brief_path": str(sample_brief_file),
        "project_path": str(minimal_project_dir),
        "llm_model": "llama3",
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = brief_analyst_agent.brief_analyst_agent_node(state)

    assert result["brief_summary"] == "Mocked summary for the assignment brief."
    assert result["brief_requirements"] == [
        "Use 4 agents",
        "Use custom Python tools",
        "Include testing and evaluation",
    ]
    assert result["technical_constraints"] == [
        "Run locally",
        "Do not use paid APIs",
    ]
    assert result["grading_signals"] == [
        "Architecture quality matters",
        "Testing quality matters",
    ]
    assert "brief_parse" in result["repo_findings"]
    assert result["logs"][-1]["agent"] == "BriefAndRubricAnalystAgent"
    assert result["logs"][-1]["details"]["used_fallback"] is False


def test_brief_analyst_agent_fallback_path(
    sample_brief_file: Path,
    minimal_project_dir: Path,
    monkeypatch,
) -> None:
    def fake_llm_extraction(brief_text: str, model_name: str):
        return None

    monkeypatch.setattr(
        brief_analyst_agent,
        "_run_llm_extraction",
        fake_llm_extraction,
    )

    state: ProjectState = {
        "user_request": "Analyze the brief.",
        "brief_path": str(sample_brief_file),
        "project_path": str(minimal_project_dir),
        "llm_model": "llama3",
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = brief_analyst_agent.brief_analyst_agent_node(state)

    assert result["brief_summary"] != ""
    assert len(result["brief_requirements"]) > 0
    assert result["logs"][-1]["details"]["used_fallback"] is True


def test_brief_analyst_agent_empty_brief(tmp_path: Path, monkeypatch) -> None:
    """Security / edge-case: empty brief content should not crash."""
    empty_brief = tmp_path / "empty.md"
    empty_brief.write_text("", encoding="utf-8")

    state: ProjectState = {
        "brief_path": str(empty_brief),
        "project_path": str(tmp_path),
        "llm_model": "llama3",
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = brief_analyst_agent.brief_analyst_agent_node(state)

    # Should not crash; should record a warning
    assert any(entry["level"] == "WARNING" for entry in result["logs"])