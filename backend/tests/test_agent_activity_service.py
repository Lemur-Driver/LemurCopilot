import unittest
from unittest.mock import patch

from app.services import agent_activity_service



class FakeCursor:
    def __init__(self, documents):
        self.documents = documents
        self.sort_args = None
        self.limit_value = None

    def sort(self, field, direction):
        self.sort_args = (field, direction)
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    async def to_list(self, length):
        return self.documents[:length]


class AgentActivityServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_returns_recent_quiz_summary_without_question_text(self):
        cursor = FakeCursor([
            {
                "quiz_topic": "C1.2",
                "completed_at": None,
                "score": 2 / 3,
                "answers": [
                    {"is_correct": True, "question": "No incluir este texto"},
                    {"is_correct": False, "question": "Tampoco incluir este texto"},
                    {"is_correct": True},
                ],
            }
        ])

        with patch.object(
            agent_activity_service.sessions_collection,
            "find",
            return_value=cursor,
        ) as find:
            result = await agent_activity_service.get_recent_quiz_activity(
                "507f1f77bcf86cd799439011"
            )

        query, projection = find.call_args.args
        self.assertEqual(query["student_id"].binary, bytes.fromhex("507f1f77bcf86cd799439011"))
        self.assertEqual(query["quiz_status"], "completed")
        self.assertNotIn("question", projection)
        self.assertNotIn("messages", projection)
        self.assertEqual(cursor.sort_args, ("completed_at", -1))
        self.assertEqual(cursor.limit_value, 10)
        self.assertEqual(result, [{
            "topic": "C1.2",
            "completed_at": None,
            "score": 2 / 3,
            "correct_answers": 2,
            "incorrect_answers": 1,
        }])
        self.assertNotIn("No incluir este texto", str(result))

    async def test_rejects_invalid_student_id(self):
        with self.assertRaises(ValueError):
            await agent_activity_service.get_recent_quiz_activity("not-an-object-id")


if __name__ == "__main__":
    unittest.main()