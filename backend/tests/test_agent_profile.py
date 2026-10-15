import unittest

from app.agents.profile import build_agent_profile
from app.models import ConceptMasteryEntry, Student


class AgentProfileTests(unittest.TestCase):
    def test_builds_compact_profile_for_requested_topic(self):
        student = Student(
            google_sub="test-user",
            name="Estudiante de prueba",
            email="test@example.com",
            mastery={
                "C1": {
                    "1": {
                        "score": 0.5,
                        "last_score": 0.5,
                        "best_score": 0.7,
                        "attempts": 2,
                    }
                }
            },
            concept_mastery={
                "C1.1": {
                    "distancia_reaccion": ConceptMasteryEntry(
                        attempts=2,
                        correct=1,
                        incorrect=1,
                        score=0.5,
                        misconception_counts={"confunde_reaccion_y_frenado": 1},
                        recent_errors=[{
                            "question": "Texto de pregunta que no debe incluirse",
                            "misconception_tags": ["confunde_reaccion_y_frenado"],
                        }],
                    ),
                },
                "C1.2": {
                    "otro_concepto": ConceptMasteryEntry(
                        attempts=1,
                        correct=1,
                        score=1.0,
                    ),
                },
            },
        )

        profile = build_agent_profile(student, "C1.1")

        self.assertEqual(profile["topic"], "C1.1")
        self.assertEqual(profile["current_mastery"]["last_score"], 0.5)
        self.assertEqual(
            [concept["tag"] for concept in profile["concepts"]],
            ["distancia_reaccion"],
        )
        self.assertEqual(
            profile["weak_concepts"][0]["tag"],
            "distancia_reaccion",
        )
        self.assertEqual(
            profile["concepts"][0]["recent_misconceptions"],
            ["confunde_reaccion_y_frenado"],
        )
        self.assertNotIn("Texto de pregunta que no debe incluirse", str(profile))

    def test_unseen_topic_has_empty_mastery_and_concepts(self):
        student = Student(
            google_sub="new-user",
            name="Estudiante nuevo",
            email="new@example.com",
        )

        profile = build_agent_profile(student, "C1.1")

        self.assertIsNone(profile["current_mastery"])
        self.assertEqual(profile["concepts"], [])
        self.assertEqual(profile["weak_concepts"], [])


if __name__ == "__main__":
    unittest.main()