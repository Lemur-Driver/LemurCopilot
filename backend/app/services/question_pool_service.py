import asyncio
import hashlib
import re
from datetime import datetime
from collections.abc import Iterable
from difflib import SequenceMatcher
from typing import Any

from bson import ObjectId

from app.database import exercises_collection, sessions_collection

POOL_THRESHOLD = 0.8
QUIZ_SIZE = 3
SIMILARITY_THRESHOLD = 0.88
_topic_locks: dict[str, asyncio.Lock] = {}


def normalize_question(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def question_fingerprint(topic: str, question: str, options: Iterable[str]) -> str:
    normalized = "|".join(
        [topic, normalize_question(question), *(normalize_question(option) for option in options)]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


async def _answered_ids(student_id: str, topic: str) -> set[str]:
    cursor = sessions_collection.find(
        {
            "student_id": ObjectId(student_id),
            "$or": [{"quiz_topic": topic}, {"answers": {"$elemMatch": {"topic": topic}}}],
        },
        {"answers.exercise_id": 1, "exercises_attempted.exercise_id": 1},
    )
    answered: set[str] = set()
    async for session in cursor:
        for answer in session.get("answers", []):
            if answer.get("exercise_id"):
                answered.add(str(answer["exercise_id"]))
        for attempt in session.get("exercises_attempted", []):
            if attempt.get("exercise_id"):
                answered.add(str(attempt["exercise_id"]))
    return answered


async def _known_ids(student_id: str, topic: str) -> set[str]:
    cursor = sessions_collection.find(
        {
            "student_id": ObjectId(student_id),
            "quiz_topic": topic,
            "answers": {"$elemMatch": {"exercise_id": {"$exists": True}, "is_correct": True}},
        },
        {"answers": 1},
    )
    known: set[str] = set()
    async for session in cursor:
        for answer in session.get("answers", []):
            if answer.get("exercise_id") and answer.get("is_correct"):
                known.add(str(answer["exercise_id"]))
    return known


async def _pool_documents(topic: str) -> list[dict[str, Any]]:
    return await exercises_collection.find({"topic": topic, "language": "es"}).to_list()


async def _is_duplicate(topic: str, question: str, options: list[str], existing: list[dict[str, Any]]) -> bool:
    fingerprint = question_fingerprint(topic, question, options)
    normalized = normalize_question(question)
    for item in existing:
        if item.get("fingerprint") == fingerprint:
            return True
        other = normalize_question(item.get("question", ""))
        if other and SequenceMatcher(None, normalized, other).ratio() >= SIMILARITY_THRESHOLD:
            return True
    return False


async def _publish_questions(topic: str, questions: list[dict[str, Any]], chunks: list[dict[str, Any]]) -> int:
    existing = await _pool_documents(topic)
    published = 0
    source_ids = [str(chunk["_id"]) for chunk in chunks if chunk.get("_id")]

    for question in questions:
        text = question.get("question", "")
        options = question.get("options", [])
        correct_index = question.get("correctAnswer")
        if (
            not isinstance(text, str)
            or not text.strip()
            or not isinstance(options, list)
            or len(options) != 4
            or not isinstance(correct_index, int)
            or not 0 <= correct_index < len(options)
            or await _is_duplicate(topic, text, options, existing)
        ):
            continue

        document = {
            "topic": topic,
            "language": "es",
            "type": "multiple_choice",
            "question": text.strip(),
            "options": options,
            "correct_index": correct_index,
            "correct_answer": options[correct_index],
            "explanation": question.get("explanation"),
            "difficulty": 0.5,
            "generated_by": "llm",
            "source_chunk_ids": source_ids,
            "fingerprint": question_fingerprint(topic, text, options),
            "reviewed": True,
        }
        result = await exercises_collection.update_one(
            {"fingerprint": document["fingerprint"]},
            {"$setOnInsert": document},
            upsert=True,
        )
        if result.upserted_id:
            document["_id"] = result.upserted_id
            existing.append(document)
            published += 1
    return published


async def _generate_batch(
    topic: str,
    lesson: dict[str, Any],
    chunks: list[dict[str, Any]],
    config: dict[str, Any],
    student_profile: dict[str, Any] | None,
) -> int:
    from app.services.quiz_service import generate_quiz

    generated = await generate_quiz(
        topic=topic,
        lesson=lesson,
        chunks=chunks,
        config=config,
        student_profile=student_profile,
    )
    return await _publish_questions(topic, generated["questions"], chunks)


async def ensure_pool(
    student_id: str,
    topic: str,
    lesson: dict[str, Any],
    chunks: list[dict[str, Any]],
    config: dict[str, Any],
    student_profile: dict[str, Any] | None,
) -> None:
    lock = _topic_locks.setdefault(topic, asyncio.Lock())
    async with lock:
        pool = await _pool_documents(topic)
        known = await _known_ids(student_id, topic)
        known_count = len({str(item["_id"]) for item in pool} & known)
        coverage = known_count / len(pool) if pool else 0.0
        answered = await _answered_ids(student_id, topic)
        unseen_count = sum(1 for item in pool if str(item["_id"]) not in answered)

        if not pool or len(pool) < QUIZ_SIZE or coverage >= POOL_THRESHOLD or unseen_count < QUIZ_SIZE:
            await _generate_batch(topic, lesson, chunks, config, student_profile)


async def select_quiz(student_id: str, topic: str) -> dict[str, Any]:
    pool = await _pool_documents(topic)
    answered = await _answered_ids(student_id, topic)
    candidates = [item for item in pool if str(item["_id"]) not in answered]

    if len(candidates) < QUIZ_SIZE:
        candidates.extend(item for item in pool if item not in candidates)

    candidates.sort(key=lambda item: (item.get("times_served", 0), item.get("difficulty", 0.5)))
    selected = candidates[:QUIZ_SIZE]
    if len(selected) < QUIZ_SIZE:
        raise ValueError("No hay suficientes preguntas disponibles para este tema")

    for item in selected:
        await exercises_collection.update_one(
            {"_id": item["_id"]},
            {"$inc": {"times_served": 1}},
        )

    assignment = await sessions_collection.insert_one({
        "student_id": ObjectId(student_id),
        "started_at": datetime.utcnow(),
        "quiz_topic": topic,
        "quiz_exercise_ids": [item["_id"] for item in selected],
        "quiz_status": "assigned",
        "answers": [],
    })

    return {
        "sessionId": str(assignment.inserted_id),
        "questions": [
            {
                "exerciseId": str(item["_id"]),
                "question": item["question"],
                "options": item["options"],
            }
            for item in selected
        ]
    }