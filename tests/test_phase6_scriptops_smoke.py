from __future__ import annotations

import argparse
import dataclasses
import errno
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY = REPO_ROOT / "legacy" / "scriptops-v2-single.py"
HARDENED = REPO_ROOT / "phase6" / "scriptops-v2-hardening.py"
PHASE6 = REPO_ROOT / "phase6"
if str(PHASE6) not in sys.path:
    sys.path.insert(0, str(PHASE6))
import x1b_human_decision as x1b
import tests.test_x1b_human_decision as x1b_tests


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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        last: OSError | None = None
        for _ in range(8):
            try:
                self.tmp.cleanup()
                return
            except OSError as exc:
                if exc.errno != errno.ENOTEMPTY:
                    raise
                last = exc
                time.sleep(0.05)
        if last is not None:
            raise last

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

    def test_x1b_rb5_direct_function_calls_cannot_bypass_authority(self) -> None:
        legacy = load_module(LEGACY, "x1b_rb5_legacy")
        legacy.PROJECT_ROOT = self.root
        legacy.SCRIPTOPS_DIR = self.root / ".scriptops"
        legacy.CONFIG_PATH = legacy.SCRIPTOPS_DIR / "config.yaml"
        before = (self.root / "scenes" / "SCN-001.fountain").read_bytes()
        with self.assertRaises(legacy.LegacyApprovalDisabled):
            legacy.cmd_approve(argparse.Namespace(scene="SCN-001"))
        with self.assertRaises(legacy.LegacyApprovalDisabled):
            legacy.cmd_scene_promote(argparse.Namespace(id="SCN-001", to="accepted"))
        self.assertEqual((self.root / "scenes" / "SCN-001.fountain").read_bytes(), before)
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

        hardened = load_module(HARDENED, "x1b_rb5_hardened")
        hardened.ROOT = self.root
        with mock.patch.object(
            hardened.x1b,
            "approve_scene",
            side_effect=hardened.x1b.X1BError("no qualifying V2 authority"),
        ) as approve:
            with self.assertRaises(hardened.Phase6Error):
                hardened.cmd_approve(argparse.Namespace(scene="SCN-001", decision_pr=77))
        approve.assert_called_once_with("SCN-001", 77, root=self.root)
        self.assertEqual((self.root / "scenes" / "SCN-001.fountain").read_bytes(), before)
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())


