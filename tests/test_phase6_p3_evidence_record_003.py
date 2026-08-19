from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = REPO_ROOT / "evidence" / "P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md"


class P3EvidenceRecord003Tests(unittest.TestCase):
    def test_run003_evidence_preserves_proposal_and_authority_boundaries(self) -> None:
        text = EVIDENCE.read_text(encoding="utf-8")
        required = [
            "CROSS_SCENE_PROPOSAL_COHERENCE=OBSERVED_PASS",
            "CANONICAL_EFFECT=NOT_APPLIED",
            "HUMAN_APPROVAL=NOT_REQUESTED",
            "GOAL_DONE=NO",
            "FALSE SUCCESS: BLOCKED",
            "This is an AI proposal, not Human-accepted screenplay canon.",
            "Human acceptance of the SCN-012 rewrite proposal",
            "Human acceptance of the SCN-027 rewrite proposal",
            "atomic or multi-artifact approval",
            "No `approve --why` was executed in this run.",
        ]
        for marker in required:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
