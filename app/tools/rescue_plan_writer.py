from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RescuePlanWriteResult:
    markdown_path: str
    json_path: str
    issues: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_markdown_report(state: dict[str, Any]) -> str:
    """Build a readable markdown rescue report from workflow state."""
    brief_summary = state.get("brief_summary", "No brief summary available.")
    repo_summary = state.get("repo_summary", "No repository summary available.")
    risks = state.get("risks", [])
    actions = state.get("recommended_actions", [])
    assignments = state.get("member_assignments", [])
    checklist = state.get("demo_checklist", [])
    outline = state.get("report_outline", [])
    missing_artifacts = state.get("missing_artifacts", [])

    def section(title: str, items: list[str]) -> str:
        if not items:
            return f"## {title}\n- None\n"
        lines = "\n".join(f"- {item}" for item in items)
        return f"## {title}\n{lines}\n"

    parts = [
        "# Project Rescue Report",
        "",
        "## Brief Summary",
        brief_summary,
        "",
        "## Repository Summary",
        repo_summary,
        "",
        section("Missing Artifacts", missing_artifacts),
        section("Risks", risks),
        section("Recommended Actions", actions),
        section("Member Assignments", assignments),
        section("Demo Checklist", checklist),
        section("Report Outline", outline),
    ]

    return "\n".join(parts).strip() + "\n"


def write_rescue_outputs(
    state: dict[str, Any],
    output_dir: str = "outputs",
) -> RescuePlanWriteResult:
    """
    Write the rescue plan to markdown and JSON files.

    Args:
        state: Final workflow state.
        output_dir: Directory where outputs should be stored.

    Returns:
        RescuePlanWriteResult containing file paths and issues.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    issues: list[str] = []
    markdown_path = out_dir / "rescue_report.md"
    json_path = out_dir / "rescue_report.json"

    try:
        markdown_path.write_text(build_markdown_report(state), encoding="utf-8")
    except Exception as exc:
        issues.append(f"Failed to write markdown report: {exc}")

    try:
        json_path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    except Exception as exc:
        issues.append(f"Failed to write JSON report: {exc}")

    return RescuePlanWriteResult(
        markdown_path=str(markdown_path),
        json_path=str(json_path),
        issues=issues,
    )