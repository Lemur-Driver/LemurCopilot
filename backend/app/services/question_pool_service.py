import asyncio
import hashlib
import re
from datetime import datetime, timezone
from collections.abc import Iterable
from difflib import SequenceMatcher
from typing import Any

from bson import ObjectId

from app.database import exercises_collection, sessions_collection

POOL_THRESHOLD = 0.8
QUIZ_SIZE = 3
MAX_GENERATION_BATCHES = 3
SIMILARITY_THRESHOLD = 0.88
_topic_locks: dict[str, asyncio.Lock] = {}


def normalize_question(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def question_fingerprint(
    topic: str,
    question: str,
    options: Iterable[str],
    correct_index: int | None = None,
    release_id: str | None = None,
) -> str:
    normalized = "|".join(
        [topic, normalize_question(question), *(normalize_question(option) for option in options)]
    )
    if correct_index is not None:
        normalized = f"{normalized}|answer:{correct_index}"
    if release_id is not None:
        normalized = f"{normalized}|release:{release_id}"
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


async def _pool_documents(
    topic: str,
    release_id: str | None = None,
) -> list[dict[str, Any]]:

    query: dict[str, Any] = {
        "topic": topic,
        "language": "es",
    }

    if release_id is not None:
        # Worker construyendo una release.
        query["release_id"] = release_id
        query["status"] = {
            "$in": ["ready", "published"]
        }

    else:
        # Runtime: solamente contenido publicado.
        from app.services.content_release_service import (
            get_published_release_id,
        )

        published_release_id = (
            await get_published_release_id(topic)
        )

        if not published_release_id:
            return []

        query["release_id"] = published_release_id
        query["status"] = "published"

    return await exercises_collection.find(query).to_list()


def _stored_question_consistent(item: dict[str, Any]) -> bool:
    options = item.get("options", [])
    correct_index = item.get("correct_index")
    return (
        isinstance(options, list)
        and len(options) == 4
        and all(isinstance(option, str) and option.strip() for option in options)
        and len({option.strip().casefold() for option in options if isinstance(option, str)}) == 4
        and isinstance(item.get("question"), str)
        and bool(item["question"].strip())
        and isinstance(correct_index, int)
        and not isinstance(correct_index, bool)
        and 0 <= correct_index < len(options)
        and item.get("correct_answer") == options[correct_index]
        and isinstance(item.get("explanation"), str)
        and bool(item["explanation"].strip())
        and (
            item.get("status") in (None, "pending", "generated", "verifying", "ready", "published")
            and item.get("verified") in (None, True)
        )
    )


async def _is_duplicate(
    topic: str,
    question: str,
    options: list[str],
    existing: list[dict[str, Any]],
    correct_index: int,
    release_id: str | None = None,
) -> bool:

    fingerprint = question_fingerprint(
        topic,
        question,
        options,
        correct_index,
        release_id,
    )

    normalized = normalize_question(question)

    for item in existing:
        if item.get("fingerprint") == fingerprint:
            return True

        other = normalize_question(
            item.get("question", "")
        )

        if (
            other
            and SequenceMatcher(
                None,
                normalized,
                other,
            ).ratio() >= SIMILARITY_THRESHOLD
        ):
            return True

    return False


async def _publish_questions(
    topic: str,
    questions: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    *,
    release_id: str | None = None,
    content_version: str | None = None,
    prompt_version: str | None = None,
    verification_version: str | int = 2,
) -> int:
    existing = [
        item for item in await _pool_documents(topic, release_id)
        if item.get("verified") is True
    ]
    published = 0
    chunks_by_ref = {
        (str(chunk.get("page")), str(chunk.get("chunk_index"))): chunk
        for chunk in chunks
    }

    for question in questions:
        text = question.get("question", "")
        options = question.get("options", [])
        correct_index = question.get("correctAnswer")
        metadata_valid = (
            release_id is None
            or (
                isinstance(question.get("concept_tags"), list)
                and bool(question["concept_tags"])
                and all(isinstance(tag, str) and tag.strip() for tag in question["concept_tags"])
                and isinstance(question.get("misconception_tags"), list)
                and all(isinstance(tag, str) and tag.strip() for tag in question["misconception_tags"])
                and isinstance(question.get("difficulty"), (int, float))
                and not isinstance(question.get("difficulty"), bool)
                and 0 <= question["difficulty"] <= 1
                and question.get("cognitive_skill") in {"recall", "comprehension", "application", "analysis"}
            )
        )
        if (
            not metadata_valid
            or not isinstance(text, str)
            or not text.strip()
            or not isinstance(options, list)
            or len(options) != 4
            or any(not isinstance(option, str) or not option.strip() for option in options)
            or len({option.strip().casefold() for option in options if isinstance(option, str)}) != 4
            or not isinstance(correct_index, int)
            or isinstance(correct_index, bool)
            or not 0 <= correct_index < len(options)
            or options[correct_index].strip().casefold() != str(question.get("correctAnswerText", "")).strip().casefold()
            or not question.get("verified")
            or await _is_duplicate(topic, text, options, existing, correct_index, release_id)
        ):
            continue

        evidence_refs = question.get("evidence_refs", [])
        referenced_chunks = []
        valid_evidence = bool(evidence_refs)
        for ref in evidence_refs:
            if not isinstance(ref, dict):
                valid_evidence = False
                break
            key = (str(ref.get("page")), str(ref.get("chunk_index")))
            source_chunk = chunks_by_ref.get(key)
            if (
                source_chunk is None
                or not isinstance(ref.get("quote"), str)
                or " ".join(ref["quote"].casefold().split()) not in " ".join(source_chunk.get("text", "").casefold().split())
            ):
                valid_evidence = False
                break
            referenced_chunks.append(source_chunk)
        if not valid_evidence:
            continue

        document = {
            "topic": topic,
            "language": "es",
            "type": "multiple_choice",
            "question": text.strip(),
            "options": options,
            "correct_index": correct_index,
            "correct_answer": options[correct_index],
            "correct_answer_text": question.get("correctAnswerText"),
            "explanation": question.get("explanation"),
            "difficulty": question.get("difficulty", 0.5),
            "concept_tags": question.get("concept_tags", []),
            "misconception_tags": question.get("misconception_tags", []),
            "cognitive_skill": question.get("cognitive_skill", "recall"),
            "generated_by": "llm",
            "source_chunk_ids": [chunk["_id"] for chunk in referenced_chunks if chunk.get("_id")],
            "evidence_refs": evidence_refs,
            "fingerprint": question_fingerprint(topic, text, options, correct_index, release_id),
            "content_version": content_version,
            "prompt_version": prompt_version,
            "verification_version": verification_version,
            "release_id": release_id,
            "status": "ready" if release_id else "published",
            "review_status": None,
            "reviewed": False,
            "verified": True,
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
    question_count: int = QUIZ_SIZE,
    *,
    release_id: str | None = None,
    content_version: str | None = None,
    prompt_version: str | None = None,
    verification_version: str | int = 2,
) -> int:
    from app.services.quiz_service import generate_quiz

    generated = await generate_quiz(
        topic=topic,
        lesson=lesson,
        chunks=chunks,
        config=config,
        student_profile=student_profile,
        question_count=question_count,
    )
    return await _publish_questions(
        topic,
        generated["questions"],
        chunks,
        release_id=release_id,
        content_version=content_version,
        prompt_version=prompt_version,
        verification_version=verification_version,
    )


async def _verify_pending_questions(topic: str, chunks: list[dict[str, Any]]) -> None:
    from app.services.quiz_service import verify_stored_question

    pending = await exercises_collection.find(
        {
            "topic": topic,
            "language": "es",
            "verified": {"$ne": True},
            "verification_version": {"$ne": 2},
            "$or": [
                {"status": {"$exists": False}},
                {"status": None},
                {"status": "published"},
            ],
        }
    ).limit(QUIZ_SIZE).to_list()
    for item in pending:
        if not _stored_question_consistent(item):
            await exercises_collection.update_one(
                {"_id": item["_id"]},
                {"$set": {"verified": False, "reviewed": False, "verification_version": 2}},
            )
            continue
        source_ids = {str(source_id) for source_id in item.get("source_chunk_ids", [])}
        evidence_chunks = [chunk for chunk in chunks if str(chunk.get("_id")) in source_ids]
        if not evidence_chunks:
            await exercises_collection.update_one(
                {"_id": item["_id"]},
                {"$set": {"verified": False, "reviewed": False, "verification_version": 2}},
            )
            continue
        is_valid = await verify_stored_question(item, evidence_chunks)
        update = {"verified": is_valid, "verification_version": 2}
        if not is_valid:
            update["reviewed"] = False
        await exercises_collection.update_one(
            {"_id": item["_id"]},
            {"$set": update},
        )


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
        await _verify_pending_questions(topic, chunks)
        pool = [
            item for item in await _pool_documents(topic)
            if item.get("verified") is True and _stored_question_consistent(item)
        ]
        known = await _known_ids(student_id, topic)
        known_count = len({str(item["_id"]) for item in pool} & known)
        coverage = known_count / len(pool) if pool else 0.0
        answered = await _answered_ids(student_id, topic)
        unseen_count = sum(1 for item in pool if str(item["_id"]) not in answered)

        if not pool or len(pool) < QUIZ_SIZE or coverage >= POOL_THRESHOLD or unseen_count < QUIZ_SIZE:
            await _generate_batch(topic, lesson, chunks, config, student_profile)


async def select_quiz(
    student_id: str,
    topic: str,
    lesson: dict[str, Any] | None = None,
    chunks: list[dict[str, Any]] | None = None,
    config: dict[str, Any] | None = None,
    student_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from app.services.content_service import get_topic_chunks
    from app.prompts.lesson_prompts import LESSON_CONFIGS

    chunks = chunks if chunks is not None else await get_topic_chunks(topic)
    config = config if config is not None else LESSON_CONFIGS.get(topic)
    if not chunks or config is None:
        raise ValueError("No se pudo obtener el manual para verificar las preguntas de este tema")

    lock = _topic_locks.setdefault(topic, asyncio.Lock())
    async with lock:
        await _verify_pending_questions(topic, chunks)

        for _ in range(MAX_GENERATION_BATCHES):
            pool = [
                item for item in await _pool_documents(topic)
                if item.get("verified") is True and _stored_question_consistent(item)
            ]
            answered = await _answered_ids(student_id, topic)
            unseen_count = sum(1 for item in pool if str(item["_id"]) not in answered)
            if unseen_count >= QUIZ_SIZE:
                break
            await _generate_batch(
                topic,
                lesson or {"title": topic, "introduction": "", "sections": []},
                chunks,
                config,
                student_profile,
                question_count=max(QUIZ_SIZE - unseen_count, 1),
            )
        pool = [
            item for item in await _pool_documents(topic)
            if item.get("verified") is True and _stored_question_consistent(item)
        ]

        answered = await _answered_ids(student_id, topic)
        candidates = [item for item in pool if str(item["_id"]) not in answered]
        if len(candidates) < QUIZ_SIZE:
            candidates.extend(item for item in pool if item not in candidates)

        candidates = [item for item in candidates if item.get("verified") is True and _stored_question_consistent(item)]
        candidates.sort(key=lambda item: (item.get("times_served", 0), item.get("difficulty", 0.5)))
        selected = candidates[:QUIZ_SIZE]
        if len(selected) < QUIZ_SIZE:
            raise ValueError("No se pudieron preparar tres preguntas verificadas para este tema. Inténtalo nuevamente más tarde.")

    for item in selected:
        await exercises_collection.update_one(
            {"_id": item["_id"]},
            {"$inc": {"times_served": 1}},
        )

    assignment = await sessions_collection.insert_one({
        "student_id": ObjectId(student_id),
        "started_at": datetime.now(timezone.utc),
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