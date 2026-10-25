"""Offline checks: python3 check_loop.py path/to/loop.local.py.

All model responses and tool outputs here are synthetic. A complete loop is
required; the public scaffold intentionally leaves run_loop unimplemented.
"""

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


class LoopChecks(unittest.TestCase):
    def setUp(self):
        self.requests, self.calls = [], []

    def tool(self, call, ok=True, **fields):
        self.calls.append(copy.deepcopy(call))
        if len(self.calls) > 6:
            raise AssertionError("unexpected extra tool execution")
        body = {"ok": ok, **fields}
        if not ok:
            body["error"] = {"code": "not_found", "message": "Synthetic missing file"}
        return {"role": "tool", "tool_call_id": call["id"], "content": json.dumps(body)}

    def script(self, responses):
        def ask(request):
            self.requests.append(copy.deepcopy(request))
            index = len(self.requests) - 1
            if index >= len(responses):
                raise AssertionError("unexpected extra model request")
            response = responses[index]
            if isinstance(response, Exception):
                raise response
            return copy.deepcopy(response)
        return ask

    def repeating(self):
        return self.script([lab.synthetic_call("limits.md", n) for n in range(6)])

    def assert_counts(self, result, model, tool, status):
        self.assertEqual(result["status"], status)
        self.assertEqual(result["model_calls"], model)
        self.assertEqual(result["tool_calls"], tool)
        self.assertEqual(len(self.requests), model)
        self.assertEqual(len(self.calls), tool)
        self.assertEqual(result["trace"][-1]["event"], "stop")
        self.assertEqual(result["trace"][-1]["status"], status)
        if status != "completed":
            self.assertIsNone(result["answer"])

    def test_two_reads_then_answer_preserves_history(self):
        responses = [lab.synthetic_call("trace.md", 1), lab.synthetic_call("limits.md", 2), lab.synthetic_final("done")]
        result = lab.run(self.script(responses), self.tool)
        self.assert_counts(result, 3, 2, "completed")
        self.assertEqual(result["answer"], "done")
        self.assertEqual([m["role"] for m in result["messages"]], ["system", "user", "assistant", "tool", "assistant", "tool", "assistant"])
        self.assertEqual([len(r["messages"]) for r in self.requests], [2, 4, 6])
        for request in self.requests[1:]:
            self.assertEqual(request["messages"][-1]["tool_call_id"], request["messages"][-2]["tool_calls"][0]["id"])
        saved = [event["request"] for event in result["trace"] if event["event"] == "model_request"]
        self.assertEqual(saved, self.requests)

    def test_zero_steps_never_requests(self):
        result = lab.run(self.script([]), self.tool, max_steps=0)
        self.assert_counts(result, 0, 0, "max_steps")

    def test_repeated_calls_stop_at_model_step_limit(self):
        result = lab.run(self.repeating(), self.tool, max_steps=2, max_tool_calls=3)
        self.assert_counts(result, 2, 2, "max_steps")
        self.assertEqual(result["messages"][-1]["role"], "tool")

    def test_tool_limit_refuses_next_dispatch(self):
        result = lab.run(self.repeating(), self.tool, max_steps=4, max_tool_calls=1)
        self.assert_counts(result, 2, 1, "max_tool_calls")
        self.assertEqual(len(result["messages"]), 4)
        responses = [e for e in result["trace"] if e["event"] == "model_response"]
        self.assertEqual(len(responses), 2)  # Blocked request is still diagnosable.

    def test_zero_tools_can_still_answer(self):
        result = lab.run(self.script([lab.synthetic_final("done")]), self.tool, max_tool_calls=0)
        self.assert_counts(result, 1, 0, "completed")

    def test_zero_tools_refuses_a_requested_call(self):
        result = lab.run(self.repeating(), self.tool, max_tool_calls=0)
        self.assert_counts(result, 1, 0, "max_tool_calls")

    def test_answer_on_last_step_after_tool_budget_exhausted(self):
        responses = [lab.synthetic_call("trace.md", 1), lab.synthetic_final("done")]
        result = lab.run(self.script(responses), self.tool, max_steps=2, max_tool_calls=1)
        self.assert_counts(result, 2, 1, "completed")

    def test_last_step_tool_result_does_not_buy_an_extra_summary(self):
        result = lab.run(self.repeating(), self.tool, max_steps=1, max_tool_calls=1)
        self.assert_counts(result, 1, 1, "max_steps")

    def test_failed_dispatch_is_feedback_and_consumes_budget(self):
        responses = [lab.synthetic_call("missing.md", 1), lab.synthetic_final("missing evidence")]
        result = lab.run(self.script(responses), lambda call: self.tool(call, ok=False))
        self.assert_counts(result, 2, 1, "completed")
        feedback = json.loads(self.requests[1]["messages"][-1]["content"])
        self.assertIs(feedback["ok"], False)
        self.assertEqual(feedback["error"]["code"], "not_found")

    def test_repeated_failed_dispatches_also_reach_limit(self):
        result = lab.run(self.repeating(), lambda call: self.tool(call, ok=False), max_tool_calls=1)
        self.assert_counts(result, 2, 1, "max_tool_calls")

    def test_feedback_reaches_model_and_changes_next_requested_path(self):
        for target in ("limits.md", "rules.md"):
            with self.subTest(target=target):
                self.requests, self.calls = [], []
                def ask(request):
                    self.requests.append(copy.deepcopy(request))
                    feedback = [m for m in request["messages"] if m["role"] == "tool"]
                    if not feedback:
                        return lab.synthetic_call("trace.md", 1)
                    if len(feedback) == 1:
                        return lab.synthetic_call(json.loads(feedback[0]["content"])["next_path"], 2)
                    if len(self.requests) > 3:
                        raise AssertionError("unexpected extra request")
                    return lab.synthetic_final("done")
                result = lab.run(ask, lambda call: self.tool(call, next_path=target))
                self.assert_counts(result, 3, 2, "completed")
                paths = [json.loads(c["function"]["arguments"])["path"] for c in self.calls]
                self.assertEqual(paths, ["trace.md", target])

    def test_malformed_responses_stop_before_execution(self):
        batch = lab.synthetic_call("limits.md", 1)
        batch["choices"][0]["message"]["tool_calls"].append(lab.synthetic_call("trace.md", 2)["choices"][0]["message"]["tool_calls"][0])
        choices = lab.synthetic_call("limits.md", 1)
        choices["choices"].append(copy.deepcopy(choices["choices"][0]))
        truncated = lab.synthetic_final('{"unfinished":')
        truncated["choices"][0]["finish_reason"] = "length"
        inconsistent = lab.synthetic_call("limits.md", 1)
        inconsistent["choices"][0]["finish_reason"] = "stop"
        missing_id = lab.synthetic_call("limits.md", 1)
        del missing_id["choices"][0]["message"]["tool_calls"][0]["id"]
        for response in (batch, choices, truncated, inconsistent, missing_id, lab.synthetic_final(" "), {}):
            with self.subTest(response=response):
                self.requests, self.calls = [], []
                result = lab.run(self.script([response]), self.tool)
                self.assert_counts(result, 1, 0, "protocol_error")
                self.assertEqual(result["trace"][1]["response"], response)

    def test_wrong_tool_result_id_stops_without_another_request(self):
        def execute(call):
            result = self.tool(call)
            result["tool_call_id"] = "wrong"
            return result
        result = lab.run(self.script([lab.synthetic_call("trace.md", 1)]), execute)
        self.assert_counts(result, 1, 1, "protocol_error")

    def test_reused_tool_id_is_not_dispatched_twice(self):
        result = lab.run(self.script([lab.synthetic_call("trace.md", 1)] * 2), self.tool)
        self.assert_counts(result, 2, 1, "protocol_error")

    def test_model_exception_is_counted_and_not_retried(self):
        result = lab.run(self.script([TimeoutError("synthetic")]), self.tool)
        self.assert_counts(result, 1, 0, "model_error")

    def test_tool_exception_stops_with_attempt_preserved(self):
        def execute(call):
            self.calls.append(call)
            raise OSError("synthetic")
        result = lab.run(self.script([lab.synthetic_call("trace.md", 1)]), execute)
        self.assert_counts(result, 1, 1, "tool_exception")

    def test_invalid_limits_fail_before_model_use(self):
        for value in (-1, True, 1.5):
            for key in ("max_steps", "max_tool_calls"):
                with self.subTest(value=value, key=key), self.assertRaises(ValueError):
                    lab.run(self.script([]), self.tool, **{key: value})
        self.assertEqual(self.requests, [])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 check_loop.py path/to/loop.local.py")
    spec = importlib.util.spec_from_file_location("learner_loop", Path(sys.argv[1]).resolve())
    lab = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lab)
    unittest.main(argv=[sys.argv[0]], verbosity=2)
