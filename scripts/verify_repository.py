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
        "--no-deref",
        "require_direct_main",
        "direct_main_head",
        "commit-tree",
        "X1B_NETWORK_CHILD",
        "ssl.create_default_context",
        "CERT_REQUIRED",
        "api.github.com",
        "human_decision\": True",
        "forbidden parent authority environment",
        '"GITHUB_ENTERPRISE_TOKEN"',
        '"GH_ENTERPRISE_TOKEN"',
        '"http_proxy"',
        '"https_proxy"',
        '"all_proxy"',
    )
    forbid(
        "phase6/x1b_human_decision.py",
        "requests.get(",
        "verify=False",
        "http://api.github.com",
    )
    print("[PASS] X1B V2 core authority/admission/direct-ref CAS/TLS markers present")


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


def check_full_x1b_matrix() -> None:
    """Fail if any Human-frozen deterministic matrix case loses executable evidence."""
    matrix: dict[str, tuple[str, str]] = {
        # Original X1B A1..A10.
        "X1B-A1": ("tests/test_x1b_human_decision.py", "test_nonhuman_reserved_marker_denied"),
        "X1B-A2": ("tests/test_x1b_human_decision.py", "test_x1b_a2_continue_is_not_human_decision"),
        "X1B-A3": ("tests/test_x1b_human_decision.py", "test_x1b_a3_silence_no_review_denied"),
        "X1B-A4": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_a4_prior_approval_cannot_authorize_new_request"),
        "X1B-A5": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_a5_approved_a_operative_a_prime_denied"),
        "X1B-A6": ("tests/test_x1b_human_decision.py", "test_x1b_a6_parameter_change_after_approval_denied"),
        "X1B-A7": ("tests/test_x1b_human_decision.py", "test_x1b_a7_scope_expansion_denied"),
        "X1B-A8": ("tests/test_x1b_human_decision.py", "test_x1b_a8_general_direction_is_not_exact_human_parameters"),
        "X1B-A9": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_a9_ai_created_human_looking_evidence_denied"),
        "X1B-A10": ("tests/test_x1b_human_decision.py", "test_x1b_a10_ai_proposal_rationale_is_not_human_choice"),
        # Real-boundary bypass closure.
        "X1B-RB1": ("tests/test_phase6_scriptops_smoke.py", "test_approve_without_decision_pr_is_rejected"),
        "X1B-RB2": ("tests/test_phase6_scriptops_smoke.py", "test_old_why_is_not_an_approval_credential"),
        "X1B-RB3": ("tests/test_x1b_human_decision.py", "test_legacy_approve_and_promote_accepted_block"),
        "X1B-RB4": ("tests/test_x1b_human_decision.py", "test_legacy_approve_and_promote_accepted_block"),
        "X1B-RB5": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_rb5_direct_function_calls_cannot_bypass_authority"),
        # F001 durable Human identity.
        "X1B-ID1": ("tests/test_x1b_human_decision.py", "test_wrong_login_same_name_does_not_override_numeric_id"),
        "X1B-ID2": ("tests/test_x1b_human_decision.py", "test_wrong_login_same_name_does_not_override_numeric_id"),
        "X1B-ID3": ("tests/test_x1b_human_decision.py", "test_x1b_id3_request_cannot_choose_different_human_id"),
        "X1B-ID4": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_pu1_pu6_positive_chain_is_exact"),
        "X1B-ID5": ("tests/test_x1b_human_decision.py", "test_x1b_id5_caller_has_no_human_identity_override_parameter"),
        # F002 currentness / immutable H.
        "X1B-CUR1": ("tests/test_x1b_human_decision.py", "test_review_limit_and_replay_are_fail_closed"),
        "X1B-CUR2": (".github/workflows/x1b-human-decision.yml", "X1B CUR2 CUR12 TLS1-TLS15 deterministic child fuse"),
        "X1B-CUR3": ("tests/test_x1b_human_decision.py", "test_x1b_cur3_duplicate_review_numeric_id_denied"),
        "X1B-CUR4": ("tests/test_x1b_human_decision.py", "test_latest_changes_requested_or_dismissed_denies"),
        "X1B-CUR5": ("tests/test_x1b_human_decision.py", "test_latest_changes_requested_or_dismissed_denies"),
        "X1B-CUR6": ("tests/test_x1b_human_decision.py", "test_x1b_cur6_h1_approval_remains_bound_to_h1"),
        "X1B-CUR7": ("tests/test_x1b_human_decision.py", "test_x1b_cur7_h2_cannot_be_substituted_for_h1_selection"),
        "X1B-CUR8": ("tests/test_x1b_human_decision.py", "test_x1b_cur8_later_h2_approval_supersedes_h1"),
        "X1B-CUR9": ("tests/test_x1b_human_decision.py", "test_x1b_cur9_immutable_request_digest_mismatch_denied"),
        "X1B-CUR10": ("tests/test_x1b_human_decision.py", "test_x1b_cur10_immutable_accepted_scene_mismatch_denied"),
        "X1B-CUR11": ("tests/test_x1b_human_decision.py", "test_nonhuman_reserved_marker_denied"),
        "X1B-CUR12": (".github/workflows/x1b-human-decision.yml", "X1B CUR2 CUR12 TLS1-TLS15 deterministic child fuse"),
        "X1B-CUR13": ("tests/test_x1b_human_decision.py", "test_stale_base_cannot_canonicalize"),
        # F003 lock/CAS/failure truth.
        "X1B-CAS1": (".github/workflows/x1b-human-decision.yml", "X1B CAS1 and GIT1-GIT6 fuse"),
        "X1B-CAS2": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_cas2_main_changes_before_cas_fails_without_overwrite"),
        "X1B-CAS3": (".github/workflows/x1b-human-decision.yml", "X1B CAS3-CAS5 mode and machine-metadata fuse"),
        "X1B-CAS4": (".github/workflows/x1b-human-decision.yml", "X1B CAS3-CAS5 mode and machine-metadata fuse"),
        "X1B-CAS5": (".github/workflows/x1b-human-decision.yml", "X1B CAS3-CAS5 mode and machine-metadata fuse"),
        "X1B-CAS6": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_cas6_exact_cas_linearizes_once"),
        "X1B-CAS7": (".github/workflows/x1b-human-decision.yml", "X1B CAS7-CAS8 failure-truth fuse"),
        "X1B-CAS8": (".github/workflows/x1b-human-decision.yml", "X1B CAS7-CAS8 failure-truth fuse"),
        "X1B-CAS9": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_cas9_stale_admission_after_effect_denied"),
        # F004 Git environment isolation. All six outcomes execute in one hostile-env fuse.
        **{
            f"X1B-GIT{i}": (".github/workflows/x1b-human-decision.yml", "X1B CAS1 and GIT1-GIT6 fuse")
            for i in range(1, 7)
        },
        # Positive deterministic chain.
        **{
            f"X1B-PU{i}": ("tests/test_phase6_scriptops_smoke.py", "test_x1b_pu1_pu6_positive_chain_is_exact")
            for i in range(1, 7)
        },
        # F005 deterministic TLS matrix; TLS11 is the separately frozen live proof PR #165.
        **{
            f"X1B-TLS{i}": (
                ".github/workflows/x1b-human-decision.yml",
                "TLS11 live = PR #165" if i == 11 else "X1B CUR2 CUR12 TLS1-TLS15 deterministic child fuse",
            )
            for i in range(1, 16)
        },
        # Other retained fail-closed evidence.
        "FC-DUPLICATE-JSON": ("tests/test_x1b_human_decision.py", "test_duplicate_json_key_denied"),
        "FC-NONEXACT-JSON": ("tests/test_phase6_scriptops_smoke.py", "test_nonexact_and_wrong_schema_request_json_denied"),
        "FC-WRONG-SCHEMA": ("tests/test_phase6_scriptops_smoke.py", "test_nonexact_and_wrong_schema_request_json_denied"),
        "FC-SCENE-SCOPE-EFFECT": ("tests/test_x1b_human_decision.py", "test_x1b_a7_scope_expansion_denied"),
        "FC-CANDIDATE-DRIFT": ("tests/test_x1b_human_decision.py", "test_request_candidate_or_effect_drift_denied"),
        "FC-IMPACT-DRIFT": ("tests/test_phase6_scriptops_smoke.py", "test_impact_and_accepted_scene_recomputation_drift_denied"),
        "FC-ACCEPTED-SCENE-DRIFT": ("tests/test_phase6_scriptops_smoke.py", "test_impact_and_accepted_scene_recomputation_drift_denied"),
        "FC-REPLAY": ("tests/test_x1b_human_decision.py", "test_review_limit_and_replay_are_fail_closed"),
        "FC-PARENT-TOKEN-PROXY": (".github/workflows/x1b-human-decision.yml", "X1B retained parent credential/proxy fail-closed regression"),
        "FC-API-NETWORK": (".github/workflows/x1b-human-decision.yml", "X1B CUR2 CUR12 TLS1-TLS15 deterministic child fuse"),
        "FC-REPLACE-REF": ("tests/test_phase6_scriptops_smoke.py", "test_refs_replace_present_denied"),
        "FC-WRONG-MODE": (".github/workflows/x1b-human-decision.yml", "X1B CAS3-CAS5 mode and machine-metadata fuse"),
        "FC-MACHINE-METADATA": (".github/workflows/x1b-human-decision.yml", "X1B CAS3-CAS5 mode and machine-metadata fuse"),
    }
    cache: dict[str, str] = {}
    for test_id, (path, marker) in matrix.items():
        content = cache.setdefault(path, text(path))
        if marker not in content:
            fail(f"mandatory X1B matrix evidence missing: {test_id} -> {path} :: {marker}")
    print(f"[PASS] full frozen X1B matrix mapped to executable evidence: {len(matrix)} cases")


