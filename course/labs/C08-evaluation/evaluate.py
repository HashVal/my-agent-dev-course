"""Copy to evaluate.local.py; implement decide. Consumes logs, never calls a model."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import ROOT, digest, save, validate_answer

EXPECTATIONS = json.loads((ROOT / "course/evals/C08-expectations.json").read_text(encoding="utf-8"))


def decide(observation):
    """Return {'verdict': ..., 'category': ...}, applying the priority below.

    status != completed -> fail/runtime
    schema_ok is False -> fail/format
    citations_ok is False -> fail/citation
    answerability_ok is False -> fail/answerability
    semantic_review is None -> pending/semantic_review
    semantic_review is False -> fail/semantic
    otherwise -> pass/accepted

    These categories indicate the first blocking check, not necessarily the
    root cause. In particular, real quotes do not prove a correct inference.
    """
    raise NotImplementedError("请实现分层评分；未人工核查不能算通过")


def observe(record, expectation, review=None):
    observation = {"status": record["status"], "schema_ok": False,
                   "citations_ok": False, "answerability_ok": False,
                   "semantic_review": review["correct"] if review else None}
    if record["status"] != "completed":
        return observation
    try:
        answer = validate_answer(record["answer"])
    except (ValueError, TypeError):
        return observation
    observation["schema_ok"] = True
    docs = record["corpus"]
    citations = answer["citations"]
    observation["citations_ok"] = all(
        item["file"] in docs and item["quote"] in docs[item["file"]] for item in citations
    ) and set(expectation["required_files"]).issubset({c["file"] for c in citations})
    observation["answerability_ok"] = answer["answerable"] is expectation["answerable"]
    return observation


def read_review(path, record_path):
    if path is None:
        return None
    review = json.loads(Path(path).read_text(encoding="utf-8"))
    if (review.get("record_sha256") != digest(record_path) or type(review.get("correct")) is not bool
            or not isinstance(review.get("reason"), str) or not review["reason"].strip()):
        raise ValueError("review needs matching record_sha256, boolean correct and nonblank reason")
    return review


def evaluate(entries):
    """Paths are relative to the current working directory; expected root is repo."""
    expected = {e["id"]: e for e in EXPECTATIONS}
    rows, seen = [], set()
    for item in entries:
        key = item["case"], item["mode"]
        if key in seen or key[0] not in expected or key[1] not in ("all", "fixed", "agent"):
            raise ValueError("duplicate or unknown case/mode")
        seen.add(key)
        row = {"case": key[0], "mode": key[1], "source": "not_run"}
        if item.get("record") is None:
            row.update(verdict="not_run", category="missing_trial")
        else:
            record = json.loads(Path(item["record"]).read_text(encoding="utf-8"))
            if (record.get("case"), record.get("mode")) != key or record.get("source") not in ("model_api", "synthetic"):
                raise ValueError("record identity or source mismatch")
            review = read_review(item.get("review"), item["record"])
            observation = observe(record, expected[key[0]], review)
            row.update(decide(observation), source=record["source"], observation=observation,
                       record=item["record"], record_sha256=digest(item["record"]),
                       review=review, model_calls=record["model_calls"], tool_attempts=record["tool_attempts"],
                       elapsed_seconds=record["elapsed_seconds"], usage=record["usage"], cost=record["cost"])
        rows.append(row)
    planned = {(e["id"], mode) for e in EXPECTATIONS for mode in ("all", "agent")}
    if not planned.issubset(seen):
        raise ValueError("keep all twenty planned entries; use null for missing runs")
    if any(mode == "fixed" for _, mode in seen) and not {
        (e["id"], "fixed") for e in EXPECTATIONS
    }.issubset(seen):
        raise ValueError("fixed comparison also needs ten entries, including not-run cases")
    counts = Counter((r["mode"], r["source"], r["verdict"]) for r in rows)
    return {"source": "evaluation", "rows": rows,
            "counts": [{"mode": m, "source": s, "verdict": v, "count": n} for (m, s, v), n in sorted(counts.items())]}


def template():
    return [{"case": e["id"], "mode": mode, "record": None, "review": None}
            for e in EXPECTATIONS for mode in ("all", "agent")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if not args.manifest:
        print(json.dumps(template(), ensure_ascii=False, indent=2))
        return 0
    try:
        report = evaluate(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (NotImplementedError, ValueError, KeyError, OSError, TypeError) as exc:
        print("评测未完成：" + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(report["counts"], ensure_ascii=False, indent=2))
    print(save("C08", report))
    return 0  # Completed evaluation may legitimately contain failed trials.


if __name__ == "__main__":
    raise SystemExit(main())
