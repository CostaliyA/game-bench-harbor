import copy
import unittest
from reward import TASK, WEIGHTS, score


def trajectory():
    rows = [{"seq": 0, "type": "start", "task": TASK}]
    rows += [{"seq": i + 1, "type": "milestone", "name": name} for i, name in enumerate(WEIGHTS)]
    rows += [{"seq": 10, "type": "day3_dawn", "cycle": 2, "alive": True,
              "health": 100, "hunger": 75, "sanity": 100, "food_hunger": 25,
              "stock": {"log": 6, "cutgrass": 6, "twigs": 4}, "camp_intact": True,
              "at_camp": True, "backpack_equipped": True, "spear_held": True}]
    return rows


class RewardTests(unittest.TestCase):
    def test_complete_success(self):
        self.assertEqual(score(trajectory())["reward"], 1)

    def test_each_terminal_requirement_matters(self):
        for key, value in {"cycle": 1, "alive": False, "health": 99.9, "hunger": 74.9,
                           "sanity": 99.9, "food_hunger": 24.9, "camp_intact": False,
                           "at_camp": False, "backpack_equipped": False, "spear_held": False}.items():
            with self.subTest(key=key):
                rows = trajectory(); rows[-1][key] = value
                self.assertEqual(score(rows)["reward"], .75)
        for name in ("log", "cutgrass", "twigs"):
            rows = trajectory(); rows[-1]["stock"][name] -= 1
            self.assertFalse(score(rows)["success"])

    def test_no_terminal_bonus_for_missing_milestone(self):
        for i in range(1, 10):
            rows = trajectory(); rows.pop(i)
            self.assertFalse(score(rows)["success"])

    def test_death_is_final(self):
        rows = trajectory(); rows.insert(1, {"seq": 1, "type": "death"})
        self.assertEqual(score(rows)["reward"], 0)
        self.assertEqual(score(rows)["terminal"], "death")

    def test_duplicates_do_not_accumulate(self):
        rows = trajectory(); rows.insert(2, {"seq": 2, "type": "milestone", "name": "tools"})
        for i, row in enumerate(rows): row["seq"] = i
        self.assertEqual(score(rows)["reward"], 1)

    def test_waiting_and_incomplete(self):
        rows = trajectory()
        self.assertEqual(score([rows[0], rows[-1]])["reward"], 0)
        self.assertFalse(score(rows[:-1])["complete"])

    def test_wrong_task_invalid_and_sequence(self):
        rows = trajectory(); rows[0]["task"] = "dst-first-night-v1"
        with self.assertRaises(ValueError): score(rows)
        rows = trajectory(); rows[-1]["type"] = "invalid"
        self.assertEqual(score(rows)["reward"], 0)
        rows = trajectory(); rows[2]["seq"] = 1
        with self.assertRaises(ValueError): score(rows)

    def test_nan_does_not_succeed(self):
        rows = trajectory(); rows[-1]["health"] = float("nan")
        self.assertFalse(score(rows)["success"])
        rows = trajectory(); rows[-1]["stock"]["log"] = float("inf")
        self.assertFalse(score(rows)["success"])


if __name__ == "__main__": unittest.main()
