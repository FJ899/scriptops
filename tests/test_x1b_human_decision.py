from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE6 = REPO_ROOT / "phase6"
LEGACY = REPO_ROOT / "legacy" / "scriptops-v2-single.py"
sys.path.insert(0, str(PHASE6))
import x1b_human_decision as x1b


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None, ok: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if ok and cp.returncode:
        raise AssertionError(f"command failed: {cmd}\nstdout={cp.stdout}\nstderr={cp.stderr}")
    return cp


def git(root: Path, *args: str, ok: bool = True) -> str:
    env = os.environ.copy()
    env.update(
        GIT_AUTHOR_NAME="Fixture",
        GIT_AUTHOR_EMAIL="fixture@example.invalid",
        GIT_COMMITTER_NAME="Fixture",
        GIT_COMMITTER_EMAIL="fixture@example.invalid",
    )
    return run(["git", *args], root, env, ok=ok).stdout.strip()


def raw_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class X1BTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        git(self.root, "init")
        git(self.root, "branch", "-M", "main")
        (self.root / ".scriptops").mkdir()
        (self.root / "scenes").mkdir()
        (self.root / "staging" / "scenes").mkdir(parents=True)
        (self.root / "tasks" / "TASK-0001").mkdir(parents=True)
        (self.root / ".scriptops" / "config.yaml").write_text("project:\n  name: Fixture\n", encoding="utf-8")

        base_fm = {
            "scene_id": "SCN-001",
            "version": 1,
            "status": "idea",
            "title": "Before",
            "act": 1,
        }
        base_body = "\nINT. ROOM - DAY\n\nOLD\n"
        base_no_hash = dict(base_fm)
        canonical = yaml.dump(base_no_hash, sort_keys=False, allow_unicode=True, default_flow_style=False) + base_body
        base_fm["hash"] = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
        base_text = "---\n" + yaml.dump(base_fm, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---" + base_body
        (self.root / "scenes" / "SCN-001.fountain").write_text(base_text, encoding="utf-8")

        candidate_fm = {
            "scene_id": "SCN-001",
            "version": 2,
            "status": "candidate",
            "title": "After",
            "act": 1,
        }
        candidate_body = "\nINT. ROOM - DAY\n\nNEW HUMAN-REVIEWED CONTENT\n"
        candidate_no_hash = dict(candidate_fm)
        candidate_canonical = yaml.dump(
            candidate_no_hash, sort_keys=False, allow_unicode=True, default_flow_style=False
        ) + candidate_body
        candidate_fm["hash"] = "sha256:" + hashlib.sha256(candidate_canonical.encode()).hexdigest()
        candidate_text = "---\n" + yaml.dump(
            candidate_fm, sort_keys=False, allow_unicode=True, default_flow_style=False
        ) + "---" + candidate_body
        self.candidate_path = self.root / "staging" / "scenes" / "SCN-001-v2-candidate.fountain"
        self.candidate_path.write_text(candidate_text, encoding="utf-8")
        candidate_bytes = self.candidate_path.read_bytes()

        impact = {
            "schema_version": "scriptops-phase6-impact/0.2-x1b",
            "task_id": "TASK-0001",
            "scene_id": "SCN-001",
            "status": "REVIEW_REQUIRED",
            "candidate": {
                "path": "staging/scenes/SCN-001-v2-candidate.fountain",
                "file_sha256": "sha256:" + raw_sha(candidate_bytes),
            },
            "requires_human_decision": True,
        }
        self.impact_path = self.root / "tasks" / "TASK-0001" / "impact-report.json"
        self.impact_path.write_text(json.dumps(impact, indent=2) + "\n", encoding="utf-8")

        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "fixture base")
        self.git = x1b.AnchoredGitV2.discover(self.root)
        self.local = x1b.local_preflight(self.git, "SCN-001")
        self.request, self.request_bytes, self.digest = x1b.build_request(
            self.local, "proposal only; not Human rationale", "11" * 32
        )
        self.review_commit = "a" * 40

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def reviews(self, *, user_id: int = x1b.TRUSTED_HUMAN_GITHUB_USER_ID, login: str = "litrgratis-pixel", state: str = "APPROVED", body: str | None = None, review_id: int = 101, submitted: str = "2026-09-03T10:00:00Z") -> bytes:
        if body is None:
            body = f"X1B-HUMAN-DECISION-V2\nrequest_sha256={self.digest}\ndecision=APPROVE"
        value = [
            {
                "id": review_id,
                "user": {"id": user_id, "login": login, "node_id": "U_TEST"},
                "state": state,
                "body": body,
                "submitted_at": submitted,
                "commit_id": self.review_commit,
            }
        ]
        return json.dumps(value, separators=(",", ":")).encode()

    def admission(self) -> tuple[dict, dict]:
        return x1b.admission_from_evidence(
            self.local,
            77,
            self.reviews(),
            self.request_bytes,
            self.local.accepted_scene_bytes,
        )

    def test_wrong_login_same_name_does_not_override_numeric_id(self) -> None:
        with self.assertRaises(x1b.X1BError):
            x1b.select_human_review(self.reviews(user_id=999999, login="litrgratis-pixel"))
        selected = x1b.select_human_review(
            self.reviews(user_id=x1b.TRUSTED_HUMAN_GITHUB_USER_ID, login="renamed-human")
        )
        self.assertEqual(selected["latest"]["user"]["id"], x1b.TRUSTED_HUMAN_GITHUB_USER_ID)

    def test_nonhuman_reserved_marker_denied(self) -> None:
        rows = json.loads(self.reviews().decode())
        rows.insert(
            0,
            {
                "id": 100,
                "user": {"id": 42, "login": "ai-process", "node_id": "U_AI"},
                "state": "COMMENTED",
                "body": "X1B-HUMAN-DECISION-V2\nforged",
                "submitted_at": "2026-09-03T09:00:00Z",
                "commit_id": self.review_commit,
            },
        )
        with self.assertRaises(x1b.X1BError):
            x1b.select_human_review(json.dumps(rows).encode())

    def test_latest_changes_requested_or_dismissed_denies(self) -> None:
        rows = json.loads(self.reviews().decode())
        rows.append(
            {
                "id": 102,
                "user": {"id": x1b.TRUSTED_HUMAN_GITHUB_USER_ID, "login": "litrgratis-pixel", "node_id": "U_TEST"},
                "state": "CHANGES_REQUESTED",
                "body": "revoke",
                "submitted_at": "2026-09-03T11:00:00Z",
                "commit_id": self.review_commit,
            }
        )
        with self.assertRaises(x1b.X1BError):
            x1b.select_human_review(json.dumps(rows).encode())
        rows[-1]["state"] = "DISMISSED"
        with self.assertRaises(x1b.X1BError):
            x1b.select_human_review(json.dumps(rows).encode())

    def test_duplicate_json_key_denied(self) -> None:
        with self.assertRaises(x1b.X1BError):
            x1b.parse_json_strict(b'{"a":1,"a":2}')

    def test_request_candidate_or_effect_drift_denied(self) -> None:
        bad = dict(self.request)
        bad["candidate_sha256"] = "00" * 32
        bad_bytes = x1b.pretty_json_bytes(bad)
        bad_digest = raw_sha(x1b.canonical_json_bytes(bad))
        with self.assertRaises(x1b.X1BError):
            x1b.validate_request(bad_bytes, bad_digest, self.local.accepted_scene_bytes, self.local)

    def test_network_child_env_is_fresh(self) -> None:
        old = os.environ.copy()
        try:
            os.environ.update(
                SSL_CERT_FILE="/tmp/attacker.pem",
                SSL_CERT_DIR="/tmp/attacker-dir",
                OPENSSL_CONF="/tmp/openssl.cnf",
                OPENSSL_MODULES="/tmp/modules",
                PYTHONPATH="/tmp/attacker-python",
                TOTALLY_UNKNOWN_ATTACKER_KEY="1",
            )
            self.assertEqual(x1b.network_child_env(), {"X1B_NETWORK_CHILD": "1"})
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_anchored_git_ignores_attacker_git_environment(self) -> None:
        attacker = self.root / "attacker"
        attacker.mkdir()
        old = os.environ.copy()
        try:
            os.environ.update(
                GIT_DIR=str(attacker / ".git"),
                GIT_WORK_TREE=str(attacker),
                GIT_INDEX_FILE=str(attacker / "index"),
                GIT_NAMESPACE="evil",
            )
            anchored = x1b.AnchoredGitV2.discover(self.root)
            self.assertEqual(anchored.root, self.root.resolve())
            self.assertEqual(anchored.main_head(), self.local.base_head)
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_positive_two_path_cas_effect(self) -> None:
        admission, request = self.admission()
        base = self.local.base_head
        result = x1b.execute_admission(self.git, self.local, admission, request)
        self.assertTrue(result["human_decision"])
        self.assertEqual(result["status"], "COMMITTED")
        head = self.git.main_head()
        self.assertNotEqual(head, base)
        parent = self.git.text("rev-parse", f"{head}^")
        self.assertEqual(parent, base)
        changed = sorted(self.git.text("diff-tree", "--no-commit-id", "--name-only", "-r", base, head).splitlines())
        self.assertEqual(changed, [".scriptops/decision-log.ndjson", "scenes/SCN-001.fountain"])
        self.assertEqual((self.root / "scenes" / "SCN-001.fountain").read_bytes(), self.local.accepted_scene_bytes)
        log_path = self.root / ".scriptops" / "decision-log.ndjson"
        self.assertTrue(log_path.exists(), "absent base decision log must be created as the second bound path")
        row = json.loads(log_path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertTrue(row["human_decision"])
        self.assertEqual(row["human_github_user_id"], x1b.TRUSTED_HUMAN_GITHUB_USER_ID)
        self.assertNotIn("approver", row)
        self.assertEqual(self.git.text("status", "--porcelain=v1", "--untracked-files=all"), "")

    def test_stale_base_cannot_canonicalize(self) -> None:
        admission, request = self.admission()
        (self.root / "EXTERNAL.txt").write_text("external\n", encoding="utf-8")
        git(self.root, "add", "EXTERNAL.txt")
        git(self.root, "commit", "-m", "external main movement")
        external_head = self.git.main_head()
        with self.assertRaises(x1b.X1BError):
            x1b.execute_admission(self.git, self.local, admission, request)
        self.assertEqual(self.git.main_head(), external_head)
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

    def test_legacy_approve_and_promote_accepted_block(self) -> None:
        env = os.environ.copy()
        env.update(
            GIT_AUTHOR_NAME="Fixture",
            GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_NAME="Fixture",
            GIT_COMMITTER_EMAIL="fixture@example.invalid",
        )
        before = (self.root / "scenes" / "SCN-001.fountain").read_bytes()
        approve = run(
            [sys.executable, str(LEGACY), "approve", "--scene", "SCN-001"],
            self.root,
            env,
            ok=False,
        )
        self.assertEqual(approve.returncode, 2)
        self.assertIn("direct legacy cmd_approve is disabled", approve.stderr)
        promote = run(
            [sys.executable, str(LEGACY), "scene-promote", "--id", "SCN-001", "--to", "accepted"],
            self.root,
            env,
            ok=False,
        )
        self.assertEqual(promote.returncode, 2)
        self.assertIn("scene-promote --to accepted is disabled", promote.stderr)
        self.assertEqual((self.root / "scenes" / "SCN-001.fountain").read_bytes(), before)
        self.assertFalse((self.root / ".scriptops" / "decision-log.ndjson").exists())

    def test_review_limit_and_replay_are_fail_closed(self) -> None:
        row = json.loads(self.reviews().decode())[0]
        rows = []
        for idx in range(100):
            copy = json.loads(json.dumps(row))
            copy["id"] = idx + 1
            copy["state"] = "COMMENTED" if idx < 99 else "APPROVED"
            copy["body"] = "neutral" if idx < 99 else row["body"]
            rows.append(copy)
        with self.assertRaises(x1b.X1BError):
            x1b.select_human_review(json.dumps(rows).encode())
        admission, request = self.admission()
        record = {"schema_version": x1b.DECISION_SCHEMA, "request_sha256": admission["request_sha256"]}
        with self.assertRaises(x1b.X1BError):
            x1b._scan_replay(x1b.canonical_json_bytes(record) + b"\n", admission["request_sha256"])


if __name__ == "__main__":
    unittest.main()
