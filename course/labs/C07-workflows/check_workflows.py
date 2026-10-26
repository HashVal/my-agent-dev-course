"""Check the fixed strategy with spies, and teacher-provided budget guards."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import load


class Checks(unittest.TestCase):
    def test_fixed_searches_original_question_once_then_answers(self):
        events = []
        class Fake:
            def search(self, q): events.append(("search", q))
            def request(self):
                events.append(("request",))
                return "final", {"content": "answer"}
            def finish(self, status, message):
                events.append((status, message["content"]))
                return "record"
        self.assertEqual(lab.run_fixed(Fake(), "why"), "record")
        self.assertEqual(events, [("search", "why"), ("request",), ("completed", "answer")])

    def test_unexpected_tool_is_not_executed(self):
        class Fake:
            def search(self, q): pass
            def request(self): return "tool", {}
            def finish(self, *args): self.fail("must not complete")
        with self.assertRaises(lab.c04.RunFailure):
            lab.run_fixed(Fake(), "q")

    def test_hard_request_cap(self):
        session = lab.Session(lambda req: lab.c04.synthetic_final("done"), None, "q", "all", {})
        for _ in range(4): session.request()
        with self.assertRaises(lab.c04.RunFailure): session.request()
        self.assertEqual(session.record["model_calls"], 4)

    def test_synthetic_source_is_not_a_business_result(self):
        answer = lab.synthetic_model("any")({"messages": []})
        self.assertIn("模拟", answer["choices"][0]["message"]["content"])

    def test_exhausted_attempt_budget_blocks_dispatch(self):
        session = lab.Session(None, lambda call: self.fail("must not execute"), "q", "agent", {})
        session.record["tool_attempts"] = 3
        message = lab.c04.synthetic_call("limits.md", 1)["choices"][0]["message"]
        with self.assertRaises(lab.c04.RunFailure) as raised:
            session.execute(message)
        self.assertEqual(raised.exception.status, "max_tool_calls")
        self.assertEqual(session.record["tool_calls"], 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("python3 check_workflows.py path/to/compare.local.py")
    lab = load(sys.argv[1])
    unittest.main(argv=[sys.argv[0]], verbosity=2)
