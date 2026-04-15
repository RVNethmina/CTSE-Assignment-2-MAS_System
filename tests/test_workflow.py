from __future__ import annotations

from pathlib import Path

from app.agents import brief_analyst_agent, intake_agent, repo_auditor_agent, strategist_agent
from app.graph.workflow import build_workflow
from app.models.state import ProjectState


def test_full_workflow_runs_with_mocked_llm(
    sample_brief_file: Path,
    minimal_project_dir: Path,
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    def fake_llm_extraction(brief_text: str, model_name: str) -> dict[str, object]:
        return {
            "brief_summary": "Workflow integration summary",
            "brief_requirements": [
                "Use local models",
                "Use 3 to 4 agents",
                "Use custom Python tools",
            ],
            "technical_constraints": [
                "Run locally",
                "No paid APIs",
            ],
            "grading_signals": [
                "Architecture",
                "Testing",
            ],
        }

    monkeypatch.setattr(
        brief_analyst_agent,
        "_run_llm_extraction",
        fake_llm_extraction,
    )
    monkeypatch.setattr(
        intake_agent,
        "_run_intake_reasoning",
        lambda validation_issues, project_type, model_name: "Mocked intake summary.",
    )
    monkeypatch.setattr(
        repo_auditor_agent,
        "_run_audit_reasoning",
        lambda repo_summary, missing_artifacts, model_name: "Mocked audit summary.",
    )
    monkeypatch.setattr(
        strategist_agent,
        "_run_strategy_reasoning",
        lambda risks, actions, model_name: "Mocked executive summary.",
    )

    workflow = build_workflow()

    initial_state: ProjectState = {
        "user_request": "Analyze this project.",
        "brief_path": str(sample_brief_file),
        "project_path": str(minimal_project_dir),
        "llm_model": "llama3",
    }

    final_state = workflow.invoke(initial_state)

    assert final_state["brief_summary"] == "Workflow integration summary"
    assert "documentation" in final_state["present_artifacts"]
    assert "configuration" in final_state["present_artifacts"]
    assert "source_code" in final_state["missing_artifacts"]
    assert "tests" in final_state["missing_artifacts"]
    assert len(final_state["risks"]) > 0
    assert len(final_state["recommended_actions"]) > 0
    assert final_state["final_report_path"].endswith("rescue_report.md")
    assert len(final_state["logs"]) == 4
    assert final_state["intake_summary"] == "Mocked intake summary."
    assert final_state["audit_summary"] == "Mocked audit summary."
    assert final_state["executive_summary"] == "Mocked executive summary."