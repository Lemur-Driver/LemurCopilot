import unittest
from datetime import datetime

from pydantic import ValidationError

from app.models import ContentJob, ContentRelease, Exercise, GeneratedLesson


class ContentModelTests(unittest.TestCase):
    def test_existing_exercise_documents_keep_legacy_defaults(self):
        exercise = Exercise.model_validate({"question": "Pregunta", "options": ["A", "B"]})
        self.assertEqual(exercise.status, "pending")
        self.assertFalse(exercise.verified)
        self.assertEqual(exercise.concept_tags, [])
        self.assertIsNone(exercise.release_id)

    def test_generated_lesson_requires_catalog_metadata(self):
        lesson = GeneratedLesson.model_validate({
            "topic": "C1.2",
            "variant": "standard",
            "lesson": {"title": "Título"},
            "content_version": "conaset-clase-b-2026-10",
            "prompt_version": "lesson-v1",
            "verification_version": "lesson-verifier-v1",
            "release_id": "release-1",
        })
        self.assertEqual(lesson.status, "pending")
        self.assertFalse(lesson.verified)

    def test_generated_lesson_rejects_unknown_variant(self):
        with self.assertRaises(ValidationError):
            GeneratedLesson.model_validate({
                "topic": "C1.2",
                "variant": "adaptive",
                "lesson": {},
                "content_version": "v1",
                "prompt_version": "p1",
                "verification_version": "v1",
                "release_id": "r1",
            })

    def test_release_and_job_validate_lifecycle_data(self):
        release = ContentRelease.model_validate({"release_id": "r1", "content_version": "v1"})
        job = ContentJob.model_validate({"job_id": "j1", "release_id": "r1", "topic": "C1.2"})
        self.assertEqual(release.status, "building")
        self.assertEqual(job.status, "pending")
        self.assertIsInstance(job.created_at, datetime)


if __name__ == "__main__":
    unittest.main()
