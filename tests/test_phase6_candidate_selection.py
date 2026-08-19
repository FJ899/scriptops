from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HARDENED = REPO_ROOT / "phase6" / "scriptops-v2-hardening.py"

spec = importlib.util.spec_from_file_location("scriptops_phase6_hardening", HARDENED)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load Phase 6 hardening module")
phase6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase6)


class CandidateSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "staging" / "scenes").mkdir(parents=True)
        self.original_root = phase6.ROOT
        phase6.ROOT = self.root

    def tearDown(self) -> None:
        phase6.ROOT = self.original_root
        self.tmp.cleanup()

    def _candidate(self, version: int) -> Path:
        path = self.root / "staging" / "scenes" / f"SCN-001-v{version}-candidate.fountain"
        path.write_text(f"version {version}\n", encoding="utf-8")
        return path

    def test_numeric_version_chooses_v10_over_v9(self) -> None:
        self._candidate(9)
        expected = self._candidate(10)
        self.assertEqual(phase6._latest_candidate("SCN-001"), expected)

    def test_symlink_candidate_is_not_eligible(self) -> None:
        target = self.root / "outside.fountain"
        target.write_text("outside\n", encoding="utf-8")
        symlink = self.root / "staging" / "scenes" / "SCN-001-v99-candidate.fountain"
        symlink.symlink_to(target)
        with self.assertRaises(phase6.Phase6Error):
            phase6._latest_candidate("SCN-001")

    def test_unparseable_version_is_ignored(self) -> None:
        bad = self.root / "staging" / "scenes" / "SCN-001-vx-candidate.fountain"
        bad.write_text("bad\n", encoding="utf-8")
        expected = self._candidate(2)
        self.assertEqual(phase6._latest_candidate("SCN-001"), expected)


if __name__ == "__main__":
    unittest.main()
