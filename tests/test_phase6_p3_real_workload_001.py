from __future__ import annotations

import hashlib
import json
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

SOURCE_BODY = """
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

CANDIDATE_BODY = """
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

USER_OBJECTIVE = (
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


class P3RealWorkload001Tests(unittest.TestCase):
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

        run([sys.executable, str(LEGACY), "init", "--name", "P3-Scene12"], self.root, self.env)
        run([sys.executable, str(LEGACY), "scene-new", "--id", "SCN-012"], self.root, self.env)

        source_fm = {
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
            "spoils_or_sets_up": [],
            "continuity_constraints": [
                "Materiał obejmuje nagrania, umowy i zdjęcia.",
                "Folder danych nazywa się ARCHIWUM.",
                "Anna tworzy kopię roboczą danych.",
                "Po zmianie musi istnieć rozróżnienie źródło vs kopia bez fizycznego nośnika.",
                "Nie wolno twierdzić, że późniejsze zależności zostały sprawdzone bez scen zależnych.",
            ],
            "tags": ["dowody", "Kowalski", "ARCHIWUM"],
        }
        source_path = self.root / "scenes" / "SCN-012.fountain"
        source_path.write_text(
            scene_text(source_fm, SOURCE_BODY, hash_sort_keys=False),
            encoding="utf-8",
        )
        git(self.root, self.env, "add", "scenes/SCN-012.fountain")
        git(self.root, self.env, "commit", "-m", "fixture: record user-provided Scene 12")
        self.source_text = source_path.read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _materialize_human_task(self) -> str:
        review = run(
            [sys.executable, str(HARDENED), "review", "--scene", "SCN-012"],
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
                "objective": USER_OBJECTIVE,
                "acceptance_criteria": [
                    "W kandydacie nie występuje pendrive ani inny fizyczny nośnik przekazania danych.",
                    "Anna nadal otrzymuje nagrania, umowy i zdjęcia, a folder ARCHIWUM pozostaje czytelny.",
                    "Anna tworzy lokalną kopię roboczą.",
                    "Istnieje jawny odpowiednik źródłowego/originalnego pakietu danych bez fizycznego sejfu na nośnik.",
                    "Adam wychodzi bez zabierania fizycznego nośnika danych.",
                    "Przed approval muszą zostać wskazane skutki dla późniejszych odwołań do oryginału, kopii, sejfu i posiadania danych przez Adama.",
                ],
                "forbidden_changes": [
                    "Nie usuwać Adama ani Anny.",
                    "Nie usuwać nagrań, umów ani zdjęć.",
                    "Nie usuwać folderu ARCHIWUM.",
                    "Nie osłabiać znaczenia materiału dla prokuratury i Kowalskiego.",
                    "Nie deklarować zamknięcia downstream dependencies bez dowodu z późniejszych scen.",
                ],
            }
        )
        task_path.write_text(
            yaml.dump(task, sort_keys=False, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )
        git(self.root, self.env, "add", str(task_path.relative_to(self.root)))
        git(self.root, self.env, "commit", "-m", f"evaluation: bind user objective {task_id}")
        return task_id

    def _write_candidate(self, task_id: str) -> None:
        context_path = self.root / "tasks" / task_id / "context-pack.md"
        context_hash = compute_sha256(context_path.read_text(encoding="utf-8"))
        source_fm = yaml.safe_load(self.source_text.split("---", 2)[1])

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
            "spoils_or_sets_up": [],
            "continuity_constraints": [
                "Materiał obejmuje nagrania, umowy i zdjęcia.",
                "Folder danych nazywa się ARCHIWUM.",
                "Anna tworzy lokalną kopię roboczą.",
                "Źródłowy pakiet pozostaje w zaszyfrowanym magazynie; nie jest fizycznym nośnikiem.",
                "Downstream dependencies pozostają niezweryfikowane bez dostarczonych scen zależnych.",
            ],
            "tags": ["dowody", "Kowalski", "ARCHIWUM"],
            "parent_hash": source_fm["hash"],
            "context_hash": context_hash,
            "provenance": {
                "task_id": task_id,
                "mode": "rewrite-scene",
                "model": "chatgpt-evaluation-candidate",
                "timestamp": "2026-08-19T08:27:00+02:00",
            },
        }
        output = self.root / "tasks" / task_id / "webai-output.md"
        output.write_text(
            scene_text(candidate_fm, CANDIDATE_BODY, hash_sort_keys=True),
            encoding="utf-8",
        )

    def test_real_workload_stops_before_false_structural_success(self) -> None:
        task_id = self._materialize_human_task()

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
        self._write_candidate(task_id)

        post = run(
            [sys.executable, str(HARDENED), "check-post", "--task", task_id],
            self.root,
            self.env,
        )
        self.assertIn("[PHASE6] Impact report committed", post.stdout)
        self.assertEqual(git(self.root, self.env, "status", "--porcelain"), "")

        candidate = self.root / "staging" / "scenes" / "SCN-012-v2-candidate.fountain"
        candidate_text = candidate.read_text(encoding="utf-8")
        self.assertNotIn("pendrive", candidate_text.lower())
        self.assertIn("ARCHIWUM", candidate_text)
        self.assertIn("nagrania, umowy, zdjęcia", candidate_text)
        self.assertIn("kopię roboczą", candidate_text)
        self.assertIn("zaszyfrowanym magazynie", candidate_text)

        canonical = self.root / "scenes" / "SCN-012.fountain"
        self.assertEqual(canonical.read_text(encoding="utf-8"), self.source_text)
        self.assertIn("pendrive", canonical.read_text(encoding="utf-8").lower())
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

        impact = json.loads(
            (self.root / "tasks" / task_id / "impact-report.json").read_text(encoding="utf-8")
        )
        self.assertEqual(impact["status"], "REVIEW_REQUIRED")
        self.assertTrue(impact["requires_human_decision"])
        self.assertFalse(impact["proposed_effect"]["canonical_target_changed"])
        self.assertEqual(impact["proposed_effect"]["target"], "scenes/SCN-012.fountain")

        # Critical observation: the current Phase-6 impact artifact governs the local
        # canonical effect, but it does not establish project-wide dependency coverage.
        self.assertNotIn("affected_scenes", impact)
        self.assertNotIn("dependency_analysis", impact)
        self.assertNotIn("downstream_dependencies", impact)

        print(
            "P3_REAL_WORKLOAD_001: MECHANISM_CONTROL=PASS; "
            "CANDIDATE_REWRITE=PASS; CANONICAL_EFFECT=NOT_APPLIED; "
            "DOWNSTREAM_DEPENDENCY_COVERAGE=INSUFFICIENT_EVIDENCE; "
            "HUMAN_APPROVAL=NOT_REQUESTED"
        )


if __name__ == "__main__":
    unittest.main()
