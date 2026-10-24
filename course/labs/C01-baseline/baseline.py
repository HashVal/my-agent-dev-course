"""C01 scaffold: copy to baseline.local.py and complete build_messages."""

import argparse
import json
import os
import platform
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
MATERIALS = ROOT / "course/labs/C01-materials"
ENDPOINT = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-flash"
QUESTIONS = {
    "E01": "一次任务最多允许执行多少次工具调用？",
    "E02": "根据现有记录，T01 是否已经达到工具调用上限？",
    "E03": "T01 目前花了多少钱？",
}


def read_documents():
    """Read only the three classroom documents, preserving their names."""
    return "\n\n".join(
        f"<document name='{name}'>\n"
        f"{(MATERIALS / name).read_text(encoding='utf-8')}\n</document>"
        for name in ("rules.md", "limits.md", "trace.md")
    )


def build_messages(question, documents):
    """练习：返回两个含 role/content 的字典，组成一个列表。

    system：写出依据资料回答、引用来源、资料不足时的处理要求。
    user：包含 documents 的实际文本与 question，标清资料和问题。
    不要加入验收集中的预期答案。完成后删除下面的异常。
    """
    raise NotImplementedError("请在 baseline.local.py 中完成 build_messages")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=QUESTIONS, default="E01")
    parser.add_argument("--send", action="store_true", help="发送一次真实 API 请求")
    args = parser.parse_args()

    messages = build_messages(QUESTIONS[args.case], read_documents())
    if (
        not isinstance(messages, list)
        or len(messages) != 2
        or any(not isinstance(message, dict) for message in messages)
        or [message.get("role") for message in messages] != ["system", "user"]
        or any(not isinstance(message.get("content"), str) for message in messages)
        or any(not message["content"].strip() for message in messages)
    ):
        raise ValueError("本练习需返回 system、user 两条消息，content 为非空字符串")

    payload = {
        "model": MODEL,
        "messages": messages,
        "thinking": {"type": "disabled"},
        "stream": False,
        "max_tokens": 512,
    }
    if not args.send:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("当前进程未设置 DEEPSEEK_API_KEY；请在运行终端设置，不写进源码")

    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    started_at = datetime.now(timezone.utc)
    started = time.perf_counter()
    # One request, no application-level retry; timeout applies to socket operations.
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"API 返回 HTTP {error.code}；未自动重试") from None
    except (urllib.error.URLError, TimeoutError):
        raise SystemExit("网络或等待响应失败；未自动重试，服务端是否完成未知") from None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise SystemExit("响应无法解析为 JSON；未自动重试") from None

    record = {
        "started_at_utc": started_at.isoformat(),
        "python_version": platform.python_version(),
        "case": args.case,
        "endpoint": ENDPOINT,
        "request_body": payload,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "response": result,
        "cost": None,
    }
    output_dir = ROOT / ".local/C01-runs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{started_at:%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}.json"
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"请求与响应已保存：{output}", file=sys.stderr)

    try:
        choice = result["choices"][0]
        answer = choice["message"]["content"]
        finish_reason = choice["finish_reason"]
    except (KeyError, IndexError, TypeError):
        raise SystemExit("响应缺少预期字段，请检查本地响应记录") from None
    print(answer)
    print(f"finish_reason: {finish_reason}", file=sys.stderr)
    print("usage: " + json.dumps(result.get("usage"), ensure_ascii=False), file=sys.stderr)
    if finish_reason != "stop" or not isinstance(answer, str) or not answer.strip():
        print("未得到正常结束的非空回答，不能据此判定用例通过", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
