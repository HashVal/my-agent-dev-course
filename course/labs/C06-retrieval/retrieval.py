"""Copy to retrieval.local.py; implement search. No model call in this lab."""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import LABS, save, positive_int

MATERIALS = Path(__file__).resolve().parent / "materials"
NAMES = ("limits.md", "trace.md", "rules.md", "t02.md", "routing.md", "quota.md")


def documents():
    """Fixed public fixture allowlist: never scan evals, .local or arbitrary roots."""
    result = {}
    for name in NAMES:
        folder = LABS / "C01-materials" if name in NAMES[:3] else MATERIALS
        path = folder / name
        if path.is_symlink():
            raise ValueError("fixture must not be a symlink")
        raw = path.read_bytes()
        if len(raw) > 4096:
            raise ValueError("fixture too large")
        result[name] = raw.decode("utf-8")
    return result


def terms(text):
    """Deterministic lexical baseline, not a semantic embedding/tokenizer."""
    words = re.findall(r"[a-z0-9_-]+", text.lower())
    for part in re.findall(r"[\u4e00-\u9fff]+", text):
        words.extend(part[n:n+2] for n in range(len(part)-1))
    return set(words)


def chunks(docs):
    """One nonempty non-heading paragraph per chunk, verbatim with 1-based lines."""
    result = []
    for name, text in sorted(docs.items()):
        lines = text.splitlines()
        title = next((line.lstrip("# ") for line in lines if line.startswith("#")), name)
        start = None
        for i, line in enumerate(lines + [""]):
            boundary = not line.strip() or line.startswith("#") or line.startswith(">")
            if boundary and start is not None:
                result.append({"file": name, "title": title, "start_line": start+1,
                               "end_line": i, "quote": "\n".join(lines[start:i])})
                start = None
            if not boundary and start is None:
                start = i
    return result


def search(query, docs, top_k=3):
    """Return at most top_k chunks with score = count of shared unique terms.

    Use terms(query) and terms(chunk['title'] + ' ' + chunk['quote']).
    Keep positive scores only. Sort by (-score, file, start_line), then slice.
    Return chunk fields plus score; preserve exact quote and source positions.
    Validate query as nonblank string of <=200 chars and top_k as int 1..5
    (reject bool). Invalid inputs raise ValueError. No match returns [].
    Inputs must remain unchanged. Do not use eval expectations for ranking.
    """
    raise NotImplementedError("请实现关键词打分、稳定排序和 top_k 截取")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="T01 工具调用上限")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--search", action="store_true")
    args = parser.parse_args()
    docs = documents()
    if not args.search:
        print(json.dumps({"query": args.query, "chunks": chunks(docs)}, ensure_ascii=False, indent=2))
        return 0
    try:
        hits = search(args.query, docs, args.top_k)
    except (NotImplementedError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    record = {"source": "deterministic_retrieval", "query": args.query, "top_k": args.top_k, "hits": hits}
    print(json.dumps(record, ensure_ascii=False, indent=2))
    print(save("C06", record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
