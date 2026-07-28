#!/usr/bin/env python3
"""Deterministyczna kontrola samowystarczalności repozytorium ScriptOps."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROTOTYPE_SHA256 = "881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596"

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
    missing = [path for path in REQUIRED_FILES + PROTOTYPE_PARTS if not (ROOT / path).is_file()]
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
    print("[PASS] statusy są spójne")


def reconstruct_prototype() -> bytes:
    return b"".join((ROOT / path).read_bytes() for path in PROTOTYPE_PARTS)


def check_prototype() -> None:
    content = reconstruct_prototype()
    actual = hashlib.sha256(content).hexdigest()
    if actual != EXPECTED_PROTOTYPE_SHA256:
        fail(
            "suma prototypu v2 jest niezgodna: "
            f"expected={EXPECTED_PROTOTYPE_SHA256}, actual={actual}"
        )

    try:
        compile(content.decode("utf-8"), "scriptops-v2-single.py", "exec")
    except (UnicodeDecodeError, SyntaxError) as exc:
        fail(f"odtworzony prototyp nie jest poprawnym kodem Python: {exc}")

    print(f"[PASS] prototyp v2: SHA-256 {actual} i poprawna składnia")


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


def main() -> None:
    check_required_files()
    check_status_consistency()
    check_prototype()
    check_scope_and_ideas()
    print("[PASS] repozytorium jest samowystarczalne na obecnym etapie")


if __name__ == "__main__":
    main()
