"""Copy to context.local.py; implement trim_result. Default: offline preview."""

import argparse
import copy
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import LABS, load, save

MARKER = "\n[内容已裁剪]\n"


def trim_result(body, max_chars):
    """Return a deep copy; never change the stored tool result.

    Precondition: body is a C03 result; max_chars is a positive integer.
    For ok=true and content longer than max_chars, keep the first
    max_chars//2 characters and the last max_chars-max_chars//2 characters,
    separated by MARKER. Set truncated=true and original_chars=len(content).
    The marker is extra, not included in max_chars. Preserve file and all
    other fields. Short results and ok=false results are unchanged copies.
    This is a character limit, NOT a token or total-context limit.
    """
    raise NotImplementedError("请实现工具正文的首尾裁剪与显式标记")


def project_messages(messages, max_chars):
    """Teacher helper: preserve protocol, change only copied tool content."""
    if type(max_chars) is not int or max_chars < 1:
        raise ValueError("max_chars must be a positive integer")
    projected = copy.deepcopy(messages)
    for message in projected:
        if message["role"] == "tool":
            body = json.loads(message["content"])
            if body.get("ok") is True and isinstance(body.get("content"), str):
                message["content"] = json.dumps(trim_result(body, max_chars), ensure_ascii=False)
    return projected


def fixture():
    # Fictional evidence is deliberately in the middle. This is not model output.
    text = "例行记录。" * 80 + "\n恢复编号为 QH-742。\n" + "例行记录。" * 80
    return [
        {"role": "system", "content": "根据资料回答，引用文件与原文。"},
        {"role": "user", "content": "恢复编号是什么？"},
        {"role": "assistant", "content": None, "tool_calls": [{
            "id": "c05_1", "type": "function", "function": {
                "name": "read_document", "arguments": '{"path":"recovery.md"}'}}]},
        {"role": "tool", "tool_call_id": "c05_1", "content": json.dumps({
            "ok": True, "file": "recovery.md", "content": text}, ensure_ascii=False)},
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--send-pair", action="store_true", help="显式发送完整与裁剪输入各一次")
    parser.add_argument("--max-chars", type=int, default=120)
    args = parser.parse_args()
    messages = fixture()
    if not (args.demo or args.send_pair):
        print(json.dumps({"source": "synthetic", "messages": messages}, ensure_ascii=False, indent=2))
        return 0
    try:
        projected = project_messages(messages, args.max_chars)
    except (NotImplementedError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    original = json.dumps(messages, ensure_ascii=False)
    selected = json.dumps(projected, ensure_ascii=False)
    record = {"source": "model_api" if args.send_pair else "synthetic", "full_messages": messages, "projected_messages": projected,
              "full_json_chars": len(original), "projected_json_chars": len(selected),
              "evidence_retained": "QH-742" in selected, "token_usage": None,
              "model_answer": None, "state": {"model_calls": 1, "tool_calls": 1}}
    if args.send_pair:
        if not os.environ.get("DEEPSEEK_API_KEY"):
            parser.error("DEEPSEEK_API_KEY is not set")
        c04 = load(LABS / "C04-agent-loop/loop.py")
        record["trials"] = []
        for label, history in (("full", messages), ("trimmed", projected)):
            request = c04.build_request(history)
            request.pop("tools", None)
            request.pop("tool_choice", None)
            request["temperature"] = 0
            trial = {"label": label, "request": request}
            record["trials"].append(trial)
            try:
                response = c04.c03.send_once(request)
                trial["response"] = response
                kind, answer = c04.parse_response(response)
                trial["status"] = "completed" if kind == "final" else "protocol_error"
                trial["answer"] = answer.get("content")
            except (OSError, ValueError, c04.RunFailure) as exc:
                trial["status"] = "error"
                trial["error_type"] = type(exc).__name__
                print(save("C05", record))
                return 2
    print(json.dumps({k: v for k, v in record.items() if "messages" not in k}, ensure_ascii=False, indent=2))
    print(save("C05", record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
