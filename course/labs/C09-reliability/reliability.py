"""Copy to reliability.local.py; implement should_retry. Offline by default."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import save


def should_retry(code, attempts, remaining):
    """Return bool. Retry only temporary_unavailable, after the first attempt,
    when a physical-tool attempt remains (remaining > 0).
    attempts includes the initial attempt; at most 2 attempts for this call.
    Unknown codes, forbidden_path, invalid_arguments, not_found are terminal.
    This policy covers the read-only local tool, not model API or writes.
    """
    raise NotImplementedError("请实现错误分类与有界重试判定")


def retry_tool(operation, remaining):
    """Teacher executor: physical attempts are counted by operation's caller.

    Return one final tool message with the original call ID. Intermediate
    attempts belong in the caller's trace, not as duplicate tool messages.
    Unexpected exceptions propagate. No HTTP retry or sleep in this exercise.
    """
    attempts = 0
    while remaining() > 0:
        message = operation()
        attempts += 1
        body = json.loads(message["content"])
        if body.get("ok") is True:
            return message
        code = body.get("error", {}).get("code")
        if attempts >= 2 or not should_retry(code, attempts, remaining()):
            return message
    raise ValueError("no tool attempt budget before execution")


def demo(codes):
    events = []
    def remaining(): return 3-len(events)
    def operation():
        code = codes[min(len(events), len(codes)-1)]
        body = {"ok": True, "content": "虚构资料"} if code is None else {"ok": False, "error": {"code": code}}
        events.append({"attempt": len(events)+1, "body": body})
        return {"role": "tool", "tool_call_id": "retry_demo", "content": json.dumps(body, ensure_ascii=False)}
    result = retry_tool(operation, remaining)
    return {"source": "synthetic", "events": events, "final_message": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", choices=("recover", "exhaust", "forbidden"))
    args = parser.parse_args()
    if not args.demo:
        print("预览：recover=暂时失败后成功；exhaust=连续暂时失败；forbidden=权限拒绝。均为离线输入。")
        return 0
    codes = {"recover": ["temporary_unavailable", None],
             "exhaust": ["temporary_unavailable"], "forbidden": ["forbidden_path"]}[args.demo]
    try:
        record = demo(codes)
    except NotImplementedError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(save("C09", record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
