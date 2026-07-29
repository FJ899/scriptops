#!/usr/bin/env python3
"""Odtwarza i weryfikuje historyczny prototyp ScriptOps v2."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = "881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596"
PARTS = [
    ROOT / f"sources/prototype/scriptops-v2-single.py.part{i:02d}"
    for i in range(1, 8)
]
DEFAULT_OUTPUT = ROOT / "scriptops-v2-single.py"


class RestoreError(RuntimeError):
    """Błąd integralności lub odtworzenia prototypu."""


def reconstruct_bytes() -> bytes:
    missing = [str(path.relative_to(ROOT)) for path in PARTS if not path.is_file()]
    if missing:
        raise RestoreError("Brak części prototypu: " + ", ".join(missing))
    return b"".join(path.read_bytes() for path in PARTS)


def validate_content(content: bytes) -> str:
    actual_sha = hashlib.sha256(content).hexdigest()
    if actual_sha != EXPECTED_SHA256:
        raise RestoreError(
            "Niezgodna suma SHA-256: "
            f"expected={EXPECTED_SHA256}, actual={actual_sha}"
        )

    try:
        source = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RestoreError(f"Prototyp nie jest poprawnym UTF-8: {exc}") from exc

    try:
        compile(source, "scriptops-v2-single.py", "exec")
    except SyntaxError as exc:
        raise RestoreError(f"Prototyp nie jest poprawnym kodem Python: {exc}") from exc

    return actual_sha


def restore_to_path(output: Path, *, overwrite: bool = False) -> str:
    content = reconstruct_bytes()
    actual_sha = validate_content(content)

    if output.exists() and not overwrite:
        existing = output.read_bytes()
        if existing == content:
            return actual_sha
        raise RestoreError(
            f"Plik {output} już istnieje i ma inną treść. Użyj --force, aby go zastąpić."
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    return actual_sha


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Odtwórz pełny scriptops-v2-single.py z siedmiu części i sprawdź integralność."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Ścieżka pliku wynikowego (domyślnie: ./scriptops-v2-single.py).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Sprawdź części, SHA-256 i składnię bez zapisywania pliku.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Zastąp istniejący plik wynikowy.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        content = reconstruct_bytes()
        actual_sha = validate_content(content)
        if args.check_only:
            print(f"[PASS] prototyp v2: SHA-256 {actual_sha}, poprawny UTF-8 i składnia Python")
            return 0

        output = args.output
        if not output.is_absolute():
            output = (Path.cwd() / output).resolve()
        restore_to_path(output, overwrite=args.force)
        print(f"[PASS] odtworzono {output}")
        print(f"[PASS] SHA-256 {actual_sha}")
        return 0
    except (OSError, RestoreError) as exc:
        print(f"[FAIL] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
