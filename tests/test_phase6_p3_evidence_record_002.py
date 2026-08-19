from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = REPO_ROOT / "evidence" / "P3_REAL_WORKLOAD_002_SCENE27_2026-08-19.md"


class P3EvidenceRecord002Tests(unittest.TestCase):
    def test_run002_evidence_preserves_cross_scene_blocker(self) -> None:
        text = EVIDENCE.read_text(encoding="utf-8")

        required = [
            "DEPENDENCY PRESENT: YES",
            "UPSTREAM CANDIDATE: STAGED",
            "DOWNSTREAM CONTEXT SOURCE: OLD CANONICAL",
            "CROSS-SCENE CANDIDATE COHERENCE: BLOCKED",
            "CANONICAL EFFECT: NOT APPLIED",
            "HUMAN APPROVAL: NOT REQUESTED",
            "GOAL DONE: NO",
            "NOT HUMAN DECISION / NOT CANON",
            "not authorized by this evidence record",
        ]
        for marker in required:
            self.assertIn(marker, text)

        self.assertNotIn("GOAL DONE: YES", text)
        self.assertNotIn("CROSS-SCENE CANDIDATE COHERENCE: PASS", text)


if __name__ == "__main__":
    unittest.main()
