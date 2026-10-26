"""Copy to compare.local.py; implement run_fixed. Preview by default."""

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import ANSWER_RULES, LABS, digest, load, save

c04 = load(LABS / "C04-agent-loop/loop.py")
retrieval_template = load(LABS / "C06-retrieval/retrieval.py")
TASKS = json.loads((Path(__file__).with_name("tasks.json")).read_text(encoding="utf-8"))
SEARCH_TOOL = {"type": "function", "function": {
    "name": "search_documents", "description": "Search the fixed course corpus for evidence. Returns at most 3 verbatim paragraphs with file and line locations; no match returns an empty list. Query may use terms learned from previous results.",
    "parameters": {"type": "object", "properties": {"query": {"type": "string"}},
                   "required": ["query"], "additionalProperties": False}}}


def initial_messages(question, mode, docs):
    content = "Question: " + question + "\nAvailable files: " + ", ".join(sorted(docs))
    if mode == "all":
        content += "\nDocuments:\n" + json.dumps(docs, ensure_ascii=False)
    return [{"role": "system", "content": ANSWER_RULES + "Request at most one tool per response."},
            {"role": "user", "content": content}]


def run_fixed(session, question):
    """Exercise: search once with question, then request one final answer.

    session.search(question) executes search_documents and appends its result.
    session.request() returns (kind, message); fixed mode advertises no tools.
    If kind == 'final', return session.finish('completed', message).
    Otherwise raise c04.RunFailure('protocol_error', 'unexpected tool request').
    Do not rewrite the query, add a retry, or inspect an expected answer.
    """
    raise NotImplementedError("请连接固定的一次检索与一次回答")


def tool_message(call, body):
    return {"role": "tool", "tool_call_id": call["id"], "content": json.dumps(body, ensure_ascii=False)}


def dispatch(call, reader, retriever, docs):
    try:
        args = json.loads(call["function"]["arguments"])
        name = call["function"]["name"]
        if name == "search_documents":
            if not isinstance(args, dict) or set(args) != {"query"}:
                raise ValueError("invalid arguments")
            return tool_message(call, {"ok": True, "hits": retriever.search(args["query"], docs, 3)})
        if name == "read_document":
            if not isinstance(args, dict) or set(args) != {"path"} or not isinstance(args["path"], str):
                raise ValueError("invalid arguments")
            if args["path"] not in docs:
                return tool_message(call, {"ok": False, "error": {"code": "forbidden_path"}})
            root = LABS / "C01-materials" if args["path"] in retrieval_template.NAMES[:3] else retrieval_template.MATERIALS
            return reader.dispatch(call, root)
        return tool_message(call, {"ok": False, "error": {"code": "unknown_tool"}})
    except (ValueError, TypeError, KeyError):
        return tool_message(call, {"ok": False, "error": {"code": "invalid_arguments"}})


class Session(c04.Session):
    """Reuse C04 history/protocol; add retrieval, optional projection and metrics."""
    def __init__(self, ask, execute, question, mode, docs, projector=None, retry=None):
        super().__init__(ask, execute)
        self.mode, self.projector, self.retry = mode, projector, retry
        self.record["messages"] = initial_messages(question, mode, docs)
        self.record.update(tool_attempts=0, usage=[])

    def request(self):
        if self.record["model_calls"] >= 4:
            raise c04.RunFailure("max_steps", "hard request cap")
        messages = copy.deepcopy(self.record["messages"])
        if self.projector:
            messages = self.projector.project_messages(messages, 120)
        request = c04.build_request(messages)
        request["temperature"] = 0
        if self.mode == "agent":
            request["tools"] += [copy.deepcopy(SEARCH_TOOL)]
        else:
            request.pop("tools", None)
            request.pop("tool_choice", None)
        self.record["model_calls"] += 1
        self.emit("model_request", request=request)
        try:
            response = self.ask_model(copy.deepcopy(request))
        except (OSError, ValueError) as exc:
            self.emit("model_exception", error_type=type(exc).__name__)
            raise c04.RunFailure("model_error", type(exc).__name__) from exc
        self.emit("model_response", response=response)
        self.record["usage"].append(response.get("usage") if isinstance(response, dict) else None)
        return c04.parse_response(response)

    def execute(self, message):
        if self.record["tool_calls"] >= 3:
            raise c04.RunFailure("max_tool_calls", "hard dispatch cap")
        if self.record["tool_attempts"] >= 3:
            raise c04.RunFailure("max_tool_calls", "physical tool attempt cap")
        original = self.execute_tool

        def attempt(call):
            if self.record["tool_attempts"] >= 3:
                raise c04.RunFailure("max_tool_calls", "physical tool attempt cap")
            self.record["tool_attempts"] += 1
            self.emit("tool_attempt", number=self.record["tool_attempts"], call=call)
            result = original(call)
            self.emit("tool_attempt_result", result=result)
            return result

        def execute(call):
            if self.retry:
                return self.retry.retry_tool(lambda: attempt(call),
                                             lambda: 3-self.record["tool_attempts"])
            return attempt(call)
        self.execute_tool = execute
        try:
            super().execute(message)
        finally:
            self.execute_tool = original

    def search(self, question):
        self.emit("workflow_action", decision_source="program", query=question)
        call = {"id": "fixed_search_1", "type": "function", "function": {
            "name": "search_documents", "arguments": json.dumps({"query": question}, ensure_ascii=False)}}
        self.execute({"role": "assistant", "content": None, "tool_calls": [call]})


