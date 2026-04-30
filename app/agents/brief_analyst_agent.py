from __future__ import annotations

import json
import re
from typing import Any

from langchain_ollama import ChatOllama

from app.models.state import ProjectState, ensure_defaults, make_log_entry
from app.tools.brief_parser import parse_assignment_brief
from app.utils.logger import setup_logger


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences if the model wraps JSON in them."""
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    return cleaned.strip()


def _extract_first_json_object(text: str) -> dict[str, Any] | None:
    """Extract and parse the first JSON object found in a model response."""
    cleaned = _strip_code_fences(text)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        return None

    candidate = match.group(0)
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return None

    return None


def _unique_non_empty(items: list[str]) -> list[str]:
    """Return unique non-empty strings while preserving order."""
    results: list[str] = []
    seen: set[str] = set()

    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        results.append(cleaned)

    return results


def _heuristic_fallback(brief_text: str) -> dict[str, Any]:
    """
    Fallback extractor used when the local model does not return valid JSON.

    This is intentionally simple but deterministic.
    """
    lines = [line.strip("*- ").strip() for line in brief_text.splitlines()]
    lines = [line for line in lines if line]

    requirement_keywords = (
        "must",
        "should",
        "required",
        "include",
        "implement",
        "submit",
        "build",
        "design",
        "deploy",
    )
    technical_keywords = (
        "local",
        "locally",
        "ollama",
        "langgraph",
        "crewai",
        "autogen",
        "python",
        "tool",
        "api",
        "state",
        "logging",
        "tracing",
    )
    grading_keywords = (
        "%",
        "criteria",
        "assessment",
        "excellent",
        "good",
        "average",
        "poor",
        "weight",
    )

    requirements: list[str] = []
    technical_constraints: list[str] = []
    grading_signals: list[str] = []

    for line in lines:
        lower = line.lower()

        if any(keyword in lower for keyword in requirement_keywords):
            requirements.append(line)

        if any(keyword in lower for keyword in technical_keywords):
            technical_constraints.append(line)

        if any(keyword in lower for keyword in grading_keywords):
            grading_signals.append(line)

    summary = " ".join(lines[:5])[:500]

    return {
        "brief_summary": summary or "Brief parsed, but summary could not be generated.",
        "brief_requirements": _unique_non_empty(requirements)[:15],
        "technical_constraints": _unique_non_empty(technical_constraints)[:15],
        "grading_signals": _unique_non_empty(grading_signals)[:15],
    }


def _run_llm_extraction(brief_text: str, model_name: str) -> dict[str, Any] | None:
    """Call the local Ollama model and request structured brief extraction."""
    llm = ChatOllama(model=model_name, temperature=0)

    prompt = f"""
You are the Brief and Rubric Analyst Agent in a local multi-agent system.

Read the assignment brief below and extract only what is explicitly supported by the text.

Return ONLY valid JSON with exactly these keys:
- brief_summary: string
- brief_requirements: array of strings
- technical_constraints: array of strings
- grading_signals: array of strings

Rules:
- Do not include markdown.
- Do not include explanations outside JSON.
- Do not invent missing requirements.
- Keep each list item short and specific.

Assignment brief:
\"\"\"
{brief_text[:12000]}
\"\"\"
""".strip()

    response = llm.invoke(prompt)
    content = response.content if isinstance(response.content, str) else str(response.content)

    return _extract_first_json_object(content)


def brief_analyst_agent_node(state: ProjectState) -> ProjectState:
    """
    Brief and Rubric Analyst Agent.

    Parses the assignment brief using a local tool, then uses the local Ollama model
    to extract a structured summary, requirements, constraints, and grading signals.
    """
    logger = setup_logger()
    state = ensure_defaults(state)

    brief_path = state.get("brief_path", "")
    model_name = state.get("llm_model", "llama3")

    logger.info("Brief analyst agent started.")

    parsed_brief = parse_assignment_brief(source_path=brief_path)

    repo_findings = state.get("repo_findings", {})
    repo_findings["brief_parse"] = parsed_brief.to_dict()
    state["repo_findings"] = repo_findings

    if parsed_brief.issues:
        state["validation_issues"].extend(parsed_brief.issues)

    if not parsed_brief.content:
        logger.warning("Brief analyst agent could not extract brief content.")
        state["logs"].append(
            make_log_entry(
                agent="BriefAndRubricAnalystAgent",
                level="WARNING",
                message="Brief parsing failed or returned empty content.",
                details={"issues": parsed_brief.issues},
            )
        )
        return state

    structured_result: dict[str, Any] | None = None
    used_fallback = False

    try:
        structured_result = _run_llm_extraction(
            brief_text=parsed_brief.content,
            model_name=model_name,
        )
    except Exception as exc:
        logger.warning("LLM extraction failed. Falling back to heuristic extraction.")
        state["validation_issues"].append(f"LLM extraction failed: {exc}")
        used_fallback = True

    if not structured_result:
        structured_result = _heuristic_fallback(parsed_brief.content)
        used_fallback = True

    state["brief_summary"] = str(
        structured_result.get("brief_summary", "No summary generated.")
    )

    state["brief_requirements"] = _unique_non_empty(
        [str(item) for item in structured_result.get("brief_requirements", [])]
    )
    state["technical_constraints"] = _unique_non_empty(
        [str(item) for item in structured_result.get("technical_constraints", [])]
    )
    state["grading_signals"] = _unique_non_empty(
        [str(item) for item in structured_result.get("grading_signals", [])]
    )

    logger.info("Brief analyst agent completed successfully.")

    state["logs"].append(
        make_log_entry(
            agent="BriefAndRubricAnalystAgent",
            level="INFO",
            message="Brief analysis completed.",
            details={
                "used_fallback": used_fallback,
                "requirements_count": len(state["brief_requirements"]),
                "technical_constraints_count": len(state["technical_constraints"]),
                "grading_signals_count": len(state["grading_signals"]),
            },
        )
    )

    return state
