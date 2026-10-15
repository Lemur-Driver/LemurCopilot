import unittest
from datetime import datetime

from app.models import ConceptMasteryEntry, Student
from app.services.mastery_service import (
    build_concept_mastery_update,
    summarize_quiz_concept_scores,
)


class ConceptMasteryTests(unittest.TestCase):
    def test_existing_student_defaults_to_empty_concept_mastery(self):
        student = Student(google_sub="google-sub", name="Student", email="student@example.com")
        self.assertEqual(student.concept_mastery, {})
        legacy_student = Student.model_validate({
            "google_sub": "legacy-sub", "name": "Legacy", "email": "legacy@example.com", "mastery": {},
        })
        self.assertEqual(legacy_student.concept_mastery, {})

    def test_correct_answer_increments_unique_concepts(self):
        now = datetime(2026, 10, 14)
        update = build_concept_mastery_update(
            "C1.1", ["Velocidad segura", "velocidad-segura", "distancia de reacción"], [],
            correct=True, exercise_id="exercise-1", question="Pregunta", timestamp=now,
        )
        self.assertEqual(update["$inc"], {
            "concept_mastery.C1.1.distancia_de_reaccion.attempts": 1,
            "concept_mastery.C1.1.distancia_de_reaccion.correct": 1,
            "concept_mastery.C1.1.velocidad_segura.attempts": 1,
            "concept_mastery.C1.1.velocidad_segura.correct": 1,
        })
        self.assertEqual(update["$set"]["concept_mastery.C1.1.velocidad_segura.last_seen"], now)
        self.assertNotIn("$push", update)

    def test_wrong_answer_tracks_misconceptions_and_caps_recent_errors(self):
        update = build_concept_mastery_update(
            "C1.1", ["velocidad_segura"], ["confunde limite legal", "confunde-limite-legal"],
            correct=False, exercise_id="exercise-2", question="Pregunta", timestamp=datetime(2026, 10, 14),
        )
        self.assertEqual(update["$inc"], {
            "concept_mastery.C1.1.velocidad_segura.attempts": 1,
            "concept_mastery.C1.1.velocidad_segura.incorrect": 1,
            "concept_mastery.C1.1.velocidad_segura.misconception_counts.confunde_limite_legal": 1,
        })
        error = update["$push"]["concept_mastery.C1.1.velocidad_segura.recent_errors"]
        self.assertEqual(error["$slice"], -10)
        self.assertEqual(error["$each"][0]["exercise_id"], "exercise-2")
        self.assertEqual(error["$each"][0]["misconception_tags"], ["confunde_limite_legal"])

    def test_concept_quiz_score_uses_only_attempts_tagged_with_concept(self):
        answers = [
            {"is_correct": True, "concept_tags": ["señales de tránsito"]},
            {"is_correct": False, "concept_tags": ["señales-de-tránsito"]},
            {"is_correct": True, "concept_tags": ["velocidad"]},
        ]
        self.assertEqual(summarize_quiz_concept_scores(answers, 3), {
            "senales_de_transito": 0.5,
            "velocidad": 1.0,
        })

    def test_unlabeled_legacy_question_does_not_modify_concept_mastery(self):
        self.assertIsNone(build_concept_mastery_update(
            "C1.1", [], [], correct=False, exercise_id="exercise-3", question="Pregunta", timestamp=datetime(2026, 10, 14),
        ))

    def test_concept_mastery_model_defaults_and_validates(self):
        self.assertEqual(ConceptMasteryEntry().attempts, 0)
        self.assertEqual(ConceptMasteryEntry().recent_errors, [])
        with self.assertRaises(ValueError):
            ConceptMasteryEntry(attempts=1, correct=1, incorrect=1)


if __name__ == "__main__":
    unittest.main()
