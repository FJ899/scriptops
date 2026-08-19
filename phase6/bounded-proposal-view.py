#!/usr/bin/env python3
"""Explicit task-bounded proposal view for cross-scene ScriptOps context.

This module is intentionally narrow. It does not change canonical scene state,
does not make staging globally outrank canon, and does not add atomic approval.
A downstream task may bind an exact validated staged candidate by path + SHA256.
Only that task's context build sees the bound proposal; all unbound scenes keep
the existing canonical-first resolution behavior.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path
from types import ModuleType

SOURCE_ROOT = Path(__file__).resolve().parents[1]
HARDENING_PATH = SOURCE_ROOT / "phase6" / "scriptops-v2-hardening.py"


def _load_hardening() -> ModuleType:
    spec = importlib.util.spec_from_file_location("scriptops_phase6_hardening", HARDENING_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Phase-6 hardening: {HARDENING_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hardening = _load_hardening()
legacy = hardening.legacy
ROOT = hardening.ROOT
Phase6Error = hardening.Phase6Error

_SCENE_ID = re.compile(r"^SCN-[0-9]{3,}$")
_FILE_SHA = re.compile(r"^sha256:[a-f0-9]{64}$")


def _task_path(task_id: str) -> Path:
    return ROOT / "tasks" / task_id / "task-pack.yaml"


def _task_pack(task_id: str) -> dict:
    return hardening._task_pack(task_id)


def _candidate_path(raw_path: str) -> Path:
    rel = Path(raw_path)
    if rel.is_absolute():
        raise Phase6Error("proposal binding candidate path must be repository-relative")

    lexical = ROOT / rel
    if lexical.is_symlink():
        raise Phase6Error("proposal binding candidate must not be a symlink")

    candidate = lexical.resolve()
    staging = (ROOT / "staging" / "scenes").resolve()
    try:
        candidate.relative_to(staging)
    except ValueError as exc:
        raise Phase6Error("proposal binding candidate must remain under staging/scenes") from exc

    if not candidate.is_file():
        raise Phase6Error(f"proposal binding candidate missing or not a regular file: {raw_path}")
    if os.stat(candidate).st_nlink != 1:
        raise Phase6Error("proposal binding candidate must be a single-hardlink regular file")
    return candidate


def _validate_candidate(scene_id: str, raw_path: str, expected_sha: str | None) -> dict:
    if not _SCENE_ID.fullmatch(scene_id):
        raise Phase6Error(f"invalid proposal binding scene id: {scene_id}")

    candidate = _candidate_path(raw_path)
    pattern = re.compile(rf"^{re.escape(scene_id)}-v([1-9][0-9]*)-candidate\.fountain$")
    if pattern.fullmatch(candidate.name) is None:
        raise Phase6Error(
            f"proposal binding filename does not identify exact {scene_id} candidate: {candidate.name}"
        )

    fm, _ = legacy.parse_front_matter(candidate)
    if fm.get("scene_id") != scene_id:
        raise Phase6Error("proposal binding scene_id does not match candidate front matter")
    if fm.get("status") != "candidate":
        raise Phase6Error("proposal binding may reference only status=candidate")

    actual_sha = legacy.compute_sha256(candidate.read_text(encoding="utf-8"))
    if expected_sha is not None:
        if not _FILE_SHA.fullmatch(expected_sha):
            raise Phase6Error("proposal binding file_sha256 is malformed")
        if actual_sha != expected_sha:
            raise Phase6Error(
                f"proposal binding SHA mismatch: expected={expected_sha}, actual={actual_sha}"
            )

    impact_path, impact = hardening._impact_for_candidate(scene_id, candidate)
    impact_candidate = impact.get("candidate", {})
    expected_rel = str(candidate.relative_to(ROOT))
    if impact_candidate.get("path") != expected_rel:
        raise Phase6Error("exact REVIEW_REQUIRED impact report path does not match bound candidate")
    if impact_candidate.get("file_sha256") != actual_sha:
        raise Phase6Error("exact REVIEW_REQUIRED impact report hash does not match bound candidate")

    return {
        "scene_id": scene_id,
        "path": expected_rel,
        "file_sha256": actual_sha,
        "candidate": candidate,
        "impact_report": str(impact_path.relative_to(ROOT)),
    }


def _target_relations(task_scene: str) -> set[str]:
    target = ROOT / "scenes" / f"{task_scene}.fountain"
    if not target.exists() or target.is_symlink() or not target.is_file():
        raise Phase6Error("bounded proposal view requires an accepted canonical target scene")
    fm, _ = legacy.parse_front_matter(target)
    return set(fm.get("depends_on", [])) | set(fm.get("spoils_or_sets_up", []))


def _require_adjacent(task_scene: str, bound_scene: str) -> None:
    if bound_scene == task_scene:
        raise Phase6Error("bounded proposal view is cross-scene only; target scene cannot bind itself")
    if bound_scene not in _target_relations(task_scene):
        raise Phase6Error(
            f"proposal binding {bound_scene} is not graph-adjacent to task target {task_scene}"
        )


def _validated_bindings(task_id: str, *, require_nonempty: bool) -> dict[str, dict]:
    pack = _task_pack(task_id)
    task_scene = str(pack.get("scene_id", ""))
    if not _SCENE_ID.fullmatch(task_scene):
        raise Phase6Error("task pack has invalid or missing scene_id")

    raw = pack.get("proposal_bindings", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise Phase6Error("proposal_bindings must be an object keyed by scene_id")
    if require_nonempty and not raw:
        raise Phase6Error("bounded proposal view requires at least one explicit proposal binding")

    validated: dict[str, dict] = {}
    for scene_id, spec in raw.items():
        scene_id = str(scene_id)
        if not isinstance(spec, dict):
            raise Phase6Error(f"proposal binding {scene_id} must be an object")
        if set(spec) != {"path", "file_sha256"}:
            raise Phase6Error(
                f"proposal binding {scene_id} must contain exactly path + file_sha256"
            )
        _require_adjacent(task_scene, scene_id)
        validated[scene_id] = _validate_candidate(
            scene_id,
            str(spec.get("path", "")),
            str(spec.get("file_sha256", "")),
        )
    return validated


def cmd_bind(args: argparse.Namespace) -> None:
    """Persist one exact proposal identity into an existing downstream task pack."""
    hardening._require_clean("proposal-bind pre-state")
    pack = _task_pack(args.task)
    task_scene = str(pack.get("scene_id", ""))
    _require_adjacent(task_scene, args.scene)
    record = _validate_candidate(args.scene, args.candidate, expected_sha=None)

    bindings = pack.get("proposal_bindings", {}) or {}
    if not isinstance(bindings, dict):
        raise Phase6Error("proposal_bindings must be an object keyed by scene_id")

    desired = {
        "path": record["path"],
        "file_sha256": record["file_sha256"],
    }
    existing = bindings.get(args.scene)
    if existing is not None and existing != desired:
        raise Phase6Error(
            f"task already binds {args.scene} to a different proposal; create a new task instead"
        )
    if existing == desired:
        print(f"[PROPOSAL VIEW] Exact binding already present: {args.scene}")
        return

    bindings[args.scene] = desired
    pack["proposal_bindings"] = bindings
    path = _task_path(args.task)
    path.write_text(legacy.yaml_dump(pack, sort_keys=False), encoding="utf-8")
    hardening._commit_paths(
        f"scriptops phase6: bind proposal {args.scene} to {args.task}",
        [path],
    )
    print(
        f"[PROPOSAL VIEW] Bound {args.scene} -> {record['path']} @ {record['file_sha256']}"
    )
    print("[PROPOSAL VIEW] Binding is task-local proposal context, not canonical acceptance")


class BoundedProposalContextBuilder(legacy.ContextBuilder):
    def __init__(self, project_root: Path, bindings: dict[str, dict]):
        self._proposal_bindings = bindings
        super().__init__(project_root)

    def _load_scene_card(self, scene_id):
        binding = self._proposal_bindings.get(scene_id)
        if binding is None:
            return super()._load_scene_card(scene_id)
        fm, body = legacy.parse_front_matter(binding["candidate"])
        fm["_body"] = body.strip()
        return fm


def _annotate_context_pack(pack_path: Path, bindings: dict[str, dict]) -> None:
    text = pack_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise Phase6Error("generated context pack has invalid front matter")

    header = legacy.yaml_load(parts[1])
    if not isinstance(header, dict):
        raise Phase6Error("generated context pack header is not an object")

    lines = [
        "This is a TASK-BOUNDED PROPOSAL VIEW, not canonical state.",
        "Only the exact bindings below override canonical scene resolution for this context build.",
        "All unbound scenes retain the existing canonical-first resolution behavior.",
        "A binding does not approve, merge, or mutate any canonical scene.",
        "",
    ]
    view_records = []
    for scene_id in sorted(bindings):
        record = bindings[scene_id]
        lines.append(
            f"- {scene_id}: {record['path']} @ {record['file_sha256']} "
            f"(impact: {record['impact_report']})"
        )
        view_records.append(
            {
                "scene_id": scene_id,
                "path": record["path"],
                "file_sha256": record["file_sha256"],
                "impact_report": record["impact_report"],
                "semantic_status": "PROPOSAL_NOT_CANON",
            }
        )

    view_text = "\n".join(lines)
    added_tokens = legacy.estimate_tokens(view_text)
    audit = header.get("token_audit", {})
    budget = int(audit.get("budget", 0))
    used = int(audit.get("used", 0)) + added_tokens
    if budget and used > budget:
        raise Phase6Error(f"bounded proposal annotation exceeds context budget: {used}/{budget}")
    if budget:
        audit["used"] = used
        audit["reserve"] = budget - used
        audit["status"] = "ok"
        header["token_audit"] = audit

    sources = header.get("included_sources", [])
    if not isinstance(sources, list):
        raise Phase6Error("context pack included_sources must be a list")
    sources.append(
        {
            "id": "BOUNDED-PROPOSAL-VIEW",
            "hash": legacy.compute_sha256(view_text),
            "type": "instruction",
            "included_tokens": added_tokens,
        }
    )
    header["included_sources"] = sources
    header["proposal_view"] = {
        "status": "BOUNDED_NONCANONICAL",
        "bindings": view_records,
    }

    existing_body = parts[2].lstrip("\n")
    full = (
        "---\n"
        + legacy.yaml_dump(header, sort_keys=False)
        + "---\n\n# BOUNDED PROPOSAL VIEW\n\n"
        + view_text
        + "\n\n---\n\n"
        + existing_body
    )
    pack_path.write_text(full, encoding="utf-8")


def cmd_context_build(args: argparse.Namespace) -> None:
    """Build one context pack against exact task-bound proposal identities."""
    hardening._require_clean("bounded context-build pre-state")
    pack = _task_pack(args.task)
    task_scene = str(pack.get("scene_id", ""))
    if task_scene != args.scene:
        raise Phase6Error(
            f"task target mismatch: task scene={task_scene}, requested scene={args.scene}"
        )

    bindings = _validated_bindings(args.task, require_nonempty=True)
    builder = BoundedProposalContextBuilder(ROOT, bindings)
    pack_path = builder.build(args.scene, args.mode, args.task)
    _annotate_context_pack(pack_path, bindings)

    dirty = set(hardening._dirty_paths())
    expected = {str(pack_path.relative_to(ROOT))}
    if dirty != expected:
        raise Phase6Error(f"bounded context-build produced unexpected delta: {sorted(dirty)}")
    hardening._commit_paths(
        f"scriptops phase6: record bounded proposal context {args.task}",
        [pack_path],
    )
    print(f"[PROPOSAL VIEW] Context checkpoint committed: {args.task}")
    print("[PROPOSAL VIEW] Canonical scenes were not modified")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ScriptOps Phase-6 explicit bounded proposal view"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    bind = sub.add_parser("bind")
    bind.add_argument("--task", required=True)
    bind.add_argument("--scene", required=True)
    bind.add_argument("--candidate", required=True)

    context = sub.add_parser("context-build")
    context.add_argument("--scene", required=True)
    context.add_argument("--mode", required=True)
    context.add_argument("--task", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "bind":
            cmd_bind(args)
        elif args.command == "context-build":
            cmd_context_build(args)
        else:
            raise Phase6Error(f"unsupported command: {args.command}")
        return 0
    except (Phase6Error, legacy.ContextBudgetError, FileNotFoundError, ValueError) as exc:
        print(f"PROPOSAL VIEW BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
