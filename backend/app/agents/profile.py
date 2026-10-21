from typing import Any

from app.models import ConceptMasteryEntry, Student, get_mastery_entry
from app.services.mastery_service import mastery_topic_key


MAX_WEAK_CONCEPTS = 5
MAX_RECENT_ERRORS = 3
MAX_MISCONCEPTIONS = 3
WEAK_SCORE_THRESHOLD = 0.6


def build_agent_profile(student: Student, topic: str) -> dict[str, Any]:
    topic_key = mastery_topic_key(topic)
    topic_mastery = get_mastery_entry(student.mastery, topic_key)
    current_mastery = None

    if topic_mastery:
        current_mastery = {
            "score": topic_mastery.score,
            "last_score": topic_mastery.last_score,
            "best_score": topic_mastery.best_score,
            "attempts": topic_mastery.attempts,
        }

    concepts = []

    for tag, raw_entry in student.concept_mastery.get(topic_key, {}).items():
        entry = (
            raw_entry
            if isinstance(raw_entry, ConceptMasteryEntry)
            else ConceptMasteryEntry.model_validate(raw_entry)
        )

        if entry.attempts == 0:
            continue

        recent_misconceptions = []
        for error in entry.recent_errors[-MAX_RECENT_ERRORS:]:
            recent_misconceptions.extend(
                tag
                for tag in error.get("misconception_tags", [])
                if isinstance(tag, str)
            )

        top_misconceptions = [
            tag
            for tag, _ in sorted(
                entry.misconception_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[:MAX_MISCONCEPTIONS]
        ]

        concepts.append({
            "tag": tag,
            "score": entry.score,
            "attempts": entry.attempts,
            "correct": entry.correct,
            "incorrect": entry.incorrect,
            "misconception_counts": {
                misconception: entry.misconception_counts[misconception]
                for misconception in top_misconceptions
            },
            "recent_misconceptions": list(dict.fromkeys(recent_misconceptions)),
        })

    concepts.sort(key=lambda item: (item["score"], item["tag"]))
    weak_concepts = [
        concept
        for concept in concepts
        if concept["score"] < WEAK_SCORE_THRESHOLD
    ][:MAX_WEAK_CONCEPTS]

    return {
        "topic": topic,
        "current_mastery": current_mastery,
        "concepts": concepts,
        "weak_concepts": weak_concepts,
    }