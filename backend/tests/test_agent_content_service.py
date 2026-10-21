import unittest
from unittest.mock import AsyncMock, patch

from bson import ObjectId

from app.services.agent_content_service import (
    _eligible_exercises,
    _rank_exercises,
    retrieve_agent_content,
)


def exercise(
    exercise_id: str,
    *,
    topic: str = "C1.2",
    release_id: str = "release-1",
    status: str = "published",
    verified: bool = True,
    review_status: str | None = None,
    concept_tags: list[str] | None = None,
    difficulty: float = 0.5,
    times_served: int = 0,
) -> dict:
    return {
        "_id": ObjectId(exercise_id),
        "topic": topic,
        "release_id": release_id,
        "status": status,
        "verified": verified,
        "review_status": review_status,
        "question": f"Pregunta {exercise_id}",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "correct_answer": "A",
        "explanation": "A es correcta.",
        "concept_tags": concept_tags or [],
        "difficulty": difficulty,
        "times_served": times_served,
    }


class AgentContentServiceTests(unittest.IsolatedAsyncioTestCase):
    def test_eligibility_excludes_unpublished_unverified_wrong_release_and_invalid(self):
        docs = [
            exercise("000000000000000000000001"),
            exercise("000000000000000000000002", status="ready"),
            exercise("000000000000000000000003", verified=False),
            exercise("000000000000000000000004", release_id="old-release"),
            exercise("000000000000000000000005", review_status="rejected"),
        ]

        eligible = _eligible_exercises(docs, "C1.2", "release-1")

        self.assertEqual([str(item["_id"]) for item in eligible], ["000000000000000000000001"])

    def test_ranking_prefers_focus_coverage_then_low_exposure_and_difficulty(self):
        exercises = [
            exercise("000000000000000000000001", concept_tags=["other"], times_served=0),
            exercise("000000000000000000000002", concept_tags=["weak"], times_served=2),
            exercise("000000000000000000000003", concept_tags=["weak"], times_served=0),
        ]

        ranked = _rank_exercises(exercises, ["weak"], 0.5)

        self.assertEqual(
            [str(item["_id"]) for item in ranked],
            ["000000000000000000000003", "000000000000000000000001", "000000000000000000000002"],
        )

    async def test_retrieval_uses_published_release_and_standard_fallback(self):
        pool = [
            exercise("000000000000000000000001", concept_tags=["weak"]),
            exercise("000000000000000000000002", concept_tags=["other"]),
            exercise("000000000000000000000003", concept_tags=["weak"], difficulty=0.7),
        ]
        lesson = {"_id": "lesson-1", "lesson": {"title": "Lección"}}

        with (
            patch("app.services.agent_content_service.get_published_release_id", new_callable=AsyncMock, return_value="release-1"),
            patch("app.services.agent_content_service.get_published_lesson", new_callable=AsyncMock, side_effect=[None, lesson]) as get_lesson,
            patch("app.services.agent_content_service._pool_documents", new_callable=AsyncMock, return_value=pool),
        ):
            result = await retrieve_agent_content("C1.2", "reinforcement", ["weak"])

        self.assertEqual(get_lesson.await_args_list[0].args, ("C1.2", "reinforcement", "release-1"))
        self.assertEqual(get_lesson.await_args_list[1].args, ("C1.2", "standard", "release-1"))
        self.assertEqual(result["release_id"], "release-1")
        self.assertEqual(result["lesson_variant"], "standard")
        self.assertEqual(len(result["exercises"]), 3)
        self.assertEqual(result["content_errors"], [])

    async def test_missing_release_returns_no_content(self):
        with patch(
            "app.services.agent_content_service.get_published_release_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await retrieve_agent_content("C1.2", "standard", [])

        self.assertIsNone(result["release_id"])
        self.assertIsNone(result["lesson"])
        self.assertEqual(result["exercises"], [])
        self.assertTrue(result["content_errors"])

    async def test_insufficient_pool_does_not_return_partial_quiz(self):
        pool = [exercise("000000000000000000000001")]

        with (
            patch("app.services.agent_content_service.get_published_release_id", new_callable=AsyncMock, return_value="release-1"),
            patch("app.services.agent_content_service.get_published_lesson", new_callable=AsyncMock, return_value={"lesson": {"title": "Lección"}}),
            patch("app.services.agent_content_service._pool_documents", new_callable=AsyncMock, return_value=pool),
        ):
            result = await retrieve_agent_content("C1.2", "standard", [])

        self.assertEqual(result["exercises"], [])
        self.assertEqual(len(result["content_errors"]), 1)
        self.assertIn("Pool insuficiente", result["content_errors"][0])


if __name__ == "__main__":
    unittest.main()
