from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = REPO_ROOT / "evidence" / "P3_BOUNDED_PROPOSAL_VIEW_2026-08-19.md"


class BoundedProposalEvidenceTests(unittest.TestCase):
    def test_evidence_preserves_scope_and_authority_boundaries(self) -> None:
        text = EVIDENCE.read_text(encoding="utf-8")
        required = [
            "IMPLEMENTATION CANDIDATE / TECHNICALLY OBSERVED / HUMAN ACCEPTANCE PENDING",
            "DOWNSTREAM_CONTEXT_SOURCE=BOUND_CANDIDATE",
            "staging globally outranks canon",
            "BOUNDED_NONCANONICAL",
            "PROPOSAL_NOT_CANON",
            "does not approve, merge, mutate or otherwise promote the candidate",
            "does **not** yet establish:",
            "Human acceptance of the implementation",
            "atomic/multi-artifact approval",
        ]
        for marker in required:
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
