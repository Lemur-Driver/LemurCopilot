from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import os
from typing import Any

from bson import ObjectId

from app.database import client, content_releases_collection, exercises_collection
from app.prompts.lesson_prompts import LESSON_SEQUENCE
from app.services.content_release_service import (
    publish_release,
    validate_release,
)
from app.services.content_service import get_topic_chunks
from app.services.quiz_service import verify_stored_question

MINIMUM_QUESTIONS = int(os.getenv("CONTENT_WORKER_MINIMUM_QUESTIONS", "15"))
PILOT_TOPIC = "C1.1"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Administra y revisa releases de contenido.")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list-releases", help="Muestra los releases y sus estados.")
    for name in ("validate", "publish"):
        command = commands.add_parser(name)
        command.add_argument("release_id")
        command.add_argument("--minimum-questions", type=int, default=MINIMUM_QUESTIONS)

    review = commands.add_parser("review-queue", help="Lista preguntas del piloto que requieren revisión manual.")
    review.add_argument("--release-id")
    review.add_argument("--legacy", action="store_true", help="Revisar preguntas migradas que aún no se copiaron a un release.")
    review.add_argument("--topic", default=PILOT_TOPIC)
    review.add_argument("--limit", type=int, default=100)

    decision = commands.add_parser("review")
    decision.add_argument("exercise_id")
    decision.add_argument("--decision", required=True, choices=("approve", "reject"))
    decision.add_argument("--reviewer", required=True)
    decision.add_argument("--notes", default="")
    decision.add_argument("--release-id", help="Release piloto para copiar una pregunta legacy tras aprobarla.")

    migrate = commands.add_parser("verify-existing", help="Clasifica preguntas previas sin publicarlas.")
    migrate.add_argument("--topic", default=PILOT_TOPIC)
    migrate.add_argument("--release-id")
    migrate.add_argument("--limit", type=int, default=500)

    return parser


def _format_question(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "exercise_id": str(item.get("_id")),
        "topic": item.get("topic"),
        "status": item.get("status"),
        "verified": item.get("verified"),
        "review_status": item.get("review_status", "pending"),
        "question": item.get("question"),
        "options": item.get("options"),
        "correct_index": item.get("correct_index"),
        "correct_answer": item.get("correct_answer"),
        "explanation": item.get("explanation"),
    }


async def list_releases() -> None:
    releases = await content_releases_collection.find({}).sort("created_at", -1).to_list()
    for item in releases:
        print(f"{item.get('release_id')}\t{item.get('status')}\t{','.join(item.get('topics', []))}")


async def review_queue(topic: str, release_id: str | None, limit: int, legacy: bool = False) -> None:
    query: dict[str, Any] = {"topic": topic, "review_status": {"$in": [None, "pending"]}}
    if release_id:
        query["release_id"] = release_id
    elif legacy:
        query["release_id"] = {"$exists": False}
    items = await exercises_collection.find(query).sort("created_at", 1).limit(limit).to_list()
    for item in items:
        print(_format_question(item))
    print(f"Pendientes: {len(items)}")


async def review_question(exercise_id: str, decision: str, reviewer: str, notes: str, release_id: str | None) -> None:
    if not ObjectId.is_valid(exercise_id):
        raise ValueError("exercise_id debe ser un ObjectId v?lido")
    question = await exercises_collection.find_one({"_id": ObjectId(exercise_id)})
    if not question:
        raise ValueError("No existe la pregunta")
    if question.get("verified") is not True or question.get("status") not in {"ready", "published"}:
        raise ValueError("Solo se pueden revisar preguntas verificadas estructural y sem?nticamente")
    if question.get("topic") != PILOT_TOPIC:
        raise ValueError(f"La revisi?n manual est? limitada al piloto {PILOT_TOPIC}")
    if question.get("release_id") and release_id and question.get("release_id") != release_id:
        raise ValueError("La pregunta pertenece a otro release")
    release = None
    if release_id:
        release = await content_releases_collection.find_one({"release_id": release_id})
        if not release:
            raise ValueError(f"No existe el release {release_id}")

    update = {
        "review_status": "approved" if decision == "approve" else "rejected",
        "reviewed_by": reviewer,
        "reviewed_at": datetime.now(timezone.utc),
        "review_notes": notes,
        "reviewed": decision == "approve",
    }
    if decision == "approve" and release_id and question.get("release_id") is None:
        update.update({
            "fingerprint": question.get("fingerprint") or f"legacy-{question['_id']}",
            "release_id": release_id,
            "content_version": release.get("content_version"),
            "prompt_version": "legacy-manual-review-v1",
            "verification_version": "legacy-migration-v1",
            "status": "ready",
            "verified": True,
        })
    await exercises_collection.update_one({"_id": question["_id"]}, {"$set": update})
    if decision == "approve" and release_id and question.get("release_id") is None:
        await content_releases_collection.update_one({"release_id": release_id}, {
            "$addToSet": {"topics": PILOT_TOPIC},
            "$set": {"metadata.manual_review_topics": [PILOT_TOPIC]},
        })
    print(f"{exercise_id}: {decision}")


