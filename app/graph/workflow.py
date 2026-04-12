from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.intake_agent import intake_agent_node
from app.models.state import ProjectState


def build_workflow():
    """Build the initial LangGraph workflow with the first intake node."""
    graph_builder = StateGraph(ProjectState)

    graph_builder.add_node("intake_agent", intake_agent_node)
    graph_builder.set_entry_point("intake_agent")
    graph_builder.add_edge("intake_agent", END)

    return graph_builder.compile()