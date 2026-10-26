"""Offline checks for retrieval and provenance, not generated-answer quality."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab_support import load


class Checks(unittest.TestCase):
    def test_ranking_and_ties(self):
        docs = {"b.md": "# Same\n\nalpha beta\n", "a.md": "# Same\n\nalpha\n\nalpha beta\n"}
        before = copy.deepcopy(docs)
        hits = lab.search("alpha beta", docs, 2)
        self.assertEqual([(x["file"], x["start_line"], x["score"]) for x in hits], [("a.md", 5, 2), ("b.md", 3, 2)])
        self.assertEqual(docs, before)

    def test_zero_matches_and_no_fabricated_fallback(self):
        self.assertEqual(lab.search("不存在的词_xyz", {"a.md": "# Test\n\nalpha"}), [])

    def test_sources_exact(self):
        docs = lab.documents()
        hits = lab.search("T01 工具调用上限", docs, 5)
        self.assertTrue(hits)
        for hit in hits:
            lines = docs[hit["file"]].splitlines()
            self.assertEqual(hit["quote"], "\n".join(lines[hit["start_line"]-1:hit["end_line"]]))
        self.assertIn("limits.md", {x["file"] for x in lab.search("单次任务 工具调用", docs, 5)})

    def test_validation(self):
        for query in ("", " ", None, "a"*201):
            with self.assertRaises(ValueError):
                lab.search(query, {})
        for k in (0, 6, True, 1.5):
            with self.assertRaises(ValueError):
                lab.search("x", {}, k)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("python3 check_retrieval.py path/to/retrieval.local.py")
    lab = load(sys.argv[1])
    unittest.main(argv=[sys.argv[0]], verbosity=2)
