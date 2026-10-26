"""Grader calibration with fictional responses, including false-positive traps."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import load


class Checks(unittest.TestCase):
    def base(self):
        return dict(status="completed", schema_ok=True, citations_ok=True,
                    answerability_ok=True, semantic_review=True)

    def test_each_layer(self):
        for updates, expected in [({}, ("pass", "accepted")),
            ({"status": "max_steps"}, ("fail", "runtime")),
            ({"schema_ok": False}, ("fail", "format")),
            ({"citations_ok": False}, ("fail", "citation")),
            ({"answerability_ok": False}, ("fail", "answerability")),
            ({"semantic_review": None}, ("pending", "semantic_review")),
            ({"semantic_review": False}, ("fail", "semantic"))]:
            with self.subTest(updates=updates):
                r = lab.decide({**self.base(), **updates})
                self.assertEqual((r["verdict"], r["category"]), expected)

    def test_manual_pass_cannot_override_runtime_or_bad_citation(self):
        r = lab.decide({**self.base(), "status": "model_error", "citations_ok": False})
        self.assertEqual(r, {"verdict": "fail", "category": "runtime"})

    def test_true_quote_with_wrong_conclusion_needs_semantic_review(self):
        answer = {"answerable": True, "answer": "T01 已达到上限。",
                  "citations": [{"file": "a.md", "quote": "共 2 次；上限 3 次。"}], "missing_information": []}
        record = {"status": "completed", "answer": json.dumps(answer), "corpus": {"a.md": "共 2 次；上限 3 次。"}}
        expectation = {"answerable": True, "required_files": ["a.md"]}
        observation = lab.observe(record, expectation)
        self.assertTrue(observation["citations_ok"])
        self.assertEqual(lab.decide(observation)["verdict"], "pending")
        observation = lab.observe(record, expectation, {"correct": False})
        self.assertEqual(lab.decide(observation)["category"], "semantic")

    def test_missing_runs_are_not_dropped(self):
        report = lab.evaluate(lab.template())
        self.assertEqual(len(report["rows"]), 20)
        self.assertTrue(all(r["verdict"] == "not_run" for r in report["rows"]))
        with self.assertRaises(ValueError):
            lab.evaluate(lab.template()[:-1])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("python3 check_evaluation.py path/to/evaluate.local.py")
    lab = load(sys.argv[1])
    unittest.main(argv=[sys.argv[0]], verbosity=2)
