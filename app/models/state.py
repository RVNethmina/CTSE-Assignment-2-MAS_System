from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from typing_extensions import NotRequired, TypedDict


class LogEntry(TypedDict):
    timestamp: str
    agent: str
    level: Literal["INFO", "WARNING", "ERROR"]
    message: str
    details: NotRequired[dict[str, Any]]


class ProjectState(TypedDict, total=False):
    user_request: str
    brief_path: str
    project_path: str
    team_members: list[str]
    deadline: str
    llm_model: str

    provided_inputs: list[str]
    validation_issues: list[str]
    project_type: str

    brief_summary: str
    brief_requirements: list[str]
    technical_constraints: list[str]
    grading_signals: list[str]

    repo_summary: str
    repo_findings: dict[str, Any]
    present_artifacts: list[str]
    missing_artifacts: list[str]

    risks: list[str]
    recommended_actions: list[str]
    member_assignments: list[str]
    demo_checklist: list[str]
    report_outline: list[str]
    final_report_path: str

    logs: list[LogEntry]


def ensure_defaults(state: ProjectState) -> ProjectState:
    """Ensure all commonly used state fields exist before the workflow runs."""
    state.setdefault("provided_inputs", [])
    state.setdefault("validation_issues", [])
    state.setdefault("brief_requirements", [])
    state.setdefault("technical_constraints", [])
    state.setdefault("grading_signals", [])
    state.setdefault("repo_findings", {})
    state.setdefault("present_artifacts", [])
    state.setdefault("missing_artifacts", [])
    state.setdefault("risks", [])
    state.setdefault("recommended_actions", [])
    state.setdefault("member_assignments", [])
    state.setdefault("demo_checklist", [])
    state.setdefault("report_outline", [])
    state.setdefault("logs", [])
    return state


def make_log_entry(
    *,
    agent: str,
    level: Literal["INFO", "WARNING", "ERROR"],
    message: str,
    details: dict[str, Any] | None = None,
) -> LogEntry:
    """Create a structured state log entry."""
    entry: LogEntry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "level": level,
        "message": message,
    }
    if details:
        entry["details"] = details
    return entry