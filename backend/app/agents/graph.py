from langgraph.graph import END, START, StateGraph

from app.agents.nodes import build_content_request, choose_focus, choose_strategy, retrieve_content
from app.agents.state import AgentState


def build_agent_graph():
    builder = StateGraph(AgentState)
    builder.add_node("choose_strategy", choose_strategy)
    builder.add_node("choose_focus", choose_focus)
    builder.add_node("build_content_request", build_content_request)
    builder.add_node("retrieve_content", retrieve_content)

    builder.add_edge(START, "choose_strategy")
    builder.add_edge("choose_strategy", "choose_focus")
    builder.add_edge("choose_focus", "build_content_request")
    builder.add_edge("build_content_request", "retrieve_content")
    builder.add_edge("retrieve_content", END)

    return builder.compile()

agent_graph = build_agent_graph()