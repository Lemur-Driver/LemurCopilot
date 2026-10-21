import math
import unittest
from unittest.mock import AsyncMock, patch

from app.agents.nodes import choose_strategy, retrieve_content


class ChooseStrategyTests(unittest.TestCase):
    def test_missing_or_invalid_score_uses_standard(self):
        states = [
            {},
            {"learner_profile": {}},
            {"learner_profile": {"current_mastery": {"last_score": None}}},
            {"learner_profile": {"current_mastery": {"last_score": True}}},
            {"learner_profile": {"current_mastery": {"last_score": math.nan}}},
            {"learner_profile": {"current_mastery": {"last_score": math.inf}}},
            {"learner_profile": {"current_mastery": {"last_score": 1.2}}},
            {"learner_profile": {"current_mastery": {"last_score": -0.1}}},
        ]

        for state in states:
            with self.subTest(state=state):
                self.assertEqual(choose_strategy(state)["strategy"], "standard")

    def test_score_below_point_six_uses_reinforcement(self):
        self.assertEqual(
            choose_strategy({
                "learner_profile": {"current_mastery": {"last_score": 0.59}}
            })["strategy"],
            "reinforcement",
        )

    def test_boundary_scores_use_expected_strategies(self):
        self.assertEqual(
            choose_strategy({
                "learner_profile": {"current_mastery": {"last_score": 0.6}}
            })["strategy"],
            "standard",
        )
        self.assertEqual(
            choose_strategy({
                "learner_profile": {"current_mastery": {"last_score": 0.85}}
            })["strategy"],
            "challenge",
        )


class RetrieveContentNodeTests(unittest.IsolatedAsyncioTestCase):
    async def test_retrieves_content_for_graph_decision(self):
        content = {
            "release_id": "release-1",
            "lesson": {"lesson": {"title": "Tema"}},
            "lesson_variant": "reinforcement",
            "exercises": [{"_id": "exercise-1"}],
            "content_errors": [],
        }
        with patch(
            "app.agents.nodes.retrieve_agent_content",
            new_callable=AsyncMock,
            return_value=content,
        ) as retrieve:
            result = await retrieve_content({
                "topic": "C1.2",
                "strategy": "reinforcement",
                "focus_concepts": ["distancia_reaccion"],
            })

        retrieve.assert_awaited_once_with(
            topic="C1.2",
            strategy="reinforcement",
            focus_concepts=["distancia_reaccion"],
        )
        self.assertEqual(result, content)

    async def test_retrieval_failure_returns_empty_content_safely(self):
        with patch(
            "app.agents.nodes.retrieve_agent_content",
            new_callable=AsyncMock,
            side_effect=RuntimeError("database unavailable"),
        ):
            result = await retrieve_content({
                "topic": "C1.2",
                "strategy": "standard",
            })

        self.assertIsNone(result["release_id"])
        self.assertIsNone(result["lesson"])
        self.assertEqual(result["exercises"], [])
        self.assertEqual(result["content_errors"], [
            "Falló la recuperación de contenido: RuntimeError"
        ])


if __name__ == "__main__":
    unittest.main()