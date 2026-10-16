from datetime import datetime
from typing import Any

from bson import ObjectId

from app.database import sessions_collection


MAX_RECENT_QUIZZES = 10


async def get_recent_quiz_activity(student_id: str) -> list[dict[str, Any]]:
    if not ObjectId.is_valid(student_id):
        raise ValueError("student_id no es válido")

    cursor = (
        sessions_collection.find(
            {
                "student_id": ObjectId(student_id),
                "quiz_status": "completed",
            },
            {
                "_id": 0,
                "quiz_topic": 1,
                "completed_at": 1,
                "score": 1,
                "answers.is_correct": 1,
            },
        )
        .sort("completed_at", -1)
        .limit(MAX_RECENT_QUIZZES)
    )

    sessions = await cursor.to_list(length=MAX_RECENT_QUIZZES)
    activity = []

    for session in sessions:
        answers = session.get("answers", [])
        if not isinstance(answers, list):
            answers = []

        completed_at = session.get("completed_at")
        activity.append({
            "topic": session.get("quiz_topic"),
            "completed_at": (
                completed_at.isoformat()
                if isinstance(completed_at, datetime)
                else None
            ),
            "score": session.get("score"),
            "correct_answers": sum(
                answer.get("is_correct") is True
                for answer in answers
                if isinstance(answer, dict)
            ),
            "incorrect_answers": sum(
                answer.get("is_correct") is False
                for answer in answers
                if isinstance(answer, dict)
            ),
        })

    return activity