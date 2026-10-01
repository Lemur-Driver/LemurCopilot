import json

from app.models import Student, get_mastery_entry
from app.prompts.lesson_prompts import LESSON_SEQUENCE


def build_student_profile(student: Student, topic: str) -> dict:
    current = get_mastery_entry(student.mastery, topic)
    topic_index = LESSON_SEQUENCE.index(topic) if topic in LESSON_SEQUENCE else len(LESSON_SEQUENCE)
    previous_topics = LESSON_SEQUENCE[:topic_index]

    previous_mastery = {
        previous_topic: get_mastery_entry(student.mastery, previous_topic).model_dump(mode="json")
        for previous_topic in previous_topics
        if get_mastery_entry(student.mastery, previous_topic)
    }
    failed_questions = list(current.failed_questions) if current else []
    last_score = current.last_score if current else None

    if last_score is None:
        difficulty = "standard"
        tone = "clear explanation with practical examples"
    elif last_score < 0.6:
        difficulty = "reinforcement"
        tone = "slower explanation with extra examples"
    elif last_score >= 0.85:
        difficulty = "challenge"
        tone = "deeper application and comparison"
    else:
        difficulty = "standard"
        tone = "clear explanation with practical examples"

    return {
        "topic": topic,
        "current_mastery": current.model_dump(mode="json") if current else None,
        "previous_mastery": previous_mastery,
        "failed_questions": failed_questions[-10:],
        "difficulty": difficulty,
        "tone": tone,
    }


def render_profile_block(profile: dict | None) -> str:
    if not profile or (profile.get("current_mastery") is None and not profile.get("previous_mastery")):
        return "PERFIL DEL ESTUDIANTE: No hay historial disponible. Utiliza el enfoque estándar."

    return (
        "PERFIL DEL ESTUDIANTE (solo adapta énfasis, profundidad, ejemplos y dificultad; "
        "no es una fuente de hechos):\n"
        + json.dumps(profile, ensure_ascii=False, indent=2, default=str)
    )
