from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RescuePlanWriteResult:
    markdown_path: str
    json_path: str
    issues: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _format_list(items: list[str], empty_text: str = "None") -> str:
    """Format a markdown bullet list."""
    if not items:
        return f"- {empty_text}"
    return "\n".join(f"- {item}" for item in items)


def _priority_label(text: str) -> str:
    """Assign a simple priority label based on action wording."""
    lowered = text.lower()

    high_keywords = (
        "missing",
        "no ",
        "fail",
        "insufficient",
        "logging",
        "tests",
        "test",
        "agent",
        "output",
        "report generation",
    )
    medium_keywords = (
        "cross-check",
        "verify",
        "improve",
        "polish",
    )

    if any(keyword in lowered for keyword in high_keywords):
        return "High"
    if any(keyword in lowered for keyword in medium_keywords):
        return "Medium"
    return "Normal"


def _format_action_plan(actions: list[str]) -> str:
    """Format actions with priority labels."""
    if not actions:
        return "- None"

    lines: list[str] = []
    for action in actions:
        priority = _priority_label(action)
        lines.append(f"- **{priority}** — {action}")
    return "\n".join(lines)


def _compliance_snapshot(state: dict[str, Any]) -> str:
    """Create a compact compliance snapshot section."""
    repo_audit = state.get("repo_findings", {}).get("repo_audit", {})

    agent_count = int(repo_audit.get("agent_file_count", 0))
    tool_count = int(repo_audit.get("tool_file_count", 0))
    test_count = int(repo_audit.get("test_file_count", 0))
    has_logging = bool(repo_audit.get("has_logging_evidence", False))
    has_output_writer = bool(repo_audit.get("has_output_writer_evidence", False))

    def yes_no(value: bool) -> str:
        return "Yes" if value else "No"

    lines = [
        "| Check | Status |",
        "|---|---|",
        f"| 3 to 4 agent modules present | {'Yes' if agent_count >= 3 else 'No'} |",
        f"| At least 1 custom tool present | {'Yes' if tool_count >= 1 else 'No'} |",
        f"| Test files present | {'Yes' if test_count > 0 else 'No'} |",
        f"| Logging/tracing evidence present | {yes_no(has_logging)} |",
        f"| Output/report writing evidence present | {yes_no(has_output_writer)} |",
    ]
    return "\n".join(lines)


def _final_recommendation(readiness_score: int) -> str:
    """Generate a short final recommendation based on readiness score."""
    if readiness_score >= 85:
        return "The project is in strong shape. Focus on polishing the demo, validating edge cases, and tightening documentation."
    if readiness_score >= 65:
        return "The project is partially ready, but a few important gaps still need attention before submission."
    if readiness_score >= 40:
        return "The project is at moderate risk. Focus first on the highest-impact missing components before polishing anything else."
    return "The project is not submission-ready yet. Resolve the critical blockers first: missing agents, missing tests, missing observability, and missing final output generation."


def _agent_design_snapshot(state: dict[str, Any]) -> str:
    """Render a markdown snapshot of agent design details."""
    profiles = state.get("agent_profiles", {})
    if not profiles:
        return "- None"

    sections: list[str] = []
    for agent_name, profile in profiles.items():
        sections.append(
            "\n".join(
                [
                    f"### {agent_name}",
                    f"- **Owner:** {profile.get('student_owner', 'Unknown')}",
                    f"- **Role:** {profile.get('role', 'Unknown')}",
                    f"- **Persona:** {profile.get('persona', 'Unknown')}",
                    f"- **Objective:** {profile.get('objective', 'Unknown')}",
                    f"- **Constraints:** {profile.get('constraints', 'Unknown')}",
                    f"- **Owned Tool:** {profile.get('owned_tool', 'Unknown')}",
                    f"- **System Prompt:** {profile.get('system_prompt', 'Unknown')}",
                ]
            )
        )

    return "\n\n".join(sections)


def _contribution_matrix(state: dict[str, Any]) -> str:
    """Render a contribution matrix for the report."""
    profiles = state.get("agent_profiles", {})
    if not profiles:
        return "- None"

    lines = [
        "| Student | Agent | Owned Tool | Main Focus |",
        "|---|---|---|---|",
    ]

    for _, profile in profiles.items():
        lines.append(
            f"| {profile.get('student_owner', 'Unknown')} | "
            f"{profile.get('role', 'Unknown')} | "
            f"{profile.get('owned_tool', 'Unknown')} | "
            f"{profile.get('objective', 'Unknown')} |"
        )

    return "\n".join(lines)


def build_markdown_report(state: dict[str, Any]) -> str:
    """Build a polished markdown rescue report from workflow state."""
    brief_summary = state.get("brief_summary", "No brief summary available.")
    repo_summary = state.get("repo_summary", "No repository summary available.")
    present_artifacts = state.get("present_artifacts", [])
    missing_artifacts = state.get("missing_artifacts", [])
    risks = state.get("risks", [])
    actions = state.get("recommended_actions", [])
    assignments = state.get("member_assignments", [])
    checklist = state.get("demo_checklist", [])
    outline = state.get("report_outline", [])
    brief_requirements = state.get("brief_requirements", [])
    technical_constraints = state.get("technical_constraints", [])
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readiness_score = int(state.get("readiness_score", 0))
    blockers = state.get("blockers", [])
    agent_design_snapshot = _agent_design_snapshot(state)
    contribution_matrix = _contribution_matrix(state)

    report = f"""# Project Rescue Report

Generated at: **{generated_at}**

## Executive Summary
This report analyzes the provided project against the assignment brief and identifies the most important gaps before submission.

## Submission Readiness Score
**{readiness_score}/100**

## Current Blockers
{_format_list(blockers)}

## Brief Summary
{brief_summary}

## Extracted Assignment Requirements
{_format_list(brief_requirements)}

## Technical Constraints
{_format_list(technical_constraints)}

## Agent Design Snapshot
{agent_design_snapshot}

## Contribution Matrix
{contribution_matrix}

## Repository Summary
{repo_summary}

## Compliance Snapshot
{_compliance_snapshot(state)}

## Present Evidence
{_format_list(present_artifacts)}

## Missing or Weak Areas
{_format_list(missing_artifacts)}

## Key Risks
{_format_list(risks)}

## Prioritized Action Plan
{_format_action_plan(actions)}

## Suggested Team Ownership
{_format_list(assignments)}

## Demo Checklist
{_format_list(checklist)}

## Technical Report Outline
{_format_list(outline)}

## Final Recommendation
{_final_recommendation(readiness_score)}
"""
    return report.strip() + "\n"


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