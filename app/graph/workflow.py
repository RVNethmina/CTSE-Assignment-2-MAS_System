from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.brief_analyst_agent import brief_analyst_agent_node
from app.agents.intake_agent import intake_agent_node
from app.agents.repo_auditor_agent import repo_auditor_agent_node
from app.agents.strategist_agent import strategist_agent_node
from app.models.state import ProjectState


def build_workflow():
    """Build the workflow with intake, brief analysis, repo audit, and strategy generation."""
    graph_builder = StateGraph(ProjectState)

    graph_builder.add_node("intake_agent", intake_agent_node)
    graph_builder.add_node("brief_analyst_agent", brief_analyst_agent_node)
    graph_builder.add_node("repo_auditor_agent", repo_auditor_agent_node)
    graph_builder.add_node("strategist_agent", strategist_agent_node)

    graph_builder.set_entry_point("intake_agent")
    graph_builder.add_edge("intake_agent", "brief_analyst_agent")
    graph_builder.add_edge("brief_analyst_agent", "repo_auditor_agent")
    graph_builder.add_edge("repo_auditor_agent", "strategist_agent")
    graph_builder.add_edge("strategist_agent", END)

    return graph_builder.compile()