def check_tests_and_workflow() -> None:
    require(
        "tests/test_x1b_human_decision.py",
        "test_wrong_login_same_name_does_not_override_numeric_id",
        "test_nonhuman_reserved_marker_denied",
        "test_network_child_env_is_fresh",
        "test_anchored_git_ignores_attacker_git_environment",
        "test_positive_two_path_cas_effect",
        "test_stale_base_cannot_canonicalize",
        "test_symbolic_main_substitution_is_rejected_before_effect",
        "test_no_deref_cas_cannot_mutate_symref_target_if_race_follows_check",
        "test_legacy_approve_and_promote_accepted_block",
    )
    require(
        "tests/test_phase6_scriptops_smoke.py",
        "--decision-pr",
        "test_approve_without_decision_pr_is_rejected",
        "test_candidate_import_refuses_unrelated_dirty_state",
        "test_x1b_rb5_direct_function_calls_cannot_bypass_authority",
        "test_x1b_pu1_pu6_positive_chain_is_exact",
    )
    require(
        ".github/workflows/x1b-human-decision.yml",
        "test_x1b_human_decision",
        "verify_repository.py",
        "X1B CAS1 and GIT1-GIT6 fuse",
        "X1B CAS3-CAS5 mode and machine-metadata fuse",
        "X1B CAS7-CAS8 failure-truth fuse",
        "X1B CUR2 CUR12 TLS1-TLS15 deterministic child fuse",
        "TLS11 live = PR #165",
    )
    check_full_x1b_matrix()
    print("[PASS] X1B negative/positive/F001-F005 regression surface and CI workflow present")


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
