import unittest

from app.services.question_pool_service import (
    _stored_question_consistent,
    normalize_question,
    question_fingerprint,
)
from app.services.quiz_service import validate_quiz_json


class QuestionPoolServiceTests(unittest.TestCase):
    def test_normalize_question_collapses_whitespace_and_case(self):
        self.assertEqual(
            normalize_question("  ¿Qué   es el Sistema Seguro? "),
            "¿qué es el sistema seguro?",
        )

    def test_fingerprint_is_stable_for_equivalent_input(self):
        first = question_fingerprint("C1.1", "¿Qué es la velocidad?", ["A", "B", "C", "D"], 0)
        second = question_fingerprint("C1.1", " ¿QUÉ es la velocidad? ", ["A", "B", "C", "D"], 0)
        self.assertEqual(first, second)

    def test_fingerprint_changes_with_topic_options_or_correct_index(self):
        original = question_fingerprint("C1.1", "Pregunta", ["A", "B", "C", "D"], 0)
        different_topic = question_fingerprint("C1.2", "Pregunta", ["A", "B", "C", "D"], 0)
        different_options = question_fingerprint("C1.1", "Pregunta", ["A", "B", "C", "E"], 0)
        different_answer = question_fingerprint("C1.1", "Pregunta", ["A", "B", "C", "D"], 1)
        self.assertNotEqual(original, different_topic)
        self.assertNotEqual(original, different_options)
        self.assertNotEqual(original, different_answer)

    def test_pool_question_requires_consistent_index_and_answer_text(self):
        self.assertTrue(_stored_question_consistent({
            "options": ["A", "B", "C", "D"],
            "correct_index": 1,
            "correct_answer": "B",
            "explanation": "B es correcta.",
        }))
        invalid = {
            "options": ["A", "B", "C", "D"],
            "correct_index": 1,
            "correct_answer": "C",
            "explanation": "C es correcta.",
        }
        self.assertFalse(_stored_question_consistent(invalid))

    def test_quiz_validation_rejects_mismatched_answer_text_and_index(self):
        question = {
            "question": "¿Cuál es correcta?",
            "options": ["A", "B", "C", "D"],
            "correctAnswerText": "C",
            "correctAnswer": 1,
            "explanation": "C es correcta.",
            "evidence_refs": [{"page": 1, "chunk_index": 0, "quote": "evidencia"}],
        }
        with self.assertRaises(ValueError):
            validate_quiz_json({
                "language": "es",
                "questions": [question, question, question],
            })

    def test_quiz_validation_accepts_matching_answer_text_and_index(self):
        question = {
            "question": "¿Cuál es correcta?",
            "options": ["A", "B", "C", "D"],
            "correctAnswerText": "B",
            "correctAnswer": 1,
            "explanation": "B es correcta.",
            "evidence_refs": [{"page": 1, "chunk_index": 0, "quote": "evidencia"}],
        }
        validate_quiz_json({
            "language": "es",
            "questions": [question, question, question],
        })


if __name__ == "__main__":
    unittest.main()