from __future__ import annotations

from app.models.state import ProjectState, ensure_defaults, make_log_entry
from app.tools.repo_audit import audit_repository
from app.utils.logger import setup_logger


def repo_auditor_agent_node(state: ProjectState) -> ProjectState:
    """
    Repository and Evidence Auditor Agent.

    Scans the project folder, summarizes repository evidence, and records
    present and missing artifacts for downstream planning.
    """
    logger = setup_logger()
    state = ensure_defaults(state)

    project_path = state.get("project_path", "")

    logger.info("Repository auditor agent started.")

    audit_result = audit_repository(project_path=project_path)

    repo_findings = state.get("repo_findings", {})
    repo_findings["repo_audit"] = audit_result.to_dict()
    state["repo_findings"] = repo_findings

    if audit_result.issues:
        state["validation_issues"].extend(audit_result.issues)

    state["repo_summary"] = (
        f"Project contains {audit_result.total_files} files and "
        f"{audit_result.total_directories} directories. "
        f"Detected artifacts: {', '.join(audit_result.detected_artifacts) or 'none'}. "
        f"Agent files: {audit_result.agent_file_count}, "
        f"Tool files: {audit_result.tool_file_count}, "
        f"Test files: {audit_result.test_file_count}, "
        f"Logging evidence: {'yes' if audit_result.has_logging_evidence else 'no'}, "
        f"Output writer evidence: {'yes' if audit_result.has_output_writer_evidence else 'no'}."
    )

    state["present_artifacts"] = audit_result.detected_artifacts.copy()
    state["missing_artifacts"] = []

    expected_artifacts = {
        "source_code",
        "tests",
        "documentation",
        "configuration",
    }

    for artifact in sorted(expected_artifacts):
        if artifact not in audit_result.detected_artifacts:
            state["missing_artifacts"].append(artifact)

    if audit_result.agent_file_count < 3:
        state["missing_artifacts"].append("insufficient_agents")

    if audit_result.tool_file_count < 1:
        state["missing_artifacts"].append("missing_tools")

    if not audit_result.has_logging_evidence:
        state["missing_artifacts"].append("missing_logging")

    if not audit_result.has_output_writer_evidence:
        state["missing_artifacts"].append("missing_output_writer")

    logger.info("Repository auditor agent completed successfully.")

    state["logs"].append(
        make_log_entry(
            agent="RepositoryAndEvidenceAuditorAgent",
            level="INFO",
            message="Repository audit completed.",
            details={
                "total_files": audit_result.total_files,
                "total_directories": audit_result.total_directories,
                "detected_artifacts": audit_result.detected_artifacts,
                "missing_artifacts": state["missing_artifacts"],
                "repo_audit": state.get("repo_findings", {}).get("repo_audit", {}),
                "agent_file_count": audit_result.agent_file_count,
                "tool_file_count": audit_result.tool_file_count,
                "test_file_count": audit_result.test_file_count,
                "has_logging_evidence": audit_result.has_logging_evidence,
            },
        )
    )

    return state