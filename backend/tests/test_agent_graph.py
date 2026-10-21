import unittest

from app.agents.graph import agent_graph
from app.agents.profile import build_agent_profile
from app.models import ConceptMasteryEntry, Student
from app.agents.runner import run_agent_for_student
from unittest.mock import AsyncMock, patch

class AgentGraphTests(unittest.IsolatedAsyncioTestCase):
    def test_graph_selects_strategy_and_preserves_input(self):
        cases = [
            (None, "standard"),
            (0.4, "reinforcement"),
            (0.7, "standard"),
            (0.9, "challenge"),
        ]

        for score, expected_strategy in cases:
            with self.subTest(score=score):
                profile = {"current_mastery": {"last_score": score}}
                result = agent_graph.invoke({
                    "topic": "C1.2",
                    "learner_profile": profile,
                })

                self.assertEqual(result["focus_concepts"], [])
                self.assertEqual(result["strategy"], expected_strategy)
                self.assertEqual(result["topic"], "C1.2")
                self.assertEqual(result["learner_profile"], profile)
                self.assertTrue(result["decision_reason"])

    def test_graph_uses_strategy_from_summarized_student_profile(self):
        student = Student(
            google_sub="test-user",
            name="Estudiante de prueba",
            email="test@example.com",
            mastery={
                "C1_2": {
                    "score": 0.5,
                    "last_score": 0.4,
                    "best_score": 0.7,
                    "attempts": 2,
                }
            },
            concept_mastery={
                "C1_2": {
                    "distancia_reaccion": ConceptMasteryEntry(
                        attempts=2,
                        correct=1,
                        incorrect=1,
                        score=0.5,
                    )
                }
            },
        )

        profile = build_agent_profile(student, "C1.2")
        result = agent_graph.invoke({
            "topic": "C1.2",
            "learner_profile": profile,
        })

        self.assertEqual(result["focus_concepts"], ["distancia_reaccion"])
        self.assertTrue(result["focus_reason"])
        self.assertEqual(result["strategy"], "reinforcement")
        self.assertEqual(result["learner_profile"]["topic"], "C1.2")
        self.assertEqual(
            result["learner_profile"]["weak_concepts"][0]["tag"],
            "distancia_reaccion",
        )

    async def test_runner_builds_profile_and_invokes_graph(self):
        student = Student(
            id="507f1f77bcf86cd799439011",
            google_sub="test-user",
            name="Estudiante de prueba",
            email="test@example.com",
            mastery={
                "C1_2": {
                    "score": 0.4,
                    "last_score": 0.4,
                    "best_score": 0.6,
                    "attempts": 2,
                }
            },
            concept_mastery={
                "C1_2": {
                    "distancia_reaccion": ConceptMasteryEntry(
                        attempts=2,
                        correct=0,
                        incorrect=2,
                        score=0,
                    )
                }
            },
        )

        recent_activity = [{
            "topic": "C1.2",
            "completed_at": "2026-10-15T12:00:00",
            "score": 0.67,
            "correct_answers": 2,
            "incorrect_answers": 1,
        }]

        with patch(
            "app.agents.runner.get_recent_quiz_activity",
            new_callable=AsyncMock,
            return_value=recent_activity,
        ) as get_activity:
            result = await run_agent_for_student(student, "C1.2")

        get_activity.assert_awaited_once_with(student.id)
        self.assertEqual(
            result["learner_profile"]["recent_quiz_activity"],
            recent_activity,
        )

        self.assertEqual(result["strategy"], "reinforcement")
        self.assertEqual(result["learner_profile"]["topic"], "C1.2")
        self.assertEqual(
            result["learner_profile"]["weak_concepts"][0]["tag"],
            "distancia_reaccion",
        )
        self.assertEqual(result["content_request"], {
            "topic": "C1.2",
            "lesson_variant": "reinforcement",
            "focus_concepts": ["distancia_reaccion"],
            "question_count": 3,
        })


async def test_runner_rejects_unconfigured_topic(self):
        student = Student(
            google_sub="test-user",
            name="Estudiante de prueba",
            email="test@example.com",
        )

        with self.assertRaisesRegex(ValueError, "configuración pedagógica"):
            await run_agent_for_student(student, "C99.99")

if __name__ == "__main__":
    unittest.main()