async def verify_existing(topic: str, release_id: str | None, limit: int) -> None:
    chunks = await get_topic_chunks(topic)
    if not chunks:
        raise ValueError(f"No hay chunks oficiales para {topic}")
    query = {
        "topic": topic,
        "release_id": {"$exists": False},
        "status": {"$nin": ["rejected", "superseded"]},
    }
    questions = await exercises_collection.find(query).limit(limit).to_list()
    counts = {"pending_manual_review": 0, "rejected": 0}
    for question in questions:
        evidence_refs = question.get("evidence_refs", [])
        if evidence_refs:
            by_reference = {
                (str(chunk.get("page")), str(chunk.get("chunk_index"))): chunk
                for chunk in chunks
            }
            valid_refs = all(
                isinstance(ref, dict)
                and (str(ref.get("page")), str(ref.get("chunk_index"))) in by_reference
                and isinstance(ref.get("quote"), str)
                and " ".join(ref["quote"].casefold().split())
                in " ".join(by_reference[(str(ref["page"]), str(ref["chunk_index"]))].get("text", "").casefold().split())
                for ref in evidence_refs
            )
            evidence_chunks = [
                by_reference[(str(ref["page"]), str(ref["chunk_index"]))]
                for ref in evidence_refs if isinstance(ref, dict)
                and (str(ref.get("page")), str(ref.get("chunk_index"))) in by_reference
            ] if valid_refs else []
        else:
            source_ids = {str(value) for value in question.get("source_chunk_ids", [])}
            evidence_chunks = [chunk for chunk in chunks if str(chunk.get("_id")) in source_ids]
            valid_refs = bool(evidence_chunks)

        is_valid = valid_refs and bool(evidence_chunks) and await verify_stored_question(question, evidence_chunks)
        now = datetime.utcnow()
        if not is_valid:
            await exercises_collection.update_one({"_id": question["_id"]}, {"$set": {
                "status": "rejected",
                "verified": False,
                "review_status": "rejected",
                "reviewed": False,
                "verification_version": "legacy-migration-v1",
                "verification_error": "Fallo validación estructural, evidencia o verificación semántica",
                "verified_at": now,
            }})
            counts["rejected"] += 1
            continue

        await exercises_collection.update_one({"_id": question["_id"]}, {"$set": {
            "status": "ready",
            "verified": True,
            "review_status": "pending",
            "reviewed": False,
            "verification_version": "legacy-migration-v1",
            "verified_at": now,
        }})
        counts["pending_manual_review"] += 1
    print({"topic": topic, "processed": len(questions), **counts})
    if release_id:
        release = await content_releases_collection.find_one({"release_id": release_id})
        if not release:
            raise ValueError(f"No existe el release {release_id}")
        if topic not in release.get("topics", []):
            await content_releases_collection.update_one({"release_id": release_id}, {"$addToSet": {"topics": topic}})
        if len(questions) < limit:
            remaining = await exercises_collection.count_documents({
                "topic": topic,
                "release_id": {"$exists": False},
                "status": {"$nin": ["rejected", "superseded"]},
            })
            if remaining == 0:
                await content_releases_collection.update_one({"release_id": release_id}, {"$set": {
                    "metadata.pilot_review_completed": True,
                    "metadata.pilot_review_completed_at": datetime.utcnow(),
                }})


async def run(args: argparse.Namespace) -> int:
    if args.command == "list-releases":
        await list_releases()
    elif args.command == "validate":
        errors = await validate_release(args.release_id, args.minimum_questions)
        print({"release_id": args.release_id, "errors": errors})
        return 1 if errors else 0
    elif args.command == "publish":
        errors = await publish_release(args.release_id, args.minimum_questions)
        print({"release_id": args.release_id, "errors": errors})
        return 1 if errors else 0
    elif args.command == "review-queue":
        await review_queue(args.topic, args.release_id, args.limit, args.legacy)
    elif args.command == "review":
        await review_question(args.exercise_id, args.decision, args.reviewer, args.notes, args.release_id)
    elif args.command == "verify-existing":
        if args.topic not in LESSON_SEQUENCE:
            raise ValueError(f"Tema desconocido: {args.topic}")
        await verify_existing(args.topic, args.release_id, args.limit)
    return 0


async def main() -> None:
    args = _parser().parse_args()
    try:
        code = await run(args)
    finally:
        await client.close()
    raise SystemExit(code)


if __name__ == "__main__":
    asyncio.run(main())
