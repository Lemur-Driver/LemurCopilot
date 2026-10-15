import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from bson import ObjectId

from app.services.question_pool_service import (
    _pool_documents,
    _stored_question_consistent,
    normalize_question,
    question_fingerprint,
    select_quiz,
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
            "question": "¿Cuál es la respuesta?",
            "options": ["A", "B", "C", "D"],
            "correct_index": 1,
            "correct_answer": "B",
            "explanation": "B es correcta.",
        }))
        invalid = {
            "question": "¿Cuál es la respuesta?",
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
            "concept_tags": ["concepto"],
            "misconception_tags": [],
            "difficulty": 0.5,
            "cognitive_skill": "recall",
        }
        validate_quiz_json({
            "language": "es",
            "questions": [question, question, question],
        })

    def test_pool_query_is_scoped_to_published_verified_release(self):
        cursor = AsyncMock()
        cursor.to_list.return_value = []
        with patch("app.services.question_pool_service.exercises_collection.find", return_value=cursor) as find:
            asyncio.run(_pool_documents("C1.1", "release-1"))

        find.assert_called_once_with({
            "topic": "C1.1",
            "language": "es",
            "release_id": "release-1",
            "status": "published",
            "verified": True,
            "$or": [{"review_status": None}, {"review_status": "approved"}],
        })

    def test_quiz_selection_never_generates_questions_and_pins_release(self):
        exercises = [
            {
                "_id": ObjectId(),
                "question": f"Pregunta {index}",
                "options": ["A", "B", "C", "D"],
                "correct_index": 0,
                "correct_answer": "A",
                "explanation": "Explicación",
                "status": "published",
                "verified": True,
                "times_served": 0,
            }
            for index in range(3)
        ]
        cursor = AsyncMock()
        cursor.to_list.return_value = exercises

        class EmptySessionsCursor:
            def __aiter__(self):
                return self

            async def __anext__(self):
                raise StopAsyncIteration

        sessions_cursor = EmptySessionsCursor()
        assignment = AsyncMock(inserted_id=ObjectId())

        with (
            patch("app.services.question_pool_service.exercises_collection.find", return_value=cursor),
            patch("app.services.question_pool_service.sessions_collection.find", return_value=sessions_cursor),
            patch("app.services.question_pool_service.sessions_collection.insert_one", new=AsyncMock(return_value=assignment)) as insert,
            patch("app.services.question_pool_service.exercises_collection.update_one", new=AsyncMock()),
            patch("app.services.quiz_service.generate_quiz", new=AsyncMock(side_effect=AssertionError("generation must stay in the worker"))) as generate,
        ):
            quiz = asyncio.run(select_quiz(str(ObjectId()), "C1.1", "release-1"))

        self.assertEqual(len(quiz["questions"]), 3)
        self.assertEqual(insert.await_args.args[0]["quiz_release_id"], "release-1")
        generate.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()