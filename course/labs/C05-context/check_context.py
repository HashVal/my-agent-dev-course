"""Offline contract checks, including the deliberate evidence-loss counterexample."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import load


class Checks(unittest.TestCase):
    def test_long_result_is_marked_without_mutation(self):
        body = {"ok": True, "file": "a.md", "content": "abcMIDDLExyz"}
        before = copy.deepcopy(body)
        result = lab.trim_result(body, 6)
        self.assertEqual(result["content"], "abc" + lab.MARKER + "xyz")
        self.assertEqual(result["original_chars"], 12)
        self.assertIs(result["truncated"], True)
        self.assertEqual(result["file"], "a.md")
        self.assertEqual(body, before)

    def test_short_error_and_odd_limit(self):
        for body in ({"ok": True, "content": "abc"}, {"ok": False, "error": {"code": "not_found"}}):
            result = lab.trim_result(body, 3)
            self.assertEqual(result, body)
            self.assertIsNot(result, body)
        self.assertEqual(lab.trim_result({"ok": True, "content": "abcdef"}, 3)["content"], "a" + lab.MARKER + "ef")

    def test_history_protocol_and_original_evidence_survive(self):
        messages = lab.fixture()
        before = copy.deepcopy(messages)
        projected = lab.project_messages(messages, 120)
        self.assertEqual(projected[:3], messages[:3])
        self.assertEqual(projected[3]["tool_call_id"], "c05_1")
        self.assertNotIn("QH-742", projected[3]["content"])
        self.assertIn("QH-742", messages[3]["content"])
        self.assertEqual(messages, before)

    def test_invalid_limit(self):
        for value in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                lab.project_messages(lab.fixture(), value)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("python3 check_context.py path/to/context.local.py")
    lab = load(sys.argv[1])
    unittest.main(argv=[sys.argv[0]], verbosity=2)
