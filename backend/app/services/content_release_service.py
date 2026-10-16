from __future__ import annotations

from datetime import datetime
from typing import Any

from bson import ObjectId

from app.models import utc_now_naive

from app.database import (
    content_catalog_collection,
    content_chunks_collection,
    content_releases_collection,
    exercises_collection,
    generated_lessons_collection,
)

CATALOG_ID = "published"


async def _published_sources(document: dict[str, Any]) -> list[dict[str, Any]]:
    source_ids = document.get("source_chunk_ids", [])
    if not source_ids:
        return []
    chunk_ids = [
        ObjectId(source_id) if isinstance(source_id, str) and ObjectId.is_valid(source_id) else source_id
        for source_id in source_ids
    ]

    chunks = await content_chunks_collection.find(
        {"_id": {"$in": chunk_ids}},
        {"title": 1, "page": 1},
    ).to_list()
    seen: set[tuple[str, str]] = set()
    sources = []
    for chunk in chunks:
        key = (str(chunk.get("title", "")), str(chunk.get("page", "")))
        if key in seen:
            continue
        seen.add(key)
        sources.append({"title": chunk.get("title"), "page": chunk.get("page")})
    return sources


def merge_published_topics(
    current: list[dict[str, str]], release_topics: list[str], release_id: str
) -> list[dict[str, str]]:
    replacements = set(release_topics)
    merged = [item for item in current if item.get("topic") not in replacements]
    merged.extend({"topic": topic, "release_id": release_id} for topic in release_topics)
    return sorted(merged, key=lambda item: item["topic"])


def release_validation_errors(
    topic: str,
    lesson: dict[str, Any] | None,
    questions: list[dict[str, Any]],
    minimum_questions: int,
    manual_review_required: bool,
) -> list[str]:
    errors = []
    if not lesson or lesson.get("status") not in {"ready", "published"} or lesson.get("verified") is not True:
        errors.append(f"{topic}: falta una lección standard verificada")
    eligible = [
        question for question in questions
        if question.get("status") in {"ready", "published"} and question.get("verified") is True
    ]
    if manual_review_required:
        eligible = [question for question in eligible if question.get("review_status") == "approved"]
    if len(eligible) < minimum_questions:
        errors.append(f"{topic}: pool publicable insuficiente ({len(eligible)}/{minimum_questions})")
    return errors


async def get_published_release_id(topic: str) -> str | None:
    catalog = await content_catalog_collection.find_one({"_id": CATALOG_ID})
    if not catalog:
        return None
    return next(
        (item["release_id"] for item in catalog.get("topics", []) if item.get("topic") == topic),
        None,
    )


async def get_published_lesson(
    topic: str,
    variant: str = "standard",
    release_id: str | None = None,
) -> dict[str, Any] | None:
    release_id = release_id or await get_published_release_id(topic)
    if not release_id:
        return None
    lesson = await generated_lessons_collection.find_one({
        "topic": topic,
        "language": "es",
        "release_id": release_id,
        "variant": variant,
        "status": "published",
        "verified": True,
    })
    if lesson:
        lesson["sources"] = await _published_sources(lesson)
    return lesson


async def validate_release(release_id: str, minimum_questions: int) -> list[str]:
    release = await content_releases_collection.find_one({"release_id": release_id})
    if not release:
        raise ValueError(f"No existe el release {release_id}")
    if release.get("status") not in {"building", "validating", "ready"}:
        raise ValueError(f"No se puede validar un release en estado {release.get('status')}")
    await content_releases_collection.update_one(
        {"release_id": release_id},
        {"$set": {"status": "validating", "validation_started_at": utc_now_naive()}},
    )

    topics = release.get("topics", [])
    if not topics:
        errors = ["El release no contiene temas procesados"]
    elif "C1.1" in topics and not release.get("metadata", {}).get("pilot_review_completed"):
        errors = ["Completa verify-existing y la revisión manual del piloto antes de validar"]
    else:
        default_manual_topics = ["C1.1"] if "C1.1" in topics else []
        manual_topics = set(release.get("metadata", {}).get("manual_review_topics", default_manual_topics))
        errors = []
        if not manual_topics.issubset(set(topics)):
            errors.append(f"Los temas de revisión manual no están todos en el release: {sorted(manual_topics - set(topics))}")
        for topic in topics:
            lesson = await generated_lessons_collection.find_one({
                "topic": topic,
                "language": "es",
                "release_id": release_id,
                "variant": "standard",
            })
            questions = await exercises_collection.find({
                "topic": topic,
                "language": "es",
                "release_id": release_id,
            }).to_list()
            errors.extend(release_validation_errors(
                topic, lesson, questions, minimum_questions, topic in manual_topics,
            ))

    update: dict[str, Any] = {
        "validation_errors": errors,
        "validated_at": utc_now_naive(),
    }
    update["status"] = "ready" if not errors else "validating"
    await content_releases_collection.update_one({"release_id": release_id}, {"$set": update})
    return errors


async def publish_release(release_id: str, minimum_questions: int) -> list[str]:
    release = await content_releases_collection.find_one({"release_id": release_id})
    if not release:
        raise ValueError(f"No existe el release {release_id}")
    if release.get("status") != "ready":
        raise ValueError("Solo se pueden publicar releases en estado ready")

    errors = await validate_release(release_id, minimum_questions)
    if errors:
        return errors

    topics = release.get("topics", [])
    current = await content_catalog_collection.find_one({"_id": CATALOG_ID})
    current_topics = current.get("topics", []) if current else []
    merged_topics = merge_published_topics(current_topics, topics, release_id)

    async with await content_releases_collection.database.client.start_session() as session:
        async with session.start_transaction():
            for topic in topics:
                await generated_lessons_collection.update_many({
                    "topic": topic, "language": "es", "release_id": release_id,
                    "status": "ready", "verified": True,
                }, {"$set": {"status": "published", "updated_at": utc_now_naive()}}, session=session)
                await exercises_collection.update_many({
                    "topic": topic, "language": "es", "release_id": release_id,
                    "status": "ready", "verified": True,
                    **({"review_status": "approved"} if topic in set(release.get("metadata", {}).get("manual_review_topics", ["C1.1"])) else {}),
                }, {"$set": {"status": "published"}}, session=session)
            await content_releases_collection.update_one({"release_id": release_id}, {"$set": {
                "status": "published",
                "published_at": utc_now_naive(),
            }}, session=session)
            await content_catalog_collection.update_one(
                {"_id": CATALOG_ID},
                {"$set": {"topics": merged_topics, "updated_at": utc_now_naive()}},
                upsert=True,
                session=session,
            )

    old_release_ids = {item.get("release_id") for item in current_topics} - {release_id}
    for old_release_id in old_release_ids:
        still_active = any(item.get("release_id") == old_release_id for item in merged_topics)
        if not still_active:
            await content_releases_collection.update_one(
                {"release_id": old_release_id, "status": "published"},
                {"$set": {"status": "superseded"}},
            )
    return []
