from app.agents.graph import agent_graph
from app.agents.profile import build_agent_profile
from app.agents.state import AgentState
from app.models import Student
from app.prompts.lesson_prompts import LESSON_CONFIGS
from app.services.agent_activity_service import get_recent_quiz_activity

async def run_agent_for_student(student: Student, topic: str) -> AgentState:
    
    if not isinstance(topic, str) or topic not in LESSON_CONFIGS:
        raise ValueError(f"El tema {topic!r} no existe en la configuración pedagógica")

    learner_profile = build_agent_profile(student, topic)
    
    learner_profile["recent_quiz_activity"] = await get_recent_quiz_activity(student.id)

    return await agent_graph.ainvoke({
        "topic": topic,
        "learner_profile": learner_profile,
    })