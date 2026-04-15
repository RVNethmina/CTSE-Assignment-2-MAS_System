"""
LLM-as-a-Judge evaluation test.

Validates brief analyst output quality using the local Ollama model as an
automated judge.  This test requires a running Ollama instance with the
``llama3`` model pulled.

Run selectively with:
    pytest -m llm_judge          # only this test
    pytest -m "not llm_judge"    # skip this test in CI
"""
from __future__ import annotations

import json

import pytest

from app.agents import brief_analyst_agent
from app.models.state import ProjectState

JUDGE_PROMPT = """
You are an evaluation judge. Given the agent output below, answer ONLY with
a JSON object: {{"pass": true/false, "reason": "..."}}

Rules the output must satisfy:
1. brief_summary must be a non-empty string
2. brief_requirements must be a list with at least 1 item
3. technical_constraints must be a list with at least 1 item
4. No item in any list should be an empty string

Output to evaluate:
{output}
"""


@pytest.mark.llm_judge
def test_brief_analyst_output_quality_via_llm_judge(
    sample_brief_file,
    minimal_project_dir,
    monkeypatch,
) -> None:
    """LLM-as-a-judge: validates brief analyst output quality using Ollama."""
    from langchain_ollama import ChatOllama

    state: ProjectState = {
        "brief_path": str(sample_brief_file),
        "project_path": str(minimal_project_dir),
        "llm_model": "llama3",
        "validation_issues": [],
        "repo_findings": {},
        "logs": [],
    }

    result = brief_analyst_agent.brief_analyst_agent_node(state)

    output_to_judge = {
        "brief_summary": result.get("brief_summary"),
        "brief_requirements": result.get("brief_requirements"),
        "technical_constraints": result.get("technical_constraints"),
    }

    llm = ChatOllama(model="llama3", temperature=0)
    response = llm.invoke(JUDGE_PROMPT.format(output=json.dumps(output_to_judge)))

    # Strip fences and parse
    text = response.content.strip().strip("```json").strip("```").strip()
    verdict = json.loads(text)

    assert verdict["pass"] is True, f"LLM judge failed: {verdict['reason']}"
