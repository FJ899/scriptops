from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY = REPO_ROOT / "legacy" / "scriptops-v2-single.py"
HARDENED = REPO_ROOT / "phase6" / "scriptops-v2-hardening.py"

SCENE_12_BODY = """
INT. BIURO - DZIEŃ

Adam wchodzi do niewielkiego biura. Anna siedzi przy biurku i przegląda dokumenty.

ANNA
Masz ten pendrive?

Adam wyciąga z kieszeni czerwony pendrive i kładzie go na stole.

ADAM
Wszystko tam jest. Nagrania, umowy, zdjęcia.

Anna bierze pendrive i wkłada go do laptopa.

ANNA
Jeśli to trafi do prokuratury, Kowalski jest skończony.

Na ekranie pojawia się folder „ARCHIWUM”.

Anna kopiuje jego zawartość na komputer.

ANNA
Zrobię kopię. Oryginał schowamy w sejfie.

Adam bierze pendrive i wychodzi.
"""

SCENE_12_CANDIDATE_BODY = """
INT. BIURO - DZIEŃ

Adam wchodzi do niewielkiego biura. Anna siedzi przy biurku i przegląda dokumenty.

ANNA
Masz dostęp?

ADAM
Wysłałem ci jednorazowy link. Wszystko tam jest. Nagrania, umowy, zdjęcia.

Anna otwiera wiadomość na laptopie. Uruchamia zaszyfrowany transfer.

ANNA
Jeśli to trafi do prokuratury, Kowalski jest skończony.

Na ekranie pojawia się folder „ARCHIWUM”.

Anna kopiuje jego zawartość na komputer.

ANNA
Zrobię kopię roboczą. Źródłowy pakiet zostaje w zaszyfrowanym magazynie. Tej wersji nie ruszamy.

Transfer kończy się. Adam wychodzi.
"""

SCENE_27_BODY = """
INT. MIESZKANIE ADAMA - NOC

Adam zamyka drzwi na dwa zamki i podchodzi do biurka.

Telefon wibruje.

ANNA
Masz jeszcze oryginał?

Adam otwiera dolną szufladę. Wyciąga czerwony pendrive.

ADAM
Mam.

ANNA
Kopia z mojego laptopa zniknęła. Ktoś ją usunął.

Adam patrzy na pendrive, ale nie podłącza go do komputera.

ADAM
Czyli zostało tylko to, co jest u mnie.

Po drugiej stronie zapada cisza.

ANNA
Nie wkładaj go do żadnego komputera. I nie oddawaj nikomu.

Adam chowa pendrive z powrotem do szuflady i przekręca klucz.

ADAM
Bez mojego udziału nikt tych danych nie dostanie.

Rozłącza się.
"""

GOAL = (
    "Całkowicie usunąć pendrive z projektu i zastąpić go sposobem przekazania danych, "
    "który nie wymaga żadnego fizycznego nośnika, zachowując logikę sceny i wszystkie "
    "wynikające z niej późniejsze zależności."
)


