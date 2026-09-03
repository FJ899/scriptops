from __future__ import annotations

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


def run(cmd: list[str], cwd: Path, env: dict[str, str], *, ok: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if ok and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def git(cwd: Path, env: dict[str, str], *args: str) -> str:
    return run(["git", *args], cwd, env).stdout.strip()


def compute_sha256(text: str) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


class Phase6SmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.env = os.environ.copy()
        self.env.update(
            GIT_AUTHOR_NAME="ScriptOps Phase6 Test",
            GIT_AUTHOR_EMAIL="phase6@example.invalid",
            GIT_COMMITTER_NAME="ScriptOps Phase6 Test",
            GIT_COMMITTER_EMAIL="phase6@example.invalid",
            PYTHONDONTWRITEBYTECODE="1",
        )
        run([sys.executable, str(LEGACY), "init", "--name", "Phase6Smoke"], self.root, self.env)
        run([sys.executable, str(LEGACY), "scene-new", "--id", "SCN-001"], self.root, self.env)
        self.assertEqual(git(self.root, self.env, "status", "--porcelain"), "")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _review_to_context(self) -> str:
        review = run(
            [sys.executable, str(HARDENED), "review", "--scene", "SCN-001"],
            self.root,
            self.env,
        )
        match = re.search(r"TASK-[0-9]{14}", review.stdout)
        self.assertIsNotNone(match, review.stdout)
        task_id = match.group(0)
        self.assertEqual(git(self.root, self.env, "status", "--porcelain"), "")

        run([sys.executable, str(HARDENED), "check-pre", "--task", task_id], self.root, self.env)
        self.assertEqual(git(self.root, self.env, "status", "--porcelain"), "")

        run(
            [
                sys.executable,
                str(HARDENED),
                "context-build",
                "--scene",
                "SCN-001",
                "--mode",
                "continuity-review",
                "--task",
                task_id,
            ],
            self.root,
            self.env,
        )
        self.assertEqual(git(self.root, self.env, "status", "--porcelain"), "")
        return task_id

    def _write_candidate(self, task_id: str) -> Path:
        body = "\nINT. TEST ROOM - DAY\n\nALICE\nKontrolowany kandydat.\n"
        fm = {
            "scene_id": "SCN-001",
            "version": 2,
            "status": "candidate",
            "title": "Phase 6 smoke",
            "act": 1,
        }
        canonical = yaml.dump(
            fm, sort_keys=True, allow_unicode=True, default_flow_style=False
        ) + body
        fm["hash"] = compute_sha256(canonical)
        text = "---\n" + yaml.dump(
            fm, sort_keys=False, allow_unicode=True, default_flow_style=False
        ) + "---" + body
        path = self.root / "tasks" / task_id / "webai-output.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_controlled_path_stops_at_review_required_without_human_evidence(self) -> None:
        task_id = self._review_to_context()
        self._write_candidate(task_id)
        run([sys.executable, str(HARDENED), "check-post", "--task", task_id], self.root, self.env)
        self.assertEqual(git(self.root, self.env, "status", "--porcelain"), "")

        impact_path = self.root / "tasks" / task_id / "impact-report.json"
        impact = json.loads(impact_path.read_text(encoding="utf-8"))
        self.assertEqual(impact["status"], "REVIEW_REQUIRED")
        self.assertTrue(impact["requires_human_decision"])
        self.assertFalse(impact["proposed_effect"]["canonical_target_changed"])
        self.assertEqual(
            impact["human_authority_route"],
            "X1B-HUMAN-DECISION-V2 GitHub pull-request review",
        )
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

    def test_approve_without_decision_pr_is_rejected(self) -> None:
        result = run(
            [sys.executable, str(HARDENED), "approve", "--scene", "SCN-001"],
            self.root,
            self.env,
            ok=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--decision-pr", result.stderr)

    def test_old_why_is_not_an_approval_credential(self) -> None:
        result = run(
            [
                sys.executable,
                str(HARDENED),
                "approve",
                "--scene",
                "SCN-001",
                "--decision-pr",
                "1",
                "--why",
                "AI supplied text",
            ],
            self.root,
            self.env,
            ok=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_candidate_import_refuses_unrelated_dirty_state(self) -> None:
        task_id = self._review_to_context()
        self._write_candidate(task_id)
        (self.root / "UNRELATED.txt").write_text("must block\n", encoding="utf-8")
        result = run(
            [sys.executable, str(HARDENED), "check-post", "--task", task_id],
            self.root,
            self.env,
            ok=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("refuses unrelated dirty state", result.stderr)
        self.assertFalse((self.root / "tasks" / task_id / "impact-report.json").exists())


if __name__ == "__main__":
    unittest.main()
