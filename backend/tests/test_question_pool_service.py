import unittest

from app.services.question_pool_service import normalize_question, question_fingerprint


class QuestionPoolServiceTests(unittest.TestCase):
    def test_normalize_question_collapses_whitespace_and_case(self):
        self.assertEqual(
            normalize_question("  ¿Qué   es el Sistema Seguro? "),
            "¿qué es el sistema seguro?",
        )

    def test_fingerprint_is_stable_for_equivalent_input(self):
        first = question_fingerprint("C1.1", "¿Qué es la velocidad?", ["A", "B", "C", "D"])
        second = question_fingerprint("C1.1", " ¿QUÉ es la velocidad? ", ["A", "B", "C", "D"])
        self.assertEqual(first, second)

    def test_fingerprint_changes_with_topic_or_options(self):
        original = question_fingerprint("C1.1", "Pregunta", ["A", "B", "C", "D"])
        different_topic = question_fingerprint("C1.2", "Pregunta", ["A", "B", "C", "D"])
        different_options = question_fingerprint("C1.1", "Pregunta", ["A", "B", "C", "E"])
        self.assertNotEqual(original, different_topic)
        self.assertNotEqual(original, different_options)


if __name__ == "__main__":
    unittest.main()