from app.agents.graph import agent_graph
from app.agents.profile import build_agent_profile
from app.agents.state import AgentState
from app.models import Student


async def run_agent_for_student(student: Student, topic: str) -> AgentState:
    learner_profile = build_agent_profile(student, topic)

    return await agent_graph.ainvoke({
        "topic": topic,
        "learner_profile": learner_profile,
    })