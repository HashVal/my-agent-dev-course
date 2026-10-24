"""Offline acceptance checks: python3 check_tool.py read_tool.local.py.

The public scaffold is intentionally incomplete. These tests are expected to
fail until the learner implements both exercises. No API is called.
"""

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class ToolChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.root = base / "docs"
        self.root.mkdir()
        self.text = "# 教学资料\n这是测试夹具，不是模型输出。\n"
        (self.root / "limits.md").write_text(self.text, encoding="utf-8")
        (self.root / "nested").mkdir()
        (self.root / "nested/a.md").write_text("nested", encoding="utf-8")
        self.outside = base / "docs-backup"
        self.outside.mkdir()
        (self.outside / "outside.md").write_text("OUTSIDE_SENTINEL", encoding="utf-8")

    def call(self, arguments, name="read_document"):
        return {
            "id": "call_test_01", "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments)},
        }

    def result(self, arguments):
        message = lab.dispatch(self.call(arguments), self.root)
        self.assertEqual(message["role"], "tool")
        self.assertEqual(message["tool_call_id"], "call_test_01")
        self.assertIsInstance(message["content"], str)
        return json.loads(message["content"])

    def error(self, path, code):
        result = self.result({"path": path})
        self.assertIs(result["ok"], False)
        self.assertEqual(result["error"]["code"], code)
        self.assertNotIn("content", result)
        self.assertNotIn(str(self.root.parent), json.dumps(result))
        self.assertNotIn("OUTSIDE_SENTINEL", json.dumps(result))

    def test_read_full_document_and_relative_source(self):
        self.assertEqual(self.result({"path": "limits.md"}), {
            "ok": True, "file": "limits.md", "content": self.text,
        })
        self.assertEqual(self.result({"path": "nested/a.md"})["file"], "nested/a.md")

    def test_invalid_arguments_do_not_reach_reader(self):
        with patch.object(lab, "read_document") as reader:
            for arguments in ({}, [], None, {"path": None}, {"path": 1},
                              {"path": " "}, {"path": "\x00"},
                              {"path": "limits.md", "root": "/"}):
                with self.subTest(arguments=arguments):
                    result = self.result(arguments)
                    self.assertEqual(result["error"]["code"], "invalid_arguments")
            reader.assert_not_called()

    def test_unknown_tool_and_invalid_json_do_not_reach_reader(self):
        bad_json = self.call({"path": "limits.md"})
        bad_json["function"]["arguments"] = '{"path":'
        with patch.object(lab, "read_document") as reader:
            for call, code in ((bad_json, "invalid_arguments"),
                               (self.call({}, "run_shell"), "unknown_tool")):
                result = json.loads(lab.dispatch(call, self.root)["content"])
                self.assertEqual(result["error"]["code"], code)
            reader.assert_not_called()

    def test_absolute_and_parent_paths(self):
        for path in (str(self.root / "limits.md"), "../docs-backup/outside.md",
                     "nested/../limits.md"):
            with self.subTest(path=path):
                with patch("builtins.open", side_effect=AssertionError("must reject before open")), \
                        patch("io.open", side_effect=AssertionError("must reject before open")):
                    self.error(path, "forbidden_path")

    def test_symlink_escape_and_sibling_prefix(self):
        # Linux classroom fixture: both paths begin with the same text prefix.
        (self.root / "escape.md").symlink_to(self.outside / "outside.md")
        (self.root / "escape-dir").symlink_to(self.outside, target_is_directory=True)
        with patch("builtins.open", side_effect=AssertionError("must reject before open")), \
                patch("io.open", side_effect=AssertionError("must reject before open")):
            self.error("escape.md", "forbidden_path")
            self.error("escape-dir/outside.md", "forbidden_path")

    def test_internal_symlink_has_canonical_source(self):
        (self.root / "alias.md").symlink_to(self.root / "limits.md")
        self.assertEqual(self.result({"path": "alias.md"})["file"], "limits.md")

    def test_missing_directory_and_wrong_extension(self):
        self.error("missing.md", "not_found")
        (self.root / "directory.md").mkdir()
        self.error("directory.md", "invalid_file")
        (self.root / "notes.txt").write_text("not Markdown", encoding="utf-8")
        self.error("notes.txt", "invalid_file")

    def test_size_limit_measured_in_bytes(self):
        (self.root / "exact.md").write_bytes(b"x" * lab.MAX_BYTES)
        self.assertEqual(len(self.result({"path": "exact.md"})["content"]), lab.MAX_BYTES)
        (self.root / "large.md").write_bytes(b"x" * (lab.MAX_BYTES + 1))
        self.error("large.md", "too_large")
        (self.root / "unicode.md").write_text("中" * (lab.MAX_BYTES // 3 + 1), encoding="utf-8")
        self.error("unicode.md", "too_large")

    def test_invalid_utf8(self):
        (self.root / "bad.md").write_bytes(b"\xff")
        self.error("bad.md", "invalid_encoding")

    def test_result_association_and_message_order(self):
        request = lab.build_request()
        before = copy.deepcopy(request)
        response = lab.demo_response("limits.md")
        messages = lab.execute_one_turn(request, response, self.root)
        self.assertEqual(request, before)
        self.assertEqual([m["role"] for m in messages], ["system", "user", "assistant", "tool"])
        self.assertEqual(messages[-1]["tool_call_id"], messages[-2]["tool_calls"][0]["id"])
        self.assertEqual(json.loads(messages[-1]["content"])["content"], self.text)

    def test_failed_read_still_has_matching_tool_result(self):
        messages = lab.execute_one_turn(lab.build_request(), lab.demo_response("missing.md"), self.root)
        self.assertEqual(messages[-1]["tool_call_id"], "call_demo_01")
        self.assertEqual(json.loads(messages[-1]["content"])["error"]["code"], "not_found")

    def test_invalid_envelope_batch_and_finish_reason_do_not_execute(self):
        missing_id = lab.demo_response("limits.md")
        del missing_id["choices"][0]["message"]["tool_calls"][0]["id"]
        batch = lab.demo_response("limits.md")
        batch["choices"][0]["message"]["tool_calls"].append(self.call({"path": "limits.md"}))
        truncated = lab.demo_response("limits.md")
        truncated["choices"][0]["finish_reason"] = "length"
        no_call = {"choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "text"}}]}
        with patch.object(lab, "read_document") as reader:
            for response in (missing_id, batch, truncated, no_call):
                with self.subTest(response=response):
                    with self.assertRaises(ValueError):
                        lab.execute_one_turn(lab.build_request(), response, self.root)
            reader.assert_not_called()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 check_tool.py path/to/read_tool.local.py")
    spec = importlib.util.spec_from_file_location("learner_tool", Path(sys.argv[1]).resolve())
    lab = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lab)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
