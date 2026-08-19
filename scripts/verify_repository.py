#!/usr/bin/env python3
"""Deterministyczna kontrola samowystarczalności repozytorium ScriptOps."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from restore_v2 import (
    CANONICAL_FILE,
    EXPECTED_SHA256,
    EXPECTED_SIZE,
    RestoreError,
    reconstruct_bytes,
    validate_content,
)

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PROJECT_STATE.md",
    "HANDOFF.md",
    "DECISION_LOG.md",
    "IDEA_ARCHIVE.md",
    "SOURCE_MANIFEST.md",
    "RECONSTRUCTION_REPORT.md",
    "SOURCE_AUDIT_SUMMARY.md",
    "CODEX_START.md",
    "continuity/COLD_START_AUDIT-001.md",
    "analysis/RC1_V2_GAP_2026-08-10.md",
    "evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md",
    "scripts/restore_v2.py",
    "legacy/scriptops-v2-single.py",
    "phase6/scriptops-v2-hardening.py",
    "tests/test_phase6_scriptops_smoke.py",
    ".github/workflows/phase6-scriptops-smoke.yml",
    ".github/pull_request_template.md",
    "sources/Decision_Summary_Current_State.md",
    "sources/ScriptOps_Main_Theme_Summary.md",
    "sources/RC1_SCOPE_LOCK.md",
    "sources/prototype/RESTORE.md",
]

PROTOTYPE_PARTS = [f"sources/prototype/scriptops-v2-single.py.part{i:02d}" for i in range(1, 8)]


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(relative_path: str) -> str:
    try:
        return (ROOT / relative_path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{relative_path} nie jest poprawnym UTF-8: {exc}")
    raise AssertionError("unreachable")


def require_markers(relative_path: str, markers: list[str]) -> None:
    text = read_text(relative_path)
    for marker in markers:
        if marker not in text:
            fail(f"{relative_path} nie zawiera wymaganego wpisu: {marker}")


def forbid_markers(relative_path: str, markers: list[str]) -> None:
    text = read_text(relative_path)
    for marker in markers:
        if marker in text:
            fail(f"{relative_path} nadal zawiera stale current-state marker: {marker}")


def check_required_files() -> None:
    missing = [p for p in REQUIRED_FILES + PROTOTYPE_PARTS if not (ROOT / p).is_file()]
    if missing:
        fail("brak wymaganych plików: " + ", ".join(missing))
    print(f"[PASS] wymagane pliki: {len(REQUIRED_FILES) + len(PROTOTYPE_PARTS)}")


def check_status_consistency() -> None:
    require_markers(
        "PROJECT_STATE.md",
        [
            "PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM / POST-SADDLE STATE RECONCILED",
            "legacy/scriptops-v2-single.py",
            "REWRITE: NO",
            "NEW CAPABILITY: NO",
            "Późniejsze `FUNCTIONAL_SADDLE_ACCEPTED` jest zaakceptowanym faktem repo Saddle",
            "evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md",
            "PR #7: `merged=true`",
        ],
    )
    require_markers(
        "README.md",
        [
            "PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM / POST-SADDLE STATE RECONCILED",
            "phase6/scriptops-v2-hardening.py",
            "PR #7 został zweryfikowany i scalony",
            "`MATURITY CLAIM`: **NONE**",
        ],
    )
    require_markers(
        "HANDOFF.md",
        [
            'activation: "BOUNDED PHASE 6 PROOF COMPLETE"',
            'blocker: "NO CURRENT LOCAL PRODUCT BLOCKER"',
            'next_step: "bounded_materially_different_evaluation_using_existing_phase6_mechanism"',
            'resume_contract: "REUSE V2 / NO REWRITE / NO NEW CAPABILITY / NO MATURITY CLAIM"',
            "DEC-SO-010",
            "PR #7 został zweryfikowany i scalony",
        ],
    )

    # Historical text may still name old gates, but startup/current-state language
    # must not present those already-closed gates as current blockers or next steps.
    forbid_markers(
        "PROJECT_STATE.md",
        [
            'status: "PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM / SADDLE LIVE MODEL EVIDENCE NEXT"',
            "FUNCTIONAL_SADDLE_ACCEPTED: NOT YET",
            "Po zielonym finalnym headzie i merge PR #7",
        ],
    )
    forbid_markers(
        "README.md",
        [
            "`FUNCTIONAL_SADDLE_ACCEPTED`: **NOT YET**",
            "Po merge Phase 6 wynik wraca do Saddle.",
            "Następnym brakującym dowodem jest live AI-worker benchmark/effect path",
        ],
    )
    forbid_markers(
        "HANDOFF.md",
        [
            'blocker: "FINAL PR HEAD MUST REMAIN GREEN BEFORE MERGE"',
            'next_step: "merge_phase6_then_return_to_saddle_live_model_evidence"',
            "`FUNCTIONAL_SADDLE_ACCEPTED`: `NOT YET`",
        ],
    )

    print("[PASS] current README/state/handoff są pogodzone po Phase 6 i późniejszym Saddle closure")


def check_decision_and_scope() -> None:
    decisions = read_text("DECISION_LOG.md")
    for marker in [
        "DEC-SO-001",
        "DEC-SO-009",
        "DEC-SO-010",
        "BASE: legacy/scriptops-v2-single.py",
        "REWRITE: NO",
        "NEW CAPABILITY: NO",
        "MATURITY CLAIM: NONE",
        "FUNCTIONAL_SADDLE_ACCEPTED: NOT YET",
    ]:
        if marker not in decisions:
            fail(f"DECISION_LOG.md nie zawiera historycznego wpisu: {marker}")

    scope = read_text("sources/RC1_SCOPE_LOCK.md")
    for phrase in [
        "browser helper",
        "direct API calls",
        "autonomous writing",
        "multi-user",
        "AI Guard",
        "Retcon Engine",
        "cloud sync",
    ]:
        if phrase not in scope:
            fail(f"RC1_SCOPE_LOCK.md nie zawiera wykluczenia: {phrase}")
    print("[PASS] historyczna decyzja bazowa i scope lock są zachowane bez relabelowania ich jako current")


def check_source_paths() -> None:
    state = read_text("PROJECT_STATE.md")
    manifest = read_text("SOURCE_MANIFEST.md")
    for reference in [
        "sources/Decision_Summary_Current_State.md",
        "sources/ScriptOps_Main_Theme_Summary.md",
        "sources/RC1_SCOPE_LOCK.md",
        "scripts/restore_v2.py",
        "RECONSTRUCTION_REPORT.md",
        "SOURCE_AUDIT_SUMMARY.md",
        "legacy/scriptops-v2-single.py",
        "analysis/RC1_V2_GAP_2026-08-10.md",
    ]:
        if reference not in state:
            fail(f"PROJECT_STATE.md nie wskazuje źródła: {reference}")
    for reference in ["legacy/scriptops-v2-single.py", "sources/RC1_SCOPE_LOCK.md"]:
        if reference not in manifest:
            fail(f"SOURCE_MANIFEST.md nie wskazuje aktywnego źródła: {reference}")
    print("[PASS] źródła bazowe i analiza B1–B5 są osiągalne")


def check_prototype() -> None:
    try:
        canonical = CANONICAL_FILE.read_bytes()
        canonical_sha = validate_content(canonical)
        reconstructed = reconstruct_bytes()
        reconstructed_sha = validate_content(reconstructed)
    except (OSError, RestoreError) as exc:
        fail(f"kontrola prototypu nie powiodła się: {exc}")

    if canonical != reconstructed:
        fail("historyczny v2 nie jest identyczny z częściami transportowymi")
    if canonical_sha != EXPECTED_SHA256 or reconstructed_sha != EXPECTED_SHA256:
        fail("historyczny v2 ma nieoczekiwaną sumę SHA-256")
    if len(canonical) != EXPECTED_SIZE:
        fail(f"rozmiar v2 niezgodny: expected={EXPECTED_SIZE}, actual={len(canonical)}")
    if hashlib.sha256(canonical).hexdigest() != EXPECTED_SHA256:
        fail("kanoniczny historyczny plik v2 ma niezgodną sumę")
    print(f"[PASS] historyczny v2 niezmieniony: {EXPECTED_SIZE} B, SHA-256 {canonical_sha}")


def check_phase6_proof_contract() -> None:
    hardening = read_text("phase6/scriptops-v2-hardening.py")
    test = read_text("tests/test_phase6_scriptops_smoke.py")
    evidence = read_text("evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md")
    for marker in [
        "LEGACY_PATH",
        "legacy = _load_legacy()",
        "checkpoint task",
        "record preflight",
        "record context",
        "record candidate input",
        "impact-report.json",
        "approve --why",
        "write_scene_file",
        '"why": why',
    ]:
        if marker not in hardening:
            fail(f"Phase-6 hardening nie zawiera: {marker}")
    for marker in [
        "test_full_controlled_happy_path",
        "test_approve_requires_explicit_why",
        "test_candidate_import_refuses_unrelated_dirty_state",
        "accepted scene hash must describe accepted content",
    ]:
        if marker not in test:
            fail(f"Phase-6 smoke nie zawiera: {marker}")
    for marker in [
        "CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM",
        "31421551632",
        "31421551982",
        "FUNCTIONAL_SADDLE_ACCEPTED",
    ]:
        if marker not in evidence:
            fail(f"Phase-6 evidence nie zawiera: {marker}")
    print("[PASS] bounded hardening B1–B5, smoke i historyczny evidence contract są obecne")


def check_ideas_and_filters() -> None:
    ideas = read_text("IDEA_ARCHIVE.md")
    if ideas.count("## IDEA-SO-") < 12:
        fail("IDEA_ARCHIVE.md nie zawiera pełnego zestawu zabezpieczonych kierunków")
    template = read_text(".github/pull_request_template.md")
    for marker in [
        "Problem / porażka",
        "Dlaczego obecny mechanizm nie wystarcza",
        "Obserwowalny dowód zaliczenia",
        "Dodany koszt utrzymania",
        "Poza zakresem",
        "Decyzja semantyczna",
    ]:
        if marker not in template:
            fail(f"szablon PR nie zawiera filtra: {marker}")
    print("[PASS] parking pomysłów i filtr PR są zachowane")


def check_continuity_audit() -> None:
    require_markers(
        "continuity/COLD_START_AUDIT-001.md",
        [
            "PUBLIC / NO PRIOR MEMORY / READ_ONLY",
            "PASS WITH FIXES",
            "Wznowienie ScriptOps — PASS",
            "scripts/restore_v2.py",
        ],
    )
    print("[PASS] historyczny cold-start evidence pozostaje osiągalny")


def main() -> None:
    check_required_files()
    check_status_consistency()
    check_decision_and_scope()
    check_source_paths()
    check_prototype()
    check_phase6_proof_contract()
    check_ideas_and_filters()
    check_continuity_audit()
    print("[PASS] repozytorium jest samowystarczalne po current-state reconciliation; Phase 6 proof pozostaje bez maturity promotion")


if __name__ == "__main__":
    main()
