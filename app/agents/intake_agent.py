from __future__ import annotations

from app.models.state import ProjectState, ensure_defaults, make_log_entry
from app.tools.project_input_validator import validate_project_inputs
from app.utils.logger import setup_logger
from app.agents.profiles import AGENT_PROFILES


def _run_intake_reasoning(
    validation_issues: list[str],
    project_type: str,
    model_name: str,
) -> str:
    """Use local LLM to generate a plain-language summary of intake validation."""
    from langchain_ollama import ChatOllama

    profile = AGENT_PROFILES["IntakeAndScopeAgent"]
    llm = ChatOllama(model=model_name, temperature=0)

    issues_text = "\n".join(f"- {i}" for i in validation_issues) if validation_issues else "- None"

    prompt = f"""
{profile["system_prompt"]}

Summarize the intake validation results below in 2-3 sentences.
Be direct. Do not invent new issues.

Detected project type: {project_type}
Validation issues:
{issues_text}

Return only the summary text, no markdown, no preamble.
""".strip()

    response = llm.invoke(prompt)
    return response.content.strip() if isinstance(response.content, str) else ""


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

    # --- LLM reasoning step ---
    model_name = state.get("llm_model", "llama3")
    try:
        state["intake_summary"] = _run_intake_reasoning(
            validation_issues=result.issues,
            project_type=result.likely_stack,
            model_name=model_name,
        )
    except Exception:
        state["intake_summary"] = "Intake summary could not be generated."

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