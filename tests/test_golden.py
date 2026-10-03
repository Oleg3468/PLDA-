import unittest

from app.services.evaluator import load_cases, run_golden_evaluation


class GoldenSetTests(unittest.TestCase):
    """Золотой набор: регрессионный контроль качества сервиса PLDA.

    Падение любого кейса означает регрессию в промптах, правилах,
    сид-каталоге или карточках агентов — выясняйте причину до слияния.
    """

    def test_golden_set_fully_passes(self):
        report = run_golden_evaluation()
        failed = [
            {"id": case["id"], "failed": case["failed"]}
            for case in report["cases"]
            if not case["passed"]
        ]
        self.assertTrue(
            report["all_passed"],
            msg=f"Золотой набор провален: {failed}",
        )

    def test_golden_set_covers_enough_cases(self):
        report = run_golden_evaluation()
        self.assertGreaterEqual(report["cases_total"], 10)
        self.assertGreaterEqual(report["checks_total"], 60)

    def test_golden_set_covers_both_planes(self):
        report = run_golden_evaluation()
        planes = set()
        for case in report["cases"]:
            planes.update(case["planes"])
        self.assertIn("physical_person", planes)
        self.assertIn("human", planes)

    def test_golden_file_is_valid_json_with_ids(self):
        cases = load_cases()
        self.assertTrue(cases)
        identifiers = [case["id"] for case in cases]
        self.assertEqual(len(identifiers), len(set(identifiers)))


if __name__ == "__main__":
    unittest.main()