def synthetic_model(question):
    """A wiring fixture. It does not solve arbitrary questions or model behavior."""
    def ask(request):
        if request.get("tools") and not any(m["role"] == "tool" for m in request["messages"]):
            response = c04.synthetic_call("limits.md", 1)
            return response
        return c04.synthetic_final(json.dumps({"answerable": False, "answer": None,
            "citations": [], "missing_information": ["模拟模型不判断题目，仅验证接线。"]}, ensure_ascii=False))
    return ask


def run(mode, question, ask, reader, retriever, loop=None, projector=None, retry=None):
    docs = retriever.documents()
    session = Session(ask, lambda call: dispatch(call, reader, retriever, docs),
                      question, mode, docs, projector, retry)
    started = time.perf_counter()
    try:
        if mode == "fixed":
            run_fixed(session, question)
        elif mode == "agent":
            if loop is None:
                raise ValueError("agent requires completed C04 module")
            loop.run_loop(session, 4, 3)
        elif mode == "all":
            kind, message = session.request()
            if kind != "final":
                raise c04.RunFailure("protocol_error", "unexpected tool request")
            session.finish("completed", message)
        else:
            raise ValueError("unknown mode")
    except c04.RunFailure as exc:
        session.finish(exc.status, reason=exc.reason)
    except NotImplementedError:
        session.finish("exercise_incomplete", reason="learner TODO remains")
    session.record["elapsed_seconds"] = time.perf_counter() - started
    return session.record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("all", "fixed", "agent"), default="fixed")
    parser.add_argument("--case", choices=[t["id"] for t in TASKS], default="E01")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--demo", action="store_true")
    action.add_argument("--send", action="store_true")
    for name in ("reader", "retriever", "loop", "projector", "retry"):
        parser.add_argument("--" + name + "-module", type=Path)
    args = parser.parse_args()
    task = next(t for t in TASKS if t["id"] == args.case)
    docs = retrieval_template.documents()
    if not (args.send or args.demo):
        print(json.dumps({"mode": args.mode, "task": task,
                          "initial_messages": initial_messages(task["question"], args.mode, docs),
                          "limits": {"model": 4, "dispatch": 3, "tool_attempts": 3}}, ensure_ascii=False, indent=2))
        return 0
    required = [] if args.mode == "all" else ["retriever"]
    if args.mode == "agent":
        required += ["reader", "loop"]
    for name in required:
        if not getattr(args, name + "_module"):
            parser.error("this mode requires --" + name + "-module")
    if args.send and not os.environ.get("DEEPSEEK_API_KEY"):
        parser.error("DEEPSEEK_API_KEY is not set")
    modules, hashes = {}, {"compare": digest(__file__),
                          "lab_support": digest(LABS / "lab_support.py"),
                          "c04_support": digest(LABS / "C04-agent-loop/loop.py"),
                          "c03_transport": digest(LABS / "C03-tool-calling/read_tool.py")}
    for name in ("reader", "retriever", "loop", "projector", "retry"):
        path = getattr(args, name + "_module")
        modules[name] = load(path) if path else None
        if path:
            hashes[name] = digest(path)
    record = run(args.mode, task["question"], c04.c03.send_once if args.send else synthetic_model(task["question"]),
                 modules["reader"], modules["retriever"] or retrieval_template,
                 modules["loop"], modules["projector"], modules["retry"])
    record.update(source="model_api" if args.send else "synthetic", case=args.case,
                  mode=args.mode, code_hashes=hashes, model=c04.c03.MODEL,
                  corpus=docs, cost=None, limits={"model": 4, "dispatch": 3, "tool_attempts": 3})
    print(json.dumps({k: record[k] for k in ("status", "answer", "model_calls", "tool_calls", "tool_attempts")}, ensure_ascii=False, indent=2))
    print(save("C07", record))
    return 0 if record["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
