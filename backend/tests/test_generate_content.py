import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from app.jobs.generate_content import (
    LESSON_VERIFICATION_VERSION,
    _lesson_is_current,
    _load_verified_questions,
    _parse_args,
    _question_generation_stop_reason,
    _verify_lesson,
)
from app.prompts.lesson_prompts import BASE_LESSON_PROMPT, LESSON_CONFIGS
from app.services.question_pool_service import question_fingerprint


class GenerateContentTests(unittest.TestCase):
    def test_lesson_generation_prompt_preserves_statistical_scope(self):
        config = LESSON_CONFIGS["C1.1"]
        self.assertIn("población", BASE_LESSON_PROMPT)
        self.assertIn("métricas distintas", BASE_LESSON_PROMPT)
        self.assertIn("personas conductoras fallecidas", config["teaching_strategy"])
        self.assertIn("distribuciones", config["teaching_strategy"])
        self.assertIn("ejemplos numéricos hipotéticos", config["teaching_strategy"])

    def test_lesson_verifier_distinguishes_indicators_and_scope_errors(self):
        async def verify_with_response(response):
            with patch("app.services.llm_service.generate_text", new=AsyncMock(return_value=response)):
                return await _verify_lesson({"introduction": "80% de siniestros urbanos; mayoría de fallecimientos fuera de ciudades."}, [])

        async def run_checks():
            valid = await verify_with_response('{"approved": true, "confidence": 0.95, "issues": []}')
            self.assertTrue(valid["approved"])

            with self.assertRaisesRegex(ValueError, "79% de las personas fallecidas"):
                await verify_with_response('{"approved": false, "confidence": 0.95, "issues": ["79% de las personas fallecidas no coincide con el dato sobre personas conductoras fallecidas"]}')

            with self.assertRaisesRegex(ValueError, "Verificador rechazó"):
                await verify_with_response('{"approved": false, "confidence": 0.95, "issues": ["Contradicción: siniestros y fallecimientos"]}')

            with self.assertRaisesRegex(ValueError, "Verificador rechazó"):
                await verify_with_response('{"approved": true, "confidence": 0.7, "issues": []}')

        asyncio.run(run_checks())
        self.assertEqual(LESSON_VERIFICATION_VERSION, "lesson-verifier-v2")

    def test_lessons_from_old_prompt_versions_are_regenerated(self):
        self.assertTrue(_lesson_is_current({
            "status": "ready",
            "verified": True,
            "prompt_version": "lesson-v2",
            "verification_version": "lesson-verifier-v2",
        }))
        self.assertFalse(_lesson_is_current({
            "status": "ready",
            "verified": True,
            "prompt_version": "lesson-v1",
            "verification_version": "lesson-verifier-v1",
        }))
        self.assertFalse(_lesson_is_current({
            "status": "ready",
            "verified": True,
            "prompt_version": "lesson-v2",
            "verification_version": "lesson-verifier-v1",
        }))

    def test_worker_options_configure_pool_target_and_limits(self):
        args = _parse_args([
            "--topic", "C1.2",
            "--question-time-limit", "3600",
            "--question-timeout", "240",
            "--question-minimum", "20",
            "--max-question-batches", "80",
        ])
        self.assertEqual(args.question_time_limit, 3600)
        self.assertEqual(args.question_timeout, 240)
        self.assertEqual(args.question_minimum, 20)
        self.assertEqual(args.max_question_batches, 80)

    def test_question_generation_stops_at_target_time_or_batch_limit(self):
        self.assertEqual(_question_generation_stop_reason(15, 15, 5, 60, 1, 10), "target_reached")
        self.assertEqual(_question_generation_stop_reason(4, 15, 60, 60, 1, 10), "time_limit_reached")
        self.assertEqual(_question_generation_stop_reason(4, 15, 20, 60, 10, 10), "batch_limit_reached")
        self.assertIsNone(_question_generation_stop_reason(4, 15, 20, 60, 9, 10))
        self.assertIsNone(_question_generation_stop_reason(4, 15, 20, 0, 10, 0))

    def test_verified_questions_from_same_release_are_kept_and_deduplicated(self):
        fingerprint = question_fingerprint("C1.2", "Pregunta única", ["A", "B", "C", "D"], 0, "release-1")
        questions = [
            {"_id": "one", "fingerprint": fingerprint, "question": "Pregunta única"},
            {"_id": "duplicate", "fingerprint": fingerprint, "question": "Pregunta única"},
            {"_id": "two", "fingerprint": "fingerprint-2", "question": "Otra pregunta"},
        ]
        cursor = Mock()
        cursor.to_list = AsyncMock(return_value=questions)
        collection = Mock()
        collection.find.return_value = cursor
        collection.update_many = AsyncMock()

        with patch("app.jobs.generate_content.exercises_collection", collection):
            result = asyncio.run(_load_verified_questions("C1.2", "release-1"))

        self.assertEqual([item["_id"] for item in result], ["one", "two"])
        collection.update_many.assert_awaited_once()
        query = collection.find.call_args.args[0]
        self.assertEqual(query["release_id"], "release-1")
        self.assertEqual(query["status"], "ready")
        self.assertIs(query["verified"], True)


if __name__ == "__main__":
    unittest.main()
