import re
import unicodedata
from datetime import datetime
from typing import Any

RECENT_ERROR_LIMIT = 10


def mastery_topic_key(topic: str) -> str:
    """Convert dotted lesson codes to safe flat keys for MongoDB updates."""
    return topic.replace(".", "_")


def normalize_mastery_tag(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    ascii_value = unicodedata.normalize("NFKD", value.casefold()).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9]+", "_", ascii_value).strip("_")
    return normalized or None


def summarize_quiz_concept_scores(answers: list[dict[str, Any]], assigned_count: int) -> dict[str, float]:
    if assigned_count <= 0:
        return {}
    correct_counts: dict[str, int] = {}
    seen_counts: dict[str, int] = {}
    for answer in answers:
        concepts = {
            concept
            for concept in (normalize_mastery_tag(tag) for tag in answer.get("concept_tags", []))
            if concept
        }
        for concept in concepts:
            seen_counts[concept] = seen_counts.get(concept, 0) + 1
            if answer.get("is_correct") is True:
                correct_counts[concept] = correct_counts.get(concept, 0) + 1
    return {
        concept: correct_counts.get(concept, 0) / count
        for concept, count in seen_counts.items()
    }


def build_concept_mastery_update(
    topic: str,
    concept_tags: list[Any],
    misconception_tags: list[Any],
    *,
    correct: bool,
    exercise_id: str,
    question: str,
    timestamp: datetime,
) -> dict[str, Any] | None:
    if not isinstance(topic, str) or not re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", topic):
        raise ValueError("Invalid topic for concept mastery")
    concepts = sorted({tag for item in concept_tags if (tag := normalize_mastery_tag(item))})
    if not concepts:
        return None

    increments: dict[str, int] = {}
    sets: dict[str, datetime] = {}
    pushes: dict[str, dict[str, Any]] = {}
    errors = []
    if not correct:
        normalized_misconceptions = sorted({
            tag for item in misconception_tags
            if (tag := normalize_mastery_tag(item))
        })
        errors = [{
            "exercise_id": exercise_id,
            "question": question,
            "misconception_tags": normalized_misconceptions,
            "timestamp": timestamp,
        }]

    for concept in concepts:
        prefix = f"concept_mastery.{topic}.{concept}"
        increments[f"{prefix}.attempts"] = 1
        increments[f"{prefix}.correct" if correct else f"{prefix}.incorrect"] = 1
        sets[f"{prefix}.last_seen"] = timestamp
        if errors:
            pushes[f"{prefix}.recent_errors"] = {"$each": errors, "$slice": -RECENT_ERROR_LIMIT}
        if not correct:
            for misconception in errors[0]["misconception_tags"]:
                increments[f"{prefix}.misconception_counts.{misconception}"] = 1

    update: dict[str, Any] = {"$inc": increments, "$set": sets}
    if pushes:
        update["$push"] = pushes
    return update
