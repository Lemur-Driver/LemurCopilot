import math
from typing import Any

from app.agents.state import AgentState
from app.services.agent_content_service import retrieve_agent_content


def choose_strategy(state: AgentState) -> dict[str, Any]:
    profile = state.get("learner_profile", {})
    mastery = profile.get("current_mastery") or {}
    last_score = mastery.get("last_score")

    if last_score is None:
        last_score = next((
            activity.get("score")
            for activity in profile.get("recent_quiz_activity", [])
            if isinstance(activity, dict)
            and activity.get("topic") == state.get("topic")
            and activity.get("score") is not None
        ), None)

    if (
        not isinstance(last_score, (int, float))
        or isinstance(last_score, bool)
        or not math.isfinite(last_score)
        or not 0 <= last_score <= 1
    ):
        return {
            "strategy": "standard",
            "decision_reason": "No hay una nota reciente válida; se usa la estrategia estándar.",
        }

    if last_score < 0.6:
        return {
            "strategy": "reinforcement",
            "decision_reason": f"La última nota fue {last_score:.0%}; se prioriza el refuerzo.",
        }

    if last_score >= 0.85:
        return {
            "strategy": "challenge",
            "decision_reason": f"La última nota fue {last_score:.0%}; se propone un desafío.",
        }

    return {
        "strategy": "standard",
        "decision_reason": f"La última nota fue {last_score:.0%}; se mantiene la estrategia estándar.",
    }


def choose_focus(state: AgentState) -> dict[str, Any]:
    profile = state.get("learner_profile", {})
    weak_concepts = profile.get("weak_concepts", [])

    focus_concepts = [
        concept["tag"]
        for concept in weak_concepts
        if isinstance(concept, dict)
        and isinstance(concept.get("tag"), str)
        and concept["tag"].strip()
    ]

    if not focus_concepts:
        return {
            "focus_concepts": [],
            "focus_reason": "No hay conceptos débiles registrados; no se fija un foco.",
        }

    return {
        "focus_concepts": focus_concepts,
        "focus_reason": "Se priorizan los conceptos con menor mastery del perfil.",
    }

def build_content_request(state: AgentState) -> dict[str, Any]:
    return {
        "content_request": {
            "topic": state["topic"],
            "lesson_variant": state["strategy"],
            "focus_concepts": state.get("focus_concepts", []),
            "question_count": 3,
        }
    }


async def retrieve_content(state: AgentState) -> dict[str, Any]:
    try:
        return await retrieve_agent_content(
            topic=state["topic"],
            strategy=state["strategy"],
            focus_concepts=state.get("focus_concepts", []),
        )
    except Exception as error:
        return {
            "release_id": None,
            "lesson": None,
            "lesson_variant": None,
            "exercises": [],
            "content_errors": [f"Falló la recuperación de contenido: {type(error).__name__}"],
        }