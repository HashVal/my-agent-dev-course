"""Check evidence completeness, changed files and synthetic-result labeling."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import digest, load


class Checks(unittest.TestCase):
    def test_empty_manifest_is_not_completion(self):
        self.assertEqual(lab.inspect(lab.template())["status"], "needs_work")

    def test_evidence_links_and_source_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = []
            for n in range(1, 11):
                for mode in ("all", "agent"):
                    path = root / f"E{n:02}-{mode}.json"
                    path.write_text(json.dumps({"status": "max_steps", "case": f"E{n:02}", "mode": mode,
                                                "source": "synthetic"}), encoding="utf-8")
                    rows.append({"case": f"E{n:02}", "mode": mode, "source": "synthetic", "verdict": "fail",
                                 "record": str(path), "record_sha256": digest(path)})
            report = root / "report.json"
            report.write_text(json.dumps({"rows": rows}), encoding="utf-8")
            m = lab.template()
            m.update(evaluation_report=str(report), failure_record=rows[0]["record"], artifacts=[str(report)])
            m["analysis"] = {key: "虚构机制检查，不能当作个人分析" for key in m["analysis"]}
            m["reproduction"] = {"commands": ["python3 audit.py"], "budget": "offline", "environment": "Python"}
            self.assertEqual(lab.inspect(m)["status"], "simulation_only")
            rows[0]["source"] = "model_api"
            report.write_text(json.dumps({"rows": rows}), encoding="utf-8")
            self.assertEqual(lab.inspect(m)["status"], "needs_work")
            rows[0]["source"] = "synthetic"
            rows.pop()
            report.write_text(json.dumps({"rows": rows}), encoding="utf-8")
            self.assertEqual(lab.inspect(m)["status"], "needs_work")
            Path(rows[0]["record"]).write_text('{"status":"max_steps","changed":true}', encoding="utf-8")
            self.assertTrue(any("changed" in p for p in lab.inspect(m)["problems"]))


if __name__ == "__main__":
    lab = load(Path(__file__).with_name("audit.py"))
    unittest.main(verbosity=2)
