from collections.abc import Awaitable, Callable

from bson import ObjectId

from app.database import exercises_collection, sessions_collection
from app.models import Exercise

GenerateExerciseFn = Callable[[str, float], Awaitable[Exercise]]

DIFFICULTY_TOLERANCE = 0.15 
MAX_TIMES_SERVED = 20  


async def _already_seen_exercise_ids(student_id: str) -> set[str]:
    """IDs de ejercicios que el estudiante ya respondió, para no repetírselos."""
    cursor = sessions_collection.find(
        {"student_id": ObjectId(student_id)},
        {"exercises_attempted.exercise_id": 1},
    )
    seen: set[str] = set()
    async for session in cursor:
        for attempt in session.get("exercises_attempted", []):
            seen.add(str(attempt["exercise_id"]))
    return seen


async def get_exercise_for_student(
    student_id: str,
    concept_id: str,
    target_difficulty: float,
    generate_fn: GenerateExerciseFn,
) -> Exercise:
    seen_ids = await _already_seen_exercise_ids(student_id)

    candidate = await exercises_collection.find_one(
        {
            "concept_id": ObjectId(concept_id),
            "reviewed": True,
            "times_served": {"$lt": MAX_TIMES_SERVED},
            "difficulty": {
                "$gte": target_difficulty - DIFFICULTY_TOLERANCE,
                "$lte": target_difficulty + DIFFICULTY_TOLERANCE,
            },
            "_id": {"$nin": [ObjectId(x) for x in seen_ids]},
        },
        sort=[("times_served", 1)], 
    )

    if candidate is not None:
        await exercises_collection.update_one(
            {"_id": candidate["_id"]},
            {"$inc": {"times_served": 1}},
        )
        return Exercise.model_validate(candidate)

    new_exercise = await generate_fn(concept_id, target_difficulty)
    new_exercise.times_served = 1
    result = await exercises_collection.insert_one(
        new_exercise.model_dump(by_alias=True, exclude={"id"})
    )
    new_exercise.id = str(result.inserted_id)
    return new_exercise


async def register_attempt_result(exercise_id: str, correct: bool) -> None:
    """Actualiza el historial agregado del ejercicio tras cada intento (para recalibrar difficulty a futuro)."""
    field = "times_correct" if correct else "times_incorrect"
    await exercises_collection.update_one(
        {"_id": ObjectId(exercise_id)},
        {"$inc": {field: 1}},
    )
