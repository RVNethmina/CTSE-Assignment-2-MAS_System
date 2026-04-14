from __future__ import annotations

from app.models.state import ProjectState, ensure_defaults, make_log_entry
from app.tools.project_input_validator import validate_project_inputs
from app.utils.logger import setup_logger
from app.agents.profiles import AGENT_PROFILES


def intake_agent_node(state: ProjectState) -> ProjectState:
    """
    Intake and Scope Agent.

    Validates the provided brief and project path, initializes key state fields,
    and records structured logs for observability.
    """
    logger = setup_logger()
    state = ensure_defaults(state)
    
    if not state.get("agent_profiles"):
        state["agent_profiles"] = AGENT_PROFILES.copy()

    brief_path = state.get("brief_path", "")
    project_path = state.get("project_path", "")

    logger.info("Intake agent started.")

    result = validate_project_inputs(brief_path=brief_path, project_path=project_path)

    state["provided_inputs"] = [brief_path, project_path]
    state["validation_issues"] = result.issues
    state["project_type"] = result.likely_stack

    repo_findings = state.get("repo_findings", {})
    repo_findings["intake_validation"] = result.to_dict()
    state["repo_findings"] = repo_findings

    if result.issues:
        logger.warning("Intake agent found validation issues.")
        state["logs"].append(
            make_log_entry(
                agent="IntakeAndScopeAgent",
                level="WARNING",
                message="Input validation completed with issues.",
                details={
                    "issues": result.issues,
                    "likely_stack": result.likely_stack,
                },
            )
        )
    else:
        logger.info("Intake agent validated inputs successfully.")
        state["logs"].append(
            make_log_entry(
                agent="IntakeAndScopeAgent",
                level="INFO",
                message="Input validation completed successfully.",
                details={
                    "likely_stack": result.likely_stack,
                    "project_is_git_repo": result.project_is_git_repo,
                },
            )
        )

    return state