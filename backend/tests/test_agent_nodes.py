import math
import unittest

from app.agents.nodes import choose_strategy


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


if __name__ == "__main__":
    unittest.main()