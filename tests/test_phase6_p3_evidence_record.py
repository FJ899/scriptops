from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = REPO_ROOT / "evidence" / "P3_REAL_WORKLOAD_001_SCENE12_2026-08-19.md"


class P3EvidenceRecordTests(unittest.TestCase):
    def test_run001_evidence_preserves_false_success_boundary(self) -> None:
        text = EVIDENCE.read_text(encoding="utf-8")
        required = [
            "LOCAL REWRITE CANDIDATE: OBSERVED PASS",
            "ALL DOWNSTREAM DEPENDENCIES PRESERVED: NOT ESTABLISHED / INSUFFICIENT EVIDENCE",
            "GOAL DONE: NO",
            "NO CANONICAL APPROVAL",
            "HUMAN_APPROVAL=NOT_REQUESTED",
        ]
        for marker in required:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
