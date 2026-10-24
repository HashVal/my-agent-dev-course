"""C02 scaffold: copy to structured.local.py and complete both exercises."""

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
    """练习：沿用全文输入，把 system_prompt 改成业务 JSON 输出要求。"""
    user_prompt = "Documents: " + documents + "\nQuestion: " + question
    # 写明 JSON、四个字段及其约定，并给出不含本题答案的格式示例。
    system_prompt = None
    if system_prompt is None:
        raise NotImplementedError("请填写要求 JSON 输出的 system_prompt")
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def validate_consistency(data):
    """练习：检查已通过字段检查的数据，违反组合规则时抛出 ValueError。

    answerable=True：answer 非空非纯空白，missing_information 为空。
    answerable=False：answer 为 None，missing_information 非空。
    通过时返回 None。
    """
    raise NotImplementedError("请完成 validate_consistency")


def validate_fields(data):
    """教师提供：检查对象、必需字段、类型和非空来源条目。"""
    if not isinstance(data, dict):
        raise ValueError("answer must be a JSON object")
    required = {"answerable", "answer", "citations", "missing_information"}
    missing = required - data.keys()
    if missing:
        raise ValueError("missing fields: " + ", ".join(sorted(missing)))
    if not isinstance(data["answerable"], bool):
        raise ValueError("answerable must be a boolean")
    if data["answer"] is not None and not isinstance(data["answer"], str):
        raise ValueError("answer must be a string or null")
    citations = data["citations"]
    if not isinstance(citations, list):
        raise ValueError("citations must be a list")
    if data["answerable"] and not citations:
        raise ValueError("citations must not be empty when answerable is True")
    for citation in citations:
        if not isinstance(citation, dict):
            raise ValueError("each citation must be an object")
        for key in ("file", "quote"):
            value = citation.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError("citation " + key + " must be a non-empty string")
    missing_info = data["missing_information"]
    if not isinstance(missing_info, list):
        raise ValueError("missing_information must be a list")
    if any(not isinstance(item, str) or not item.strip() for item in missing_info):
        raise ValueError("missing_information items must be non-empty strings")


def parse_answer(text):
    """教师提供：解析内容，再依次执行字段和跨字段检查。"""
    data = json.loads(text)
    validate_fields(data)
    validate_consistency(data)
    return data


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
        "response_format": {"type": "json_object"},
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
    output_dir = ROOT / ".local/C02-runs"
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
    try:
        parse_answer(answer)
    except json.JSONDecodeError:
        print("回答内容无法解析为 JSON；原始响应已保留", file=sys.stderr)
        return 2
    except ValueError as error:
        print("回答不满足数据约定：" + str(error), file=sys.stderr)
        return 2
    print("JSON 与字段约定检查通过；事实和引用仍需核查", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
