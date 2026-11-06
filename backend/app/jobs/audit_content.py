from __future__ import annotations

import argparse
import asyncio
import json
from datetime import date, datetime, timezone
from typing import Any

from app.database import (
    content_catalog_collection,
    content_jobs_collection,
    content_releases_collection,
    exercises_collection,
    generated_lessons_collection,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exporta un inventario de contenido MongoDB sin datos de estudiantes."
    )
    parser.add_argument(
        "--samples-per-topic",
        type=int,
        default=2,
        help="Máximo de preguntas de muestra por tema (0 desactiva las muestras).",
    )
    parser.add_argument(
        "--text-limit",
        type=int,
        default=500,
        help="Máximo de caracteres por fragmento de texto de muestra.",
    )
    parser.add_argument(
        "--topic",
        action="append",
        dest="topics",
        help="Limita las muestras a este tema; puede repetirse. El inventario sigue siendo global.",
    )
    return parser


def _short_text(value: Any, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    return text if len(text) <= limit else text[:limit].rstrip() + "…"


def _json_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


async def _group_counts(collection: Any, fields: list[str]) -> list[dict[str, Any]]:
    group_id = {field: f"${field}" for field in fields}
    cursor = await collection.aggregate([
        {"$group": {"_id": group_id, "count": {"$sum": 1}}},
        {"$sort": {"_id.topic": 1, "_id.release_id": 1, "_id.variant": 1, "_id.status": 1}},
    ])
    return [
        {**(item.get("_id") or {}), "count": item["count"]}
        async for item in cursor
    ]


async def _sample_lesson(topic: str, release_id: str, variant: str, text_limit: int) -> dict[str, Any] | None:
    item = await generated_lessons_collection.find_one(
        {"topic": topic, "release_id": release_id, "variant": variant, "language": "es"},
        {"_id": 0, "status": 1, "verified": 1, "prompt_version": 1,
         "verification_version": 1, "concept_tags": 1, "lesson": 1},
    )
    if not item:
        return None

    lesson = item.get("lesson") if isinstance(item.get("lesson"), dict) else {}
    sections = lesson.get("sections", [])
    return {
        "variant": variant,
        "status": item.get("status"),
        "verified": item.get("verified"),
        "prompt_version": item.get("prompt_version"),
        "verification_version": item.get("verification_version"),
        "concept_tags": item.get("concept_tags", []),
        "title": _short_text(lesson.get("title"), text_limit),
        "introduction": _short_text(lesson.get("introduction"), text_limit),
        "sections": [
            {
                "title": _short_text(section.get("title"), text_limit),
                "content": _short_text(section.get("content"), text_limit),
            }
            for section in sections[:2]
            if isinstance(section, dict)
        ] if isinstance(sections, list) else [],
        "key_points": [
            _short_text(point, text_limit)
            for point in lesson.get("key_points", [])[:4]
            if isinstance(point, str)
        ] if isinstance(lesson.get("key_points"), list) else [],
    }


async def _sample_questions(
    topic: str, release_id: str, limit: int, text_limit: int
) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    cursor = exercises_collection.find(
        {
            "topic": topic,
            "release_id": release_id,
            "language": "es",
            "status": {"$in": ["ready", "published"]},
            "verified": True,
            "$or": [{"review_status": None}, {"review_status": "approved"}],
        },
        {
            "_id": 0, "question": 1, "options": 1, "correct_index": 1,
            "correct_answer": 1, "explanation": 1, "concept_tags": 1,
            "misconception_tags": 1, "cognitive_skill": 1, "difficulty": 1,
            "status": 1, "review_status": 1,
        },
    ).sort("_id", 1).limit(limit)
    samples = []
    async for item in cursor:
        samples.append({
            **{key: item.get(key) for key in (
                "concept_tags", "misconception_tags", "cognitive_skill", "difficulty",
                "status", "review_status", "correct_index",
            )},
            "question": _short_text(item.get("question"), text_limit),
            "options": [
                _short_text(option, text_limit) for option in item.get("options", [])
                if isinstance(option, str)
            ],
            "correct_answer": _short_text(item.get("correct_answer"), text_limit),
            "explanation": _short_text(item.get("explanation"), text_limit),
        })
    return samples


async def build_report(args: argparse.Namespace) -> dict[str, Any]:
    catalog = await content_catalog_collection.find_one({"_id": "published"}, {"_id": 0}) or {}
    catalog_topics = catalog.get("topics", [])
    releases = await content_releases_collection.find(
        {},
        {"_id": 0, "release_id": 1, "content_version": 1, "status": 1,
         "created_at": 1, "published_at": 1, "topics": 1, "metadata.manual_review_topics": 1},
    ).sort("created_at", -1).to_list()
    release_by_id = {item.get("release_id"): item for item in releases}

    exercise_counts = await _group_counts(
        exercises_collection, ["topic", "release_id", "status", "verified", "review_status"]
    )
    lesson_counts = await _group_counts(
        generated_lessons_collection, ["topic", "release_id", "variant", "status", "verified"]
    )
    job_counts = await _group_counts(content_jobs_collection, ["topic", "release_id", "status"])

    requested_topics = set(args.topics or [])
    active_topics = [item for item in catalog_topics if isinstance(item, dict) and item.get("topic")]
    sample_topics = [item for item in active_topics if not requested_topics or item["topic"] in requested_topics]
    topic_reports = []
    for active in sample_topics:
        topic = active["topic"]
        release_id = active.get("release_id")
        chosen_release = release_by_id.get(release_id, {})
        lesson_samples = []
        for variant in ("standard", "reinforcement", "challenge"):
            lesson = await _sample_lesson(topic, release_id, variant, args.text_limit)
            if lesson is not None:
                lesson_samples.append(lesson)

        eligible_count = await exercises_collection.count_documents({
            "topic": topic,
            "release_id": release_id,
            "language": "es",
            "status": "published",
            "verified": True,
            "$or": [{"review_status": None}, {"review_status": "approved"}],
        })
        manual_review_topics = chosen_release.get("metadata", {}).get("manual_review_topics")
        if manual_review_topics is None:
            manual_review_topics = ["C1.1"] if "C1.1" in chosen_release.get("topics", []) else []
        topic_reports.append({
            "topic": topic,
            "active_release_id": release_id,
            "release_status": chosen_release.get("status"),
            "content_version": chosen_release.get("content_version"),
            "manual_review_required": topic in manual_review_topics,
            "published_eligible_question_count": eligible_count,
            "lessons": lesson_samples,
            "question_samples": await _sample_questions(
                topic, release_id, args.samples_per_topic, args.text_limit
            ),
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "privacy_note": "Solo inventario y muestras de contenido; no se consultan estudiantes, sesiones ni credenciales.",
        "published_catalog": active_topics,
        "releases": releases,
        "counts": {
            "exercises_by_topic_release_status_verification_review": exercise_counts,
            "lessons_by_topic_release_variant_status_verification": lesson_counts,
            "jobs_by_topic_release_status": job_counts,
        },
        "active_topic_samples": topic_reports,
        "sample_configuration": {
            "questions_per_topic": args.samples_per_topic,
            "text_limit_characters": args.text_limit,
            "topic_filter": sorted(requested_topics) if requested_topics else None,
        },
    }


async def main() -> None:
    args = _parser().parse_args()
    if args.samples_per_topic < 0:
        raise SystemExit("--samples-per-topic debe ser 0 o mayor")
    if args.text_limit < 100:
        raise SystemExit("--text-limit debe ser al menos 100")
    report = await build_report(args)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=_json_default))


if __name__ == "__main__":
    asyncio.run(main())
