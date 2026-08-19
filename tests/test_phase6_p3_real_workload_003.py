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

SCENE_27_CANDIDATE_BODY = """
INT. MIESZKANIE ADAMA - NOC

Adam zamyka drzwi na dwa zamki i podchodzi do biurka.

Telefon wibruje.

ANNA
Masz jeszcze dostęp do źródła?

ADAM
Mam.

ANNA
Kopia z mojego laptopa zniknęła. Ktoś ją usunął.

Adam nie loguje się do magazynu. Odkłada telefon ekranem w dół.

ADAM
Czyli został tylko źródłowy pakiet w zaszyfrowanym magazynie, do którego mam dostęp.

Po drugiej stronie zapada cisza.

ANNA
Nie otwieraj go z żadnego komputera. I nikomu nie udostępniaj dostępu.

Adam blokuje telefon.

ADAM
Bez mojego udziału nikt tych danych nie dostanie.

Rozłącza się.
"""


class P3RealWorkload003Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = run002.P3RealWorkload002Tests(
            methodName="test_downstream_context_reads_old_canon_not_staged_upstream_candidate"
        )
        self.fixture.setUp()
        self.root = self.fixture.root
        self.env = self.fixture.env

    def tearDown(self) -> None:
        self.fixture.tearDown()

    def test_bounded_view_supports_coherent_two_scene_proposal_without_canonical_effect(self) -> None:
        upstream_task = self.fixture._stage_scene_12_candidate()
        staged_12 = self.root / "staging" / "scenes" / "SCN-012-v2-candidate.fountain"
        self.assertTrue(staged_12.exists())
        self.assertNotIn("pendrive", staged_12.read_text(encoding="utf-8").lower())

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
        self.assertIn("jednorazowy link", context_text.lower())
        self.assertIn("źródłowy pakiet zostaje w zaszyfrowanym magazynie", context_text.lower())
        self.assertNotIn("oryginał schowamy w sejfie", context_text.lower())

        canonical_27_text = (self.root / "scenes" / "SCN-027.fountain").read_text(encoding="utf-8")
        source_fm = yaml.safe_load(canonical_27_text.split("---", 2)[1])
        candidate_fm = {
            "scene_id": "SCN-027",
            "version": 2,
            "status": "candidate",
            "title": "Mieszkanie Adama / noc",
            "act": 2,
            "sequence": "",
            "location": "MIESZKANIE ADAMA",
            "time": "NOC",
            "characters": ["Adam", "Anna"],
            "purpose": [
                "Ujawnić utratę kopii Anny",
                "Potwierdzić, że Adam zachowuje jedyne pozostałe źródło lub kontrolę nad danymi",
            ],
            "emotional_turn": {"from": "niepokój", "to": "izolacja jedynego pozostałego źródła"},
            "depends_on": ["SCN-012"],
            "spoils_or_sets_up": [],
            "continuity_constraints": [
                "Kopia z laptopa Anny została usunięta.",
                "Adam nadal kontroluje jedyny pozostały zaszyfrowany pakiet lub dostęp do niego.",
                "Nie istnieje fizyczny nośnik danych do zachowania, podłączania ani przekazania.",
                "Dostęp do źródła nie może zostać udostępniony bez udziału Adama.",
            ],
            "tags": ["dowody", "Kowalski", "utrata-kopii"],
            "parent_hash": source_fm["hash"],
            "context_hash": run002.compute_sha256(context_text),
            "provenance": {
                "task_id": downstream_task,
                "mode": "rewrite-scene",
                "model": "chatgpt-evaluation-candidate",
                "timestamp": "2026-08-19T16:49:00+02:00",
            },
        }
        output = self.root / "tasks" / downstream_task / "webai-output.md"
        output.write_text(
            run002.scene_text(candidate_fm, SCENE_27_CANDIDATE_BODY, hash_sort_keys=True),
            encoding="utf-8",
        )
        run002.run(
            [sys.executable, str(HARDENED), "check-post", "--task", downstream_task],
            self.root,
            self.env,
        )

        staged_27 = self.root / "staging" / "scenes" / "SCN-027-v2-candidate.fountain"
        self.assertTrue(staged_27.exists())
        staged_27_text = staged_27.read_text(encoding="utf-8")
        self.assertNotIn("pendrive", staged_27_text.lower())
        self.assertIn("masz jeszcze dostęp do źródła", staged_27_text.lower())
        self.assertIn("kopia z mojego laptopa zniknęła", staged_27_text.lower())
        self.assertIn("źródłowy pakiet w zaszyfrowanym magazynie", staged_27_text.lower())
        self.assertIn("bez mojego udziału nikt tych danych nie dostanie", staged_27_text.lower())

        impact_12 = self.root / "tasks" / upstream_task / "impact-report.json"
        impact_27 = self.root / "tasks" / downstream_task / "impact-report.json"
        self.assertIn('"status": "REVIEW_REQUIRED"', impact_12.read_text(encoding="utf-8"))
        self.assertIn('"status": "REVIEW_REQUIRED"', impact_27.read_text(encoding="utf-8"))

        canonical_12 = self.root / "scenes" / "SCN-012.fountain"
        canonical_27 = self.root / "scenes" / "SCN-027.fountain"
        self.assertEqual(canonical_12.read_text(encoding="utf-8"), self.fixture.scene_12_canonical)
        self.assertEqual(canonical_27.read_text(encoding="utf-8"), self.fixture.scene_27_canonical)
        self.assertIn("pendrive", canonical_12.read_text(encoding="utf-8").lower())
        self.assertIn("pendrive", canonical_27.read_text(encoding="utf-8").lower())
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

        self.assertEqual(run002.git(self.root, self.env, "status", "--porcelain=v1"), "")

        print(
            "P3_REAL_WORKLOAD_003: BOUNDED_UPSTREAM_CONTEXT=PASS; "
            "DOWNSTREAM_CANDIDATE=STAGED; CROSS_SCENE_PROPOSAL_COHERENCE=OBSERVED_PASS; "
            "CANONICAL_EFFECT=NOT_APPLIED; HUMAN_APPROVAL=NOT_REQUESTED; GOAL_DONE=NO"
        )


if __name__ == "__main__":
    unittest.main()