class X1BRetainedMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = x1b_tests.X1BTests()
        self.case.setUp()

    def tearDown(self) -> None:
        self.case.tearDown()

    def test_x1b_a4_prior_approval_cannot_authorize_new_request(self) -> None:
        _, request2_bytes, digest2 = x1b.build_request(
            self.case.local, "new AI proposal", "22" * 32
        )
        self.assertNotEqual(digest2, self.case.digest)
        with self.assertRaises(x1b.X1BError):
            x1b.admission_from_evidence(
                self.case.local,
                77,
                self.case.reviews(),
                request2_bytes,
                self.case.local.accepted_scene_bytes,
            )

    def test_x1b_a5_approved_a_operative_a_prime_denied(self) -> None:
        with self.assertRaises(x1b.X1BError):
            x1b.admission_from_evidence(
                self.case.local,
                77,
                self.case.reviews(),
                self.case.request_bytes,
                self.case.local.accepted_scene_bytes + b"A-prime",
            )

    def test_x1b_a9_ai_created_human_looking_evidence_denied(self) -> None:
        with self.assertRaises(x1b.X1BError):
            x1b.select_human_review(
                self.case.reviews(user_id=42, login="litrgratis-pixel")
            )

    def test_nonexact_and_wrong_schema_request_json_denied(self) -> None:
        with self.assertRaises(x1b.X1BError):
            x1b.validate_request(
                x1b.canonical_json_bytes(self.case.request),
                self.case.digest,
                self.case.local.accepted_scene_bytes,
                self.case.local,
            )
        bad = json.loads(json.dumps(self.case.request))
        bad["schema_version"] = "x1b-human-decision-request/v999"
        bad_bytes = x1b.pretty_json_bytes(bad)
        bad_digest = x1b._sha256(x1b.canonical_json_bytes(bad))
        with self.assertRaises(x1b.X1BError):
            x1b.validate_request(
                bad_bytes, bad_digest, self.case.local.accepted_scene_bytes, self.case.local
            )

    def test_impact_and_accepted_scene_recomputation_drift_denied(self) -> None:
        drift_impact = dataclasses.replace(
            self.case.local, impact_report_sha256="00" * 32
        )
        with self.assertRaises(x1b.X1BError):
            x1b.validate_request(
                self.case.request_bytes,
                self.case.digest,
                self.case.local.accepted_scene_bytes,
                drift_impact,
            )
        drift_projection = dataclasses.replace(
            self.case.local,
            accepted_scene_bytes=self.case.local.accepted_scene_bytes + b"drift",
        )
        with self.assertRaises(x1b.X1BError):
            x1b.validate_request(
                self.case.request_bytes,
                self.case.digest,
                self.case.local.accepted_scene_bytes,
                drift_projection,
            )

    def test_refs_replace_present_denied(self) -> None:
        base = self.case.local.base_head
        self.case.git.run("update-ref", f"refs/replace/{base}", base)
        try:
            with self.assertRaises(x1b.X1BError):
                self.case.git.require_no_replace_refs()
            with self.assertRaises(x1b.X1BError):
                x1b.local_preflight(self.case.git, "SCN-001")
        finally:
            self.case.git.run("update-ref", "-d", f"refs/replace/{base}")

    def test_x1b_cas2_main_changes_before_cas_fails_without_overwrite(self) -> None:
        admission, request = self.case.admission()
        base = self.case.local.base_head
        prospective, _, _ = x1b._prospective_commit(
            self.case.git, self.case.local, admission, request
        )
        (self.case.root / "EXTERNAL.txt").write_text("external\n", encoding="utf-8")
        x1b_tests.git(self.case.root, "add", "EXTERNAL.txt")
        x1b_tests.git(self.case.root, "commit", "-m", "external main advance")
        external = self.case.git.require_direct_main()
        self.assertNotEqual(external, base)
        self.assertFalse(self.case.git.cas_main(prospective, base))
        self.assertEqual(self.case.git.require_direct_main(), external)

    def test_x1b_cas6_exact_cas_linearizes_once(self) -> None:
        admission, request = self.case.admission()
        base = self.case.local.base_head
        result = x1b.execute_admission(
            self.case.git, self.case.local, admission, request
        )
        self.assertEqual(result["status"], "COMMITTED")
        self.assertTrue(result["human_decision"])
        commit = result["commit"]
        self.assertEqual(self.case.git.require_direct_main(), commit)
        self.assertEqual(self.case.git.text("rev-parse", f"{commit}^"), base)
        self.assertNotEqual(commit, base)

    def test_x1b_cas9_stale_admission_after_effect_denied(self) -> None:
        admission, request = self.case.admission()
        first = x1b.execute_admission(
            self.case.git, self.case.local, admission, request
        )
        canonical = first["commit"]
        with self.assertRaises(x1b.X1BError):
            x1b.execute_admission(
                self.case.git, self.case.local, admission, request
            )
        self.assertEqual(self.case.git.require_direct_main(), canonical)

    def test_x1b_pu1_pu6_positive_chain_is_exact(self) -> None:
        admission, request = self.case.admission()
        self.assertEqual(admission["human_github_user_id"], x1b.TRUSTED_HUMAN_GITHUB_USER_ID)
        self.assertEqual(admission["human_review_commit_id"], self.case.review_commit)
        self.assertEqual(admission["request_sha256"], self.case.digest)
        prospective, new_log, _ = x1b._prospective_commit(
            self.case.git, self.case.local, admission, request
        )
        x1b._verify_prospective(
            self.case.git, self.case.local.base_head, prospective, self.case.local, new_log
        )
        result = x1b.execute_admission(
            self.case.git, self.case.local, admission, request
        )
        self.assertTrue(result["human_decision"])
        commit = result["commit"]
        self.assertEqual(self.case.git.require_direct_main(), commit)
        self.assertEqual(
            (self.case.root / self.case.local.accepted_scene_path).read_bytes(),
            self.case.local.accepted_scene_bytes,
        )
        row = json.loads(
            (self.case.root / ".scriptops" / "decision-log.ndjson")
            .read_text(encoding="utf-8")
            .splitlines()[-1]
        )
        self.assertEqual(row["human_github_user_id"], x1b.TRUSTED_HUMAN_GITHUB_USER_ID)
        self.assertEqual(row["human_review_commit_id"], self.case.review_commit)
        self.assertEqual(row["request_sha256"], self.case.digest)
        self.assertEqual(row["admission_id"], admission["admission_id"])
        self.assertEqual(row["admission_digest"], admission["admission_digest"])
        self.case.git.require_clean()


if __name__ == "__main__":
    unittest.main()
