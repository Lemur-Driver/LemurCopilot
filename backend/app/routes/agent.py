from fastapi import APIRouter, Depends, HTTPException

from app.agents.runner import run_agent_for_student
from app.dependencies import get_current_student
from app.models import Student
from app.prompts.lesson_prompts import LESSON_CONFIGS
from app.services.progress_service import is_topic_unlocked


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post("/{topic}/plan")
async def create_agent_plan(
    topic: str,
    student: Student = Depends(get_current_student),
):
    if topic not in LESSON_CONFIGS:
        raise HTTPException(
            status_code=404,
            detail=f"No existe configuración pedagógica para {topic}",
        )

    if not is_topic_unlocked(student, topic):
        raise HTTPException(
            status_code=403,
            detail="Debes completar la unidad anterior antes de acceder a esta clase.",
        )

    result = await run_agent_for_student(student, topic)

    return {
        "topic": result["topic"],
        "strategy": result["strategy"],
        "decisionReason": result["decision_reason"],
        "focusConcepts": result["focus_concepts"],
        "focusReason": result["focus_reason"],
        "contentRequest": result["content_request"],
    }