def run(
    cmd: list[str],
    cwd: Path,
    env: dict[str, str],
    *,
    ok: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if ok and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def git(cwd: Path, env: dict[str, str], *args: str) -> str:
    return run(["git", *args], cwd, env).stdout.strip()


def compute_sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def scene_text(front_matter: dict, body: str, *, hash_sort_keys: bool) -> str:
    fm = dict(front_matter)
    canonical = yaml.dump(
        fm,
        sort_keys=hash_sort_keys,
        allow_unicode=True,
        default_flow_style=False,
    ) + body
    fm["hash"] = compute_sha256(canonical)
    return "---\n" + yaml.dump(
        fm,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ) + "---" + body


class P3RealWorkload002Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = os.environ.copy()
        self.env.update(
            GIT_AUTHOR_NAME="ScriptOps P3 Evaluation",
            GIT_AUTHOR_EMAIL="p3-evaluation@example.invalid",
            GIT_COMMITTER_NAME="ScriptOps P3 Evaluation",
            GIT_COMMITTER_EMAIL="p3-evaluation@example.invalid",
            PYTHONDONTWRITEBYTECODE="1",
        )

        run([sys.executable, str(LEGACY), "init", "--name", "P3-Scene12-27"], self.root, self.env)
        run([sys.executable, str(LEGACY), "scene-new", "--id", "SCN-012"], self.root, self.env)
        run([sys.executable, str(LEGACY), "scene-new", "--id", "SCN-027"], self.root, self.env)

        scene_12_fm = {
            "scene_id": "SCN-012",
            "version": 1,
            "status": "accepted",
            "title": "Biuro / dzień",
            "act": 1,
            "sequence": "",
            "location": "BIURO",
            "time": "DZIEŃ",
            "characters": ["Adam", "Anna"],
            "purpose": [
                "Adam przekazuje Annie materiał dowodowy przeciw Kowalskiemu",
                "Anna zabezpiecza kopię danych do dalszego użycia",
            ],
            "emotional_turn": {"from": "ostrożność", "to": "decyzja o zabezpieczeniu materiału"},
            "depends_on": [],
            "spoils_or_sets_up": ["SCN-027"],
            "continuity_constraints": [
                "Materiał obejmuje nagrania, umowy i zdjęcia.",
                "Folder danych nazywa się ARCHIWUM.",
                "Anna tworzy kopię roboczą danych.",
                "SCN-027 odwołuje się do oryginału, kopii i kontroli danych przez Adama.",
            ],
            "tags": ["dowody", "Kowalski", "ARCHIWUM"],
        }
        scene_27_fm = {
            "scene_id": "SCN-027",
            "version": 1,
            "status": "accepted",
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
                "Po zmianie z SCN-012 Adam musi nadal kontrolować jedyne pozostałe źródło lub dostęp.",
                "Nie wolno zachować fizycznego pendrive'a jako nośnika danych.",
            ],
            "tags": ["dowody", "Kowalski", "utrata-kopii"],
        }

        scene_12 = self.root / "scenes" / "SCN-012.fountain"
        scene_27 = self.root / "scenes" / "SCN-027.fountain"
        scene_12.write_text(scene_text(scene_12_fm, SCENE_12_BODY, hash_sort_keys=False), encoding="utf-8")
        scene_27.write_text(scene_text(scene_27_fm, SCENE_27_BODY, hash_sort_keys=False), encoding="utf-8")
        git(self.root, self.env, "add", "scenes/SCN-012.fountain", "scenes/SCN-027.fountain")
        git(self.root, self.env, "commit", "-m", "fixture: record user-provided Scene 12 and Scene 27 dependency")
        self.scene_12_canonical = scene_12.read_text(encoding="utf-8")
        self.scene_27_canonical = scene_27.read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _rewrite_task(self, scene_id: str, objective: str) -> str:
        review = run(
            [sys.executable, str(HARDENED), "review", "--scene", scene_id],
            self.root,
            self.env,
        )
        match = re.search(r"TASK-[0-9]{14}", review.stdout)
        self.assertIsNotNone(match, review.stdout)
        task_id = match.group(0)
        task_path = self.root / "tasks" / task_id / "task-pack.yaml"
        task = yaml.safe_load(task_path.read_text(encoding="utf-8"))
        task.update(
            {
                "author": "human",
                "mode": "rewrite-scene",
                "objective": objective,
                "acceptance_criteria": [
                    "Nie używać fizycznego nośnika danych.",
                    "Zachować semantykę źródła/originalu i kopii.",
                    "Zachować kontrolę Adama nad pozostałym źródłem lub dostępem.",
                    "Nie deklarować downstream consistency bez dowodu z zależnych scen.",
                ],
                "forbidden_changes": [
                    "Nie usuwać Adama ani Anny.",
                    "Nie usuwać znaczenia danych dla sprawy Kowalskiego.",
                    "Nie promować kandydata do kanonu bez Human approve --why.",
                ],
            }
        )
        task_path.write_text(
            yaml.dump(task, sort_keys=False, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
        git(self.root, self.env, "add", str(task_path.relative_to(self.root)))
        git(self.root, self.env, "commit", "-m", f"evaluation: bind rewrite objective {task_id}")
        return task_id

    def _stage_scene_12_candidate(self) -> str:
        task_id = self._rewrite_task("SCN-012", GOAL)
        run([sys.executable, str(HARDENED), "check-pre", "--task", task_id], self.root, self.env)
        run(
            [
                sys.executable,
                str(HARDENED),
                "context-build",
                "--scene",
                "SCN-012",
                "--mode",
                "rewrite-scene",
                "--task",
                task_id,
            ],
            self.root,
            self.env,
        )

        context = self.root / "tasks" / task_id / "context-pack.md"
        source_fm = yaml.safe_load(self.scene_12_canonical.split("---", 2)[1])
        candidate_fm = {
            "scene_id": "SCN-012",
            "version": 2,
            "status": "candidate",
            "title": "Biuro / dzień",
            "act": 1,
            "sequence": "",
            "location": "BIURO",
            "time": "DZIEŃ",
            "characters": ["Adam", "Anna"],
            "purpose": [
                "Adam przekazuje Annie materiał dowodowy przeciw Kowalskiemu",
                "Anna zabezpiecza kopię danych do dalszego użycia",
            ],
            "emotional_turn": {"from": "ostrożność", "to": "decyzja o zabezpieczeniu materiału"},
            "depends_on": [],
            "spoils_or_sets_up": ["SCN-027"],
            "continuity_constraints": [
                "Materiał obejmuje nagrania, umowy i zdjęcia.",
                "Folder danych nazywa się ARCHIWUM.",
                "Anna tworzy lokalną kopię roboczą.",
                "Źródłowy pakiet pozostaje w zaszyfrowanym magazynie i nie jest fizycznym nośnikiem.",
                "SCN-027 wymaga późniejszej adaptacji semantyki oryginału, kopii i kontroli Adama.",
            ],
            "tags": ["dowody", "Kowalski", "ARCHIWUM"],
            "parent_hash": source_fm["hash"],
            "context_hash": compute_sha256(context.read_text(encoding="utf-8")),
            "provenance": {
                "task_id": task_id,
                "mode": "rewrite-scene",
                "model": "chatgpt-evaluation-candidate",
                "timestamp": "2026-08-19T09:39:00+02:00",
            },
        }
        output = self.root / "tasks" / task_id / "webai-output.md"
        output.write_text(
            scene_text(candidate_fm, SCENE_12_CANDIDATE_BODY, hash_sort_keys=True),
            encoding="utf-8",
        )
        run([sys.executable, str(HARDENED), "check-post", "--task", task_id], self.root, self.env)
        return task_id

    def test_downstream_context_reads_old_canon_not_staged_upstream_candidate(self) -> None:
        upstream_task = self._stage_scene_12_candidate()

        staged = self.root / "staging" / "scenes" / "SCN-012-v2-candidate.fountain"
        self.assertTrue(staged.exists())
        self.assertNotIn("pendrive", staged.read_text(encoding="utf-8").lower())
        self.assertIn("jednorazowy link", staged.read_text(encoding="utf-8").lower())

        canonical_12 = self.root / "scenes" / "SCN-012.fountain"
        self.assertEqual(canonical_12.read_text(encoding="utf-8"), self.scene_12_canonical)
        self.assertIn("pendrive", canonical_12.read_text(encoding="utf-8").lower())

        downstream_task = self._rewrite_task(
            "SCN-027",
            "Dostosować wszystkie zależności SCN-027 do beznośnikowego przekazania danych z SCN-012, "
            "zachowując utratę kopii Anny i wyłączną kontrolę Adama nad pozostałym źródłem lub dostępem.",
        )
        run([sys.executable, str(HARDENED), "check-pre", "--task", downstream_task], self.root, self.env)
        run(
            [
                sys.executable,
                str(HARDENED),
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

        # The dependency is known, but ContextBuilder resolves accepted scenes before staging.
        # Therefore SCN-027 receives the old physical-carrier SCN-012 as its neighbor context,
        # even though a validated/staged no-carrier SCN-012 candidate already exists.
        self.assertIn("### SCN-012", context_text)
        self.assertIn("czerwony pendrive", context_text.lower())
        self.assertIn("oryginał schowamy w sejfie", context_text.lower())
        self.assertNotIn("jednorazowy link", context_text.lower())
        self.assertNotIn("źródłowy pakiet zostaje w zaszyfrowanym magazynie", context_text.lower())

        canonical_27 = self.root / "scenes" / "SCN-027.fountain"
        self.assertEqual(canonical_27.read_text(encoding="utf-8"), self.scene_27_canonical)
        self.assertIn("czerwony pendrive", canonical_27.read_text(encoding="utf-8").lower())
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

        impact = self.root / "tasks" / upstream_task / "impact-report.json"
        self.assertTrue(impact.exists())

        print(
            "P3_REAL_WORKLOAD_002: DEPENDENCY_PRESENT=YES; UPSTREAM_CANDIDATE=STAGED; "
            "DOWNSTREAM_CONTEXT_SOURCE=OLD_CANONICAL; CROSS_SCENE_CANDIDATE_COHERENCE=BLOCKED; "
            "CANONICAL_EFFECT=NOT_APPLIED; HUMAN_APPROVAL=NOT_REQUESTED; GOAL_DONE=NO"
        )


if __name__ == "__main__":
    unittest.main()
