#!/usr/bin/env python3
"""Deterministyczna kontrola samowystarczalności repozytorium ScriptOps."""

from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

from restore_v2 import EXPECTED_SHA256, RestoreError, restore_to_path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROTOTYPE_SIZE = 51980

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
    "scripts/restore_v2.py",
    "sources/Decision_Summary_Current_State.md",
    "sources/ScriptOps_Main_Theme_Summary.md",
    "sources/RC1_SCOPE_LOCK.md",
    "sources/prototype/RESTORE.md",
]

PROTOTYPE_PARTS = [
    f"sources/prototype/scriptops-v2-single.py.part{i:02d}" for i in range(1, 8)
]


def fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{relative_path} nie jest poprawnym UTF-8: {exc}")
    raise AssertionError("unreachable")


def check_required_files() -> None:
    missing = [
        path
        for path in REQUIRED_FILES + PROTOTYPE_PARTS
        if not (ROOT / path).is_file()
    ]
    if missing:
        fail("brak wymaganych plików: " + ", ".join(missing))
    print(f"[PASS] wymagane pliki: {len(REQUIRED_FILES) + len(PROTOTYPE_PARTS)}")


def check_status_consistency() -> None:
    expected = "NOT ACTIVATED / SOURCE OF TRUTH ACTIVE / ACCESS CHECK REQUIRED"
    project_state = read_text("PROJECT_STATE.md")
    readme = read_text("README.md")
    handoff = read_text("HANDOFF.md")

    if expected not in project_state:
        fail("PROJECT_STATE.md nie zawiera kanonicznego statusu")
    if "SOURCE OF TRUTH ACTIVE / ACCESS CHECK REQUIRED" not in readme:
        fail("README.md ma niespójny status")
    if "ACCESS CHECK REQUIRED" not in handoff:
        fail("HANDOFF.md nie zachowuje aktywnej blokady")
    if "Prywatne repozytorium" in readme:
        fail("README.md utrwala zmienną właściwość widoczności repozytorium")
    print("[PASS] statusy i opis repo są spójne")


def check_source_paths() -> None:
    project_state = read_text("PROJECT_STATE.md")
    source_manifest = read_text("SOURCE_MANIFEST.md")

    required_references = [
        "sources/Decision_Summary_Current_State.md",
        "sources/ScriptOps_Main_Theme_Summary.md",
        "sources/RC1_SCOPE_LOCK.md",
        "scripts/restore_v2.py",
        "RECONSTRUCTION_REPORT.md",
        "SOURCE_AUDIT_SUMMARY.md",
    ]
    for reference in required_references:
        if reference not in project_state:
            fail(f"PROJECT_STATE.md nie wskazuje aktywnego źródła: {reference}")
        if reference.endswith(".md") and not (ROOT / reference).is_file():
            fail(f"wskazane źródło nie istnieje: {reference}")

    if "Historyczne ścieżki pochodzenia" not in project_state:
        fail("PROJECT_STATE.md nie odróżnia historycznych ścieżek od aktywnych")
    if "Aktywne, odczytywalne kopie" not in source_manifest:
        fail("SOURCE_MANIFEST.md nie wyjaśnia mapowania historycznych ścieżek")
    print("[PASS] aktywne źródła i historyczne pochodzenie są rozdzielone")


def check_prototype_restore() -> None:
    try:
        with tempfile.TemporaryDirectory(prefix="scriptops-v2-") as temp_dir:
            output = Path(temp_dir) / "scriptops-v2-single.py"
            actual_sha = restore_to_path(output)
            content = output.read_bytes()
    except (OSError, RestoreError) as exc:
        fail(f"automatyczne odtworzenie prototypu nie powiodło się: {exc}")

    if actual_sha != EXPECTED_SHA256:
        fail(
            "suma prototypu v2 jest niezgodna: "
            f"expected={EXPECTED_SHA256}, actual={actual_sha}"
        )
    if len(content) != EXPECTED_PROTOTYPE_SIZE:
        fail(
            "rozmiar prototypu v2 jest niezgodny: "
            f"expected={EXPECTED_PROTOTYPE_SIZE}, actual={len(content)}"
        )
    if hashlib.sha256(content).hexdigest() != EXPECTED_SHA256:
        fail("plik zapisany przez restore_v2.py ma niezgodną sumę")

    print(
        f"[PASS] prototyp v2 odtworzony: {EXPECTED_PROTOTYPE_SIZE} B, "
        f"SHA-256 {actual_sha} i poprawna składnia"
    )


def check_scope_and_ideas() -> None:
    scope = read_text("sources/RC1_SCOPE_LOCK.md")
    ideas = read_text("IDEA_ARCHIVE.md")
    decisions = read_text("DECISION_LOG.md")
    codex = read_text("CODEX_START.md")

    required_exclusions = [
        "browser helper",
        "direct API calls",
        "autonomous writing",
        "multi-user",
        "AI Guard",
        "Retcon Engine",
        "cloud sync",
    ]
    for phrase in required_exclusions:
        if phrase not in scope:
            fail(f"RC1_SCOPE_LOCK.md nie zawiera wykluczenia: {phrase}")

    if ideas.count("## IDEA-SO-") < 12:
        fail("IDEA_ARCHIVE.md nie zawiera pełnego zestawu zabezpieczonych kierunków")
    if "DEC-SO-008" not in decisions:
        fail("DECISION_LOG.md nie zapisuje braku aktywacji projektu")
    if "PLAN FIRST / NO IMPLEMENTATION WITHOUT APPROVAL" not in codex:
        fail("CODEX_START.md nie wymusza etapu planowania")

    print("[PASS] zakres, decyzje i pomysły są zabezpieczone")


def check_continuity_audit() -> None:
    audit = read_text("continuity/COLD_START_AUDIT-001.md")
    required_markers = [
        "PUBLIC / NO PRIOR MEMORY / READ_ONLY",
        "PASS WITH FIXES",
        "Wznowienie ScriptOps — PASS",
        "GAP-001 — BPM:160",
        "scripts/restore_v2.py",
    ]
    for marker in required_markers:
        if marker not in audit:
            fail(f"audyt ciągłości nie zawiera wymaganego wpisu: {marker}")
    print("[PASS] wynik niezależnego testu ciągłości jest zapisany")


def main() -> None:
    check_required_files()
    check_status_consistency()
    check_source_paths()
    check_prototype_restore()
    check_scope_and_ideas()
    check_continuity_audit()
    print("[PASS] repozytorium jest samowystarczalne na obecnym etapie")


if __name__ == "__main__":
    main()
