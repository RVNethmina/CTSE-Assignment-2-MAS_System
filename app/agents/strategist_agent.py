from __future__ import annotations

from app.models.state import ProjectState, ensure_defaults, make_log_entry
from app.tools.rescue_plan_writer import write_rescue_outputs
from app.utils.logger import setup_logger


def strategist_agent_node(state: ProjectState) -> ProjectState:
    """
    Risk and Delivery Strategist Agent.

    Compares brief requirements with repository evidence, identifies risks,
    creates an action plan, assigns work, and writes the final rescue report.
    """
    logger = setup_logger()
    state = ensure_defaults(state)

    logger.info("Strategist agent started.")

    missing_artifacts = state.get("missing_artifacts", [])
    brief_requirements = state.get("brief_requirements", [])
    technical_constraints = state.get("technical_constraints", [])

    risks: list[str] = []
    actions: list[str] = []
    assignments: list[str] = []
    checklist: list[str] = []
    outline: list[str] = []

    if "source_code" in missing_artifacts:
        risks.append("No source code evidence was detected in the provided project folder.")
        actions.append("Add the main implementation files for the MAS agents, tools, and workflow.")

    if "tests" in missing_artifacts:
        risks.append("Testing evidence is missing, which can reduce marks for evaluation quality.")
        actions.append("Create automated tests for each agent and one integration test for the full workflow.")

    if "documentation" in missing_artifacts:
        risks.append("Documentation evidence is missing, which weakens repo clarity and final submission quality.")
        actions.append("Add a README and project documentation explaining setup, workflow, and usage.")

    if "configuration" in missing_artifacts:
        risks.append("Configuration or dependency evidence is missing, making the project harder to run and assess.")
        actions.append("Add clear dependency and configuration files such as requirements.txt or pyproject.toml.")

    if brief_requirements:
        actions.append("Cross-check the implemented system against all extracted assignment requirements.")
    if technical_constraints:
        actions.append("Verify the project runs fully locally and does not depend on paid APIs.")

    assignments = [
        "Student 1: Finalize Intake and Scope Agent and input validation tests.",
        "Student 2: Finalize Brief and Rubric Analyst Agent and brief extraction tests.",
        "Student 3: Finalize Repository and Evidence Auditor Agent and repo audit tests.",
        "Student 4: Finalize Risk and Delivery Strategist Agent, report generation, and integration checks.",
    ]

    checklist = [
        "Run the full workflow locally using Ollama.",
        "Show all 4 agents executing in sequence.",
        "Demonstrate tool usage clearly.",
        "Show logs or tracing output.",
        "Open the generated rescue report file.",
        "Keep the demo under 5 minutes.",
    ]

    outline = [
        "Introduction and problem domain",
        "Why a multi-agent system is needed",
        "System architecture and workflow diagram",
        "Agent roles and responsibilities",
        "Custom tools and their usage",
        "State management design",
        "Observability and logging",
        "Testing and evaluation strategy",
        "Individual contributions",
        "Challenges and lessons learned",
    ]

    state["risks"] = risks
    state["recommended_actions"] = actions
    state["member_assignments"] = assignments
    state["demo_checklist"] = checklist
    state["report_outline"] = outline

    write_result = write_rescue_outputs(state)

    state["final_report_path"] = write_result.markdown_path

    if write_result.issues:
        state["validation_issues"].extend(write_result.issues)

    logger.info("Strategist agent completed successfully.")

    state["logs"].append(
        make_log_entry(
            agent="RiskAndDeliveryStrategistAgent",
            level="INFO",
            message="Rescue strategy generated and output files written.",
            details={
                "risks_count": len(risks),
                "actions_count": len(actions),
                "markdown_path": write_result.markdown_path,
                "json_path": write_result.json_path,
            },
        )
    )

    return state