"""Teacher evidence auditor. Learner exercise: fill the emitted local manifest."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import digest, save


def template():
    return {"evaluation_report": None, "failure_record": None, "failure_review": None,
            "analysis": {key: "" for key in ("observed", "cause_evidence", "hypothesis", "change",
                                               "verification", "remaining_limit")},
            "reproduction": {"commands": [], "budget": "", "environment": ""},
            "artifacts": []}


def inspect(manifest):
    """Check completeness/integrity only; a teacher still assesses explanations."""
    problems = []
    sources = set()
    analysis = manifest.get("analysis", {})
    for key in template()["analysis"]:
        if not isinstance(analysis.get(key), str) or not analysis[key].strip():
            problems.append("analysis." + key)
    reproduction = manifest.get("reproduction", {})
    commands = reproduction.get("commands")
    if not isinstance(commands, list) or not commands or any(not isinstance(c, str) or not c.strip() for c in commands):
        problems.append("reproduction.commands")
    for key in ("budget", "environment"):
        if not isinstance(reproduction.get(key), str) or not reproduction[key].strip():
            problems.append("reproduction." + key)
    fingerprints = {}
    if not manifest.get("artifacts"):
        problems.append("artifacts")
    for path in manifest.get("artifacts", []):
        if not Path(path).is_file():
            problems.append("missing artifact: " + path)
        else:
            fingerprints[path] = digest(path)
    report_path = manifest.get("evaluation_report")
    if not report_path or not Path(report_path).is_file():
        problems.append("evaluation_report")
    else:
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        expected = {(f"E{n:02}", mode) for n in range(1, 11) for mode in ("all", "agent")}
        rows = report.get("rows", [])
        keys = [(r["case"], r["mode"]) for r in rows]
        if len(set(keys)) != len(keys) or not expected.issubset(set(keys)):
            problems.append("need ten distinct cases for each of all and agent")
        for row in rows:
            if row["verdict"] not in ("pass", "fail"):
                problems.append("unreviewed or missing trial: " + row["case"] + "/" + row["mode"])
            if row.get("source") not in ("model_api", "synthetic"):
                problems.append("invalid trial source")
            sources.add(row.get("source"))
            path = row.get("record")
            if not path or not Path(path).is_file() or digest(path) != row.get("record_sha256"):
                problems.append("trial missing or changed: " + row["case"] + "/" + row["mode"])
            else:
                trial = json.loads(Path(path).read_text(encoding="utf-8"))
                if (trial.get("case"), trial.get("mode"), trial.get("source")) != (row["case"], row["mode"], row["source"]):
                    problems.append("trial identity mismatch")
                if row["verdict"] == "pass":
                    review = row.get("review")
                    if (trial.get("status") != "completed" or not isinstance(review, dict)
                            or review.get("correct") is not True
                            or review.get("record_sha256") != digest(path)
                            or not isinstance(review.get("reason"), str) or not review["reason"].strip()):
                        problems.append("passing trial lacks matching semantic review")
        fingerprints[report_path] = digest(report_path)
    failure_path = manifest.get("failure_record")
    if not failure_path or not Path(failure_path).is_file():
        problems.append("failure_record")
    else:
        failure = json.loads(Path(failure_path).read_text(encoding="utf-8"))
        review = manifest.get("failure_review")
        if failure.get("status") == "completed":
            if (not isinstance(review, dict) or review.get("correct") is not False
                    or review.get("record_sha256") != digest(failure_path)
                    or not isinstance(review.get("reason"), str) or not review["reason"].strip()):
                problems.append("completed failure needs a matching negative semantic review")
        elif failure.get("status") not in ("max_steps", "max_tool_calls", "model_error", "protocol_error", "tool_exception"):
            problems.append("failure_record must be a C07 failed run or reviewed wrong answer")
        fingerprints[failure_path] = digest(failure_path)
    if len(sources) > 1:
        problems.append("separate synthetic and model_api evaluations")
    status = "needs_work" if problems else ("simulation_only" if sources == {"synthetic"} else "evidence_complete")
    return {"source": "evidence_audit", "status": status, "problems": problems,
            "fingerprints": fingerprints, "teaching_acceptance": "pending_explanation_and_reproduction"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    if not args.manifest:
        print(json.dumps(template(), ensure_ascii=False, indent=2))
        return 0
    try:
        result = inspect(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError, OSError):
        print("交接记录无效；检查路径与 JSON 结构。", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(save("C10", result))
    return 2 if result["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
