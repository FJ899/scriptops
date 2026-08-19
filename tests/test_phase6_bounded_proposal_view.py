from __future__ import annotations

import sys
import unittest
from pathlib import Path

import yaml

import test_phase6_p3_real_workload_002 as run002

REPO_ROOT = Path(__file__).resolve().parents[1]
HARDENED = REPO_ROOT / "phase6" / "scriptops-v2-hardening.py"
BOUNDED = REPO_ROOT / "phase6" / "bounded-proposal-view.py"

DOWNSTREAM_OBJECTIVE = (
    "Dostosować wszystkie zależności SCN-027 do beznośnikowego przekazania danych z SCN-012, "
    "zachowując utratę kopii Anny i wyłączną kontrolę Adama nad pozostałym źródłem lub dostępem."
)


class BoundedProposalViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = run002.P3RealWorkload002Tests(
            methodName="test_downstream_context_reads_old_canon_not_staged_upstream_candidate"
        )
        self.fixture.setUp()
        self.root = self.fixture.root
        self.env = self.fixture.env

    def tearDown(self) -> None:
        self.fixture.tearDown()

    def _prepare_bound_downstream_task(self) -> tuple[str, Path]:
        self.fixture._stage_scene_12_candidate()
        staged = self.root / "staging" / "scenes" / "SCN-012-v2-candidate.fountain"
        self.assertTrue(staged.exists())

        downstream_task = self.fixture._rewrite_task("SCN-027", DOWNSTREAM_OBJECTIVE)
        run002.run(
            [
                sys.executable,
                str(BOUNDED),
                "bind",
                "--task",
                downstream_task,
                "--scene",
                "SCN-012",
                "--candidate",
                "staging/scenes/SCN-012-v2-candidate.fountain",
            ],
            self.root,
            self.env,
        )
        return downstream_task, staged

    def test_exact_binding_builds_context_from_staged_upstream_proposal(self) -> None:
        downstream_task, staged = self._prepare_bound_downstream_task()

        task_path = self.root / "tasks" / downstream_task / "task-pack.yaml"
        task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
        binding = task["proposal_bindings"]["SCN-012"]
        self.assertEqual(binding["path"], "staging/scenes/SCN-012-v2-candidate.fountain")
        self.assertEqual(
            binding["file_sha256"],
            run002.compute_sha256(staged.read_text(encoding="utf-8")),
        )

        run002.run(
            [sys.executable, str(HARDENED), "check-pre", "--task", downstream_task],
            self.root,
            self.env,
        )
        run002.run(
            [
                sys.executable,
                str(BOUNDED),
                "context-build",
                "--scene",
                "SCN-027",
                "--mode",
                "rewrite-scene",
                "--task",
                downstream_task,
            ],
            self.root,
            self.env,
        )

        context_path = self.root / "tasks" / downstream_task / "context-pack.md"
        context_text = context_path.read_text(encoding="utf-8")
        header = yaml.safe_load(context_text.split("---", 2)[1])

        self.assertEqual(header["proposal_view"]["status"], "BOUNDED_NONCANONICAL")
        self.assertEqual(header["proposal_view"]["bindings"][0]["scene_id"], "SCN-012")
        self.assertEqual(
            header["proposal_view"]["bindings"][0]["semantic_status"],
            "PROPOSAL_NOT_CANON",
        )
        self.assertIn("# BOUNDED PROPOSAL VIEW", context_text)
        self.assertIn("jednorazowy link", context_text.lower())
        self.assertIn("źródłowy pakiet zostaje w zaszyfrowanym magazynie", context_text.lower())
        self.assertNotIn("oryginał schowamy w sejfie", context_text.lower())

        canonical_12 = self.root / "scenes" / "SCN-012.fountain"
        canonical_27 = self.root / "scenes" / "SCN-027.fountain"
        self.assertEqual(canonical_12.read_text(encoding="utf-8"), self.fixture.scene_12_canonical)
        self.assertEqual(canonical_27.read_text(encoding="utf-8"), self.fixture.scene_27_canonical)
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

        print(
            "BOUNDED_PROPOSAL_VIEW: EXPLICIT_BINDING=PASS; DOWNSTREAM_CONTEXT_SOURCE=BOUND_CANDIDATE; "
            "UNBOUND_GLOBAL_PRECEDENCE=NO; CANONICAL_EFFECT=NOT_APPLIED; ATOMIC_APPROVAL=NOT_ADDED"
        )

    def test_binding_fails_closed_if_candidate_identity_drifts(self) -> None:
        downstream_task, staged = self._prepare_bound_downstream_task()

        staged.write_text(staged.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        run002.git(self.root, self.env, "add", str(staged.relative_to(self.root)))
        run002.git(self.root, self.env, "commit", "-m", "fixture: drift bound candidate after binding")

        result = run002.run(
            [
                sys.executable,
                str(BOUNDED),
                "context-build",
                "--scene",
                "SCN-027",
                "--mode",
                "rewrite-scene",
                "--task",
                downstream_task,
            ],
            self.root,
            self.env,
            ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("proposal binding sha mismatch", result.stderr.lower())
        self.assertFalse((self.root / "tasks" / downstream_task / "context-pack.md").exists())
        self.assertEqual(
            (self.root / "scenes" / "SCN-012.fountain").read_text(encoding="utf-8"),
            self.fixture.scene_12_canonical,
        )
        self.assertEqual(
            (self.root / "scenes" / "SCN-027.fountain").read_text(encoding="utf-8"),
            self.fixture.scene_27_canonical,
        )

    def test_bounded_context_requires_explicit_binding(self) -> None:
        self.fixture._stage_scene_12_candidate()
        downstream_task = self.fixture._rewrite_task("SCN-027", DOWNSTREAM_OBJECTIVE)

        result = run002.run(
            [
                sys.executable,
                str(BOUNDED),
                "context-build",
                "--scene",
                "SCN-027",
                "--mode",
                "rewrite-scene",
                "--task",
                downstream_task,
            ],
            self.root,
            self.env,
            ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires at least one explicit proposal binding", result.stderr.lower())
        self.assertFalse((self.root / "tasks" / downstream_task / "context-pack.md").exists())


if __name__ == "__main__":
    unittest.main()
