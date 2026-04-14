from __future__ import annotations

from app.models.state import ProjectState, ensure_defaults, make_log_entry
from app.tools.rescue_plan_writer import write_rescue_outputs
from app.utils.logger import setup_logger

def _dedupe_keep_order(items: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""
    seen: set[str] = set()
    result: list[str] = []

    for item in items:
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)

    return result


def _calculate_readiness_score(
    *,
    agent_file_count: int,
    tool_file_count: int,
    test_file_count: int,
    has_logging_evidence: bool,
    has_output_writer_evidence: bool,
    missing_artifacts: list[str],
) -> int:
    """Calculate a simple submission readiness score out of 100."""
    score = 100

    if "insufficient_agents" in missing_artifacts or agent_file_count < 3:
        score -= 25

    if "tests" in missing_artifacts or test_file_count == 0:
        score -= 25

    if "missing_logging" in missing_artifacts or not has_logging_evidence:
        score -= 20

    if "missing_output_writer" in missing_artifacts or not has_output_writer_evidence:
        score -= 15

    if "missing_tools" in missing_artifacts or tool_file_count < 1:
        score -= 15

    return max(score, 0)


def _build_dynamic_assignments(
    *,
    missing_artifacts: list[str],
    agent_file_count: int,
    tool_file_count: int,
    test_file_count: int,
    has_logging_evidence: bool,
    has_output_writer_evidence: bool,
) -> list[str]:
    """Generate team ownership suggestions based on actual project gaps."""
    assignments: list[str] = []

    if "insufficient_agents" in missing_artifacts or agent_file_count < 3:
        assignments.append(
            "Student 1: Build the missing agent modules so the system reaches the required 3 to 4 distinct agents."
        )
    else:
        assignments.append(
            "Student 1: Refine the Intake and Scope Agent and improve input validation edge cases."
        )

    if "tests" in missing_artifacts or test_file_count == 0:
        assignments.append(
            "Student 2: Create per-agent tests and one integration test for the full workflow."
        )
    else:
        assignments.append(
            "Student 2: Expand evaluation coverage with stronger edge-case and failure-path tests."
        )

    if "missing_tools" in missing_artifacts or tool_file_count < 1:
        assignments.append(
            "Student 3: Build the missing custom tool layer and connect tool usage clearly to the agents."
        )
    elif "missing_logging" in missing_artifacts or not has_logging_evidence:
        assignments.append(
            "Student 3: Implement structured logging or tracing and make it clearly visible in the demo."
        )
    else:
        assignments.append(
            "Student 3: Improve repository auditing depth and observability quality."
        )

    if "missing_output_writer" in missing_artifacts or not has_output_writer_evidence:
        assignments.append(
            "Student 4: Implement final output/report generation and polish the rescue report for submission."
        )
    else:
        assignments.append(
            "Student 4: Polish the final report, demo flow, and submission packaging."
        )

    return assignments


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
    repo_audit = state.get("repo_findings", {}).get("repo_audit", {})
    agent_file_count = int(repo_audit.get("agent_file_count", 0))
    tool_file_count = int(repo_audit.get("tool_file_count", 0))
    test_file_count = int(repo_audit.get("test_file_count", 0))
    has_logging_evidence = bool(repo_audit.get("has_logging_evidence", False))
    has_output_writer_evidence = bool(repo_audit.get("has_output_writer_evidence", False))
    brief_requirements = state.get("brief_requirements", [])
    technical_constraints = state.get("technical_constraints", [])

    risks: list[str] = []
    actions: list[str] = []
    assignments: list[str] = []
    blockers: list[str] = []   
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
    
    if "insufficient_agents" in missing_artifacts or agent_file_count < 3:
        risks.append(
            f"Only {agent_file_count} agent file(s) were detected, which may fail the 3 to 4 agent requirement."
        )
        actions.append("Implement at least 3 to 4 distinct agent modules with clear responsibilities.")

    if "missing_tools" in missing_artifacts or tool_file_count < 1:
        risks.append("No strong custom tool evidence was detected.")
        actions.append("Add at least one meaningful custom Python tool that interacts with files, terminal, database, or APIs.")

    if "missing_logging" in missing_artifacts or not has_logging_evidence:
        risks.append("Logging or tracing evidence is missing, which weakens observability marks.")
        actions.append("Implement structured logging or tracing and show it clearly in the demo.")

    if test_file_count == 0:
        risks.append("No test files were detected in the repository.")
        actions.append("Add per-agent tests and one workflow integration test.")

    if brief_requirements:
        actions.append("Cross-check the implemented system against all extracted assignment requirements.")

    if technical_constraints:
        actions.append("Verify the project runs fully locally and does not depend on paid APIs.")

    if "insufficient_agents" in missing_artifacts or agent_file_count < 3:
        blockers.append("Agent count is below the required 3 to 4 distinct agents.")

    if "tests" in missing_artifacts or test_file_count == 0:
        blockers.append("Automated testing evidence is missing.")

    if "missing_logging" in missing_artifacts or not has_logging_evidence:
        blockers.append("Logging or tracing evidence is missing.")

    if "missing_output_writer" in missing_artifacts or not has_output_writer_evidence:
        blockers.append("Final output/report generation evidence is missing.")

    risks = _dedupe_keep_order(risks)
    actions = _dedupe_keep_order(actions)
    blockers = _dedupe_keep_order(blockers)

    assignments = _build_dynamic_assignments(
        missing_artifacts=missing_artifacts,
        agent_file_count=agent_file_count,
        tool_file_count=tool_file_count,
        test_file_count=test_file_count,
        has_logging_evidence=has_logging_evidence,
        has_output_writer_evidence=bool(repo_audit.get("has_output_writer_evidence", False)),
    )

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
    state["blockers"] = blockers
    state["readiness_score"] = _calculate_readiness_score(
        agent_file_count=agent_file_count,
        tool_file_count=tool_file_count,
        test_file_count=test_file_count,
        has_logging_evidence=has_logging_evidence,
        has_output_writer_evidence=bool(repo_audit.get("has_output_writer_evidence", False)),
        missing_artifacts=missing_artifacts,
    )
    state["member_assignments"] = assignments
    state["demo_checklist"] = checklist
    state["report_outline"] = outline

    output_dir = "outputs"
    markdown_path = f"{output_dir}\\rescue_report.md"
    json_path = f"{output_dir}\\rescue_report.json"

    state["final_report_path"] = markdown_path

    state["logs"].append(
        make_log_entry(
            agent="RiskAndDeliveryStrategistAgent",
            level="INFO",
            message="Rescue strategy generated and output files written.",
            details={
                "risks_count": len(risks),
                "actions_count": len(actions),
                "blockers_count": len(blockers),
                "readiness_score": state["readiness_score"],
                "markdown_path": markdown_path,
                "json_path": json_path,
            },
        )
    )

    write_result = write_rescue_outputs(state, output_dir=output_dir)

    if write_result.issues:
        state["validation_issues"].extend(write_result.issues)

    logger.info("Strategist agent completed successfully.")

    return state