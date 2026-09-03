#!/usr/bin/env python3
"""Deterministic repository verification for active ScriptOps + X1B V2."""
from __future__ import annotations

import sys
from pathlib import Path

from restore_v2 import EXPECTED_SHA256, EXPECTED_SIZE, RestoreError, validate_historical_parts

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PROJECT_STATE.md",
    "HANDOFF.md",
    "SOURCE_MANIFEST.md",
    "legacy/scriptops-v2-single.py",
    "phase6/scriptops-v2-hardening.py",
    "phase6/x1b_human_decision.py",
    "scripts/restore_v2.py",
    "scripts/verify_repository.py",
    "sources/prototype/RESTORE.md",
    "tests/test_phase6_scriptops_smoke.py",
    "tests/test_x1b_human_decision.py",
    ".github/workflows/x1b-human-decision.yml",
    "evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md",
    "sources/RC1_SCOPE_LOCK.md",
]
PROTOTYPE_PARTS = [f"sources/prototype/scriptops-v2-single.py.part{i:02d}" for i in range(1, 8)]


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def text(path: str) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path}: {exc}")
    raise AssertionError("unreachable")


def require(path: str, *markers: str) -> None:
    content = text(path)
    for marker in markers:
        if marker not in content:
            fail(f"{path} missing required marker: {marker}")


def forbid(path: str, *markers: str) -> None:
    content = text(path)
    for marker in markers:
        if marker in content:
            fail(f"{path} contains forbidden active marker: {marker}")


def check_required_files() -> None:
    missing = [p for p in REQUIRED_FILES + PROTOTYPE_PARTS if not (ROOT / p).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))
    print(f"[PASS] required files present: {len(REQUIRED_FILES) + len(PROTOTYPE_PARTS)}")


def check_historical_prototype() -> None:
    try:
        digest = validate_historical_parts()
    except RestoreError as exc:
        fail(f"historical prototype transport invalid: {exc}")
    if digest != EXPECTED_SHA256:
        fail("historical prototype digest mismatch")
    print(f"[PASS] historical prototype preserved: {EXPECTED_SIZE} B / {digest}")
    active = (ROOT / "legacy/scriptops-v2-single.py").read_bytes()
    historical = b"".join((ROOT / part).read_bytes() for part in PROTOTYPE_PARTS)
    if active == historical:
        fail("active legacy path must not equal unsafe historical executable bytes")
    require(
        "scripts/restore_v2.py",
        "historical prototype may not overwrite active legacy/scriptops-v2-single.py",
        "validate_historical_parts",
    )
    print("[PASS] historical reconstruction cannot reactivate unsafe approval path")


def check_x1b_core() -> None:
    require(
        "phase6/x1b_human_decision.py",
        "TRUSTED_HUMAN_GITHUB_USER_ID = 226907434",
        "X1B-HUMAN-DECISION-V2",
        "x1b-human-decision-request/v2",
        "x1b-operation-admission/v2",
        "scriptops-x1b-decision/v2",
        "git-update-ref-compare-and-swap",
        "refs/heads/main",
        "GIT_CONFIG_NOSYSTEM",
        "GIT_CONFIG_GLOBAL",
        "GIT_NO_REPLACE_OBJECTS",
        "scriptops-x1b.lock",
        "update-ref",
        "commit-tree",
        "X1B_NETWORK_CHILD",
        "ssl.create_default_context",
        "CERT_REQUIRED",
        "api.github.com",
        "human_decision\": True",
    )
    forbid(
        "phase6/x1b_human_decision.py",
        "requests.get(",
        "verify=False",
        "http://api.github.com",
    )
    print("[PASS] X1B V2 core authority/admission/CAS/TLS markers present")


def check_active_routes() -> None:
    require(
        "phase6/scriptops-v2-hardening.py",
        "approve.add_argument(\"--decision-pr\"",
        "x1b.approve_scene",
        "HumanDecision=TRUE",
        "X1B-HUMAN-DECISION-V2 GitHub pull-request review",
    )
    forbid(
        "phase6/scriptops-v2-hardening.py",
        "approve.add_argument(\"--why\"",
        '"approver": "human"',
    )
    require(
        "legacy/scriptops-v2-single.py",
        "LegacyApprovalDisabled",
        "direct legacy cmd_approve is disabled before mutation",
        "legacy scene-promote --to accepted is disabled",
    )
    forbid(
        "legacy/scriptops-v2-single.py",
        '"approver": "human"',
        "scriptops: accept {scene_id}",
    )
    print("[PASS] Phase6 requires decision PR; direct legacy accepted-state routes fail closed")


def check_tests_and_workflow() -> None:
    require(
        "tests/test_x1b_human_decision.py",
        "test_wrong_login_same_name_does_not_override_numeric_id",
        "test_nonhuman_reserved_marker_denied",
        "test_network_child_env_is_fresh",
        "test_anchored_git_ignores_attacker_git_environment",
        "test_positive_two_path_cas_effect",
        "test_stale_base_cannot_canonicalize",
        "test_legacy_approve_and_promote_accepted_block",
    )
    require(
        "tests/test_phase6_scriptops_smoke.py",
        "--decision-pr",
        "test_approve_without_decision_pr_is_rejected",
        "test_candidate_import_refuses_unrelated_dirty_state",
    )
    require(
        ".github/workflows/x1b-human-decision.yml",
        "test_x1b_human_decision",
        "verify_repository.py",
    )
    print("[PASS] X1B negative/positive regression test surface and CI workflow present")


def check_docs() -> None:
    for path in ("README.md", "PROJECT_STATE.md", "HANDOFF.md"):
        require(
            path,
            "X1B Human Decision Authorship V2",
            "approve --scene <SCN-ID> --decision-pr <PR-NUMBER>",
            "--why is not Human authority",
            "HumanDecision=TRUE only after post-effect verification",
        )
    require(
        "SOURCE_MANIFEST.md",
        "phase6/x1b_human_decision.py",
        "historical prototype",
        "legacy/scriptops-v2-single.py",
    )
    require(
        "sources/prototype/RESTORE.md",
        "HISTORICAL ONLY",
        "must not overwrite `legacy/scriptops-v2-single.py`",
    )
    print("[PASS] active docs route acceptance only through X1B V2 and preserve historical separation")


def main() -> int:
    check_required_files()
    check_historical_prototype()
    check_x1b_core()
    check_active_routes()
    check_tests_and_workflow()
    check_docs()
    print("[PASS] ScriptOps repository is self-consistent for X1B V2 implementation candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
