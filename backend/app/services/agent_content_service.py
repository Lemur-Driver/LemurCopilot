import math
from typing import Any

from app.services.content_release_service import (
    get_published_lesson,
    get_published_release_id,
)
from app.services.question_pool_service import (
    QUIZ_SIZE,
    _pool_documents,
    _stored_question_consistent,
)


TARGET_DIFFICULTY = {
    "reinforcement": 0.4,
    "standard": 0.5,
    "challenge": 0.7,
}


def _eligible_exercises(
    exercises: list[dict[str, Any]],
    topic: str,
    release_id: str,
) -> list[dict[str, Any]]:
    return [
        exercise
        for exercise in exercises
        if exercise.get("topic") == topic
        and exercise.get("release_id") == release_id
        and exercise.get("status") == "published"
        and exercise.get("verified") is True
        and exercise.get("review_status") in (None, "approved")
        and exercise.get("_id") is not None
        and _stored_question_consistent(exercise)
        and isinstance(exercise.get("difficulty"), (int, float))
        and not isinstance(exercise.get("difficulty"), bool)
        and math.isfinite(exercise["difficulty"])
        and 0 <= exercise["difficulty"] <= 1
    ]


def _rank_exercises(
    exercises: list[dict[str, Any]],
    focus_concepts: list[str],
    target_difficulty: float,
) -> list[dict[str, Any]]:
    remaining = list(exercises)
    ranked = []
    covered_concepts: set[str] = set()
    focus = {concept for concept in focus_concepts if isinstance(concept, str)}

    def concepts_for(exercise: dict[str, Any]) -> set[str]:
        tags = exercise.get("concept_tags", [])
        if not isinstance(tags, list):
            return set()
        return {tag for tag in tags if isinstance(tag, str)}

    def served_count(exercise: dict[str, Any]) -> float:
        value = exercise.get("times_served", 0)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            return 0
        return value

    while remaining:
        remaining.sort(key=lambda exercise: (
            -len((concepts_for(exercise) & focus) - covered_concepts),
            served_count(exercise),
            abs(exercise["difficulty"] - target_difficulty),
            str(exercise["_id"]),
        ))
        selected = remaining.pop(0)
        ranked.append(selected)
        covered_concepts.update(concepts_for(selected) & focus)

    return ranked


async def retrieve_agent_content(
    topic: str,
    strategy: str,
    focus_concepts: list[str],
) -> dict[str, Any]:
    release_id = await get_published_release_id(topic)
    if not release_id:
        return {
            "release_id": None,
            "lesson": None,
            "lesson_variant": None,
            "exercises": [],
            "content_errors": [f"No hay contenido publicado para {topic}."],
        }

    lesson_variant = strategy
    lesson = await get_published_lesson(topic, lesson_variant, release_id)
    if lesson is None and lesson_variant != "standard":
        lesson_variant = "standard"
        lesson = await get_published_lesson(topic, lesson_variant, release_id)

    if lesson is None:
        errors = [f"No hay una lección verificada y publicada para {topic} en el release activo."]
    else:
        errors = []

    pool = await _pool_documents(topic, release_id)
    eligible = _eligible_exercises(pool, topic, release_id)
    target_difficulty = TARGET_DIFFICULTY.get(strategy, TARGET_DIFFICULTY["standard"])
    selected = _rank_exercises(eligible, focus_concepts, target_difficulty)[:QUIZ_SIZE]

    if len(selected) < QUIZ_SIZE:
        errors.append(
            f"Pool insuficiente para {topic}: hay {len(selected)} preguntas verificadas y publicadas; se requieren {QUIZ_SIZE}."
        )

    return {
        "release_id": release_id,
        "lesson": lesson,
        "lesson_variant": lesson_variant if lesson is not None else None,
        "exercises": selected if not errors else [],
        "content_errors": errors,
    }
