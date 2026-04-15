from __future__ import annotations

from pathlib import Path

from app.agents import strategist_agent
from app.agents.strategist_agent import strategist_agent_node
from app.models.state import ProjectState


def test_strategist_agent_generates_outputs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        strategist_agent,
        "_run_strategy_reasoning",
        lambda risks, actions, model_name: "Mocked executive summary.",
    )

    state: ProjectState = {
        "brief_summary": "Test brief summary",
        "repo_summary": "Test repository summary",
        "brief_requirements": [
            "Use 4 agents",
            "Use tools",
        ],
        "technical_constraints": [
            "Run locally",
            "Do not use paid APIs",
        ],
        "missing_artifacts": [
            "source_code",
            "tests",
        ],
        "validation_issues": [],
        "logs": [],
    }

    result = strategist_agent_node(state)

    assert len(result["risks"]) >= 2
    assert len(result["recommended_actions"]) >= 2
    assert len(result["member_assignments"]) == 4
    assert len(result["demo_checklist"]) > 0
    assert len(result["report_outline"]) > 0
    assert result["executive_summary"] == "Mocked executive summary."

    markdown_path = tmp_path / "outputs" / "rescue_report.md"
    json_path = tmp_path / "outputs" / "rescue_report.json"

    assert markdown_path.exists()
    assert json_path.exists()
    assert result["final_report_path"].endswith("rescue_report.md")
    assert result["logs"][-1]["agent"] == "RiskAndDeliveryStrategistAgent"