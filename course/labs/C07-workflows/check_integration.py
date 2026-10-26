"""Offline cross-lesson checks using completed local modules and synthetic model replies."""

import argparse
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import load


def call(name, arguments, number):
    response = lab.c04.synthetic_call("limits.md", number)
    response["choices"][0]["message"]["tool_calls"][0]["function"] = {
        "name": name, "arguments": json.dumps(arguments)}
    return response


class Integration(unittest.TestCase):
    def test_fixed_feedback_is_in_the_only_model_request(self):
        requests = []
        def ask(request):
            requests.append(copy.deepcopy(request))
            return lab.c04.synthetic_final("synthetic final")
        result = lab.run("fixed", "T01 工具调用上限", ask, reader, retriever, loop)
        self.assertEqual(result["status"], "completed")
        self.assertEqual((result["model_calls"], result["tool_calls"], result["tool_attempts"]), (1, 1, 1))
        self.assertNotIn("tools", requests[0])
        self.assertTrue(json.loads(requests[0]["messages"][-1]["content"])["hits"])

    def test_agent_can_use_search_feedback_to_read_another_file(self):
        requests = []
        def ask(request):
            requests.append(copy.deepcopy(request))
            if len(requests) == 1:
                return call("search_documents", {"query": "A17"}, 1)
            if len(requests) == 2:
                self.assertIn("QH-Z9", request["messages"][-1]["content"])
                return call("read_document", {"path": "quota.md"}, 2)
            self.assertIn("5 次", request["messages"][-1]["content"])
            return lab.c04.synthetic_final("synthetic final")
        result = lab.run("agent", "A17 额度", ask, reader, retriever, loop)
        self.assertEqual(result["status"], "completed")
        self.assertEqual((result["model_calls"], result["tool_attempts"]), (3, 2))
        self.assertEqual([len(r["messages"]) for r in requests], [2, 4, 6])

    def test_api_failure_is_not_automatically_retried(self):
        def ask(request):
            raise TimeoutError("synthetic timeout")
        result = lab.run("all", "q", ask, reader, retriever)
        self.assertEqual(result["status"], "model_error")
        self.assertEqual(result["model_calls"], 1)

    def test_invalid_and_forbidden_calls_do_not_read(self):
        class NoReader:
            def dispatch(self, *args):
                raise AssertionError("rejected call reached reader")
        for name, arguments, code in [("read_document", {"path": "../secret.md"}, "forbidden_path"),
                                      ("read_document", {"path": 3}, "invalid_arguments"),
                                      ("shell", {"command": "ignored"}, "unknown_tool")]:
            request = call(name, arguments, 1)["choices"][0]["message"]["tool_calls"][0]
            result = lab.dispatch(request, NoReader(), retriever, retriever.documents())
            self.assertEqual(json.loads(result["content"])["error"]["code"], code)

    def test_retry_consumes_shared_attempt_budget(self):
        if retry is None:
            self.skipTest("optional C09 retry module not supplied")
        attempts = []
        def execute(request):
            attempts.append(request)
            return lab.tool_message(request, {"ok": False, "error": {"code": "temporary_unavailable"}})
        number = 0
        def ask(request):
            nonlocal number
            number += 1
            return call("read_document", {"path": "limits.md"}, number)
        session = lab.Session(ask, execute, "q", "agent", {}, retry=retry)
        try:
            loop.run_loop(session, 4, 3)
        except lab.c04.RunFailure as exc:
            session.finish(exc.status, reason=exc.reason)
        self.assertEqual(session.record["status"], "max_tool_calls")
        self.assertEqual(len(attempts), 3)
        self.assertEqual(session.record["tool_calls"], 2)
        self.assertEqual(len([m for m in session.record["messages"] if m["role"] == "tool"]), 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module")
    for name in ("reader", "retriever", "loop"):
        parser.add_argument("--" + name + "-module", required=True)
    parser.add_argument("--retry-module")
    args = parser.parse_args()
    lab, reader, retriever, loop = map(load, (args.module, args.reader_module, args.retriever_module, args.loop_module))
    retry = load(args.retry_module) if args.retry_module else None
    with patch("urllib.request.urlopen", side_effect=AssertionError("network disabled in offline checks")):
        unittest.main(argv=[sys.argv[0]], verbosity=2)
