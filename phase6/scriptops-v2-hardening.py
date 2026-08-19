#!/usr/bin/env python3
"""Phase-6 hardening shim for the canonical ScriptOps v2 prototype.

This is deliberately not a rewrite and does not add AI/model capability.
It loads ``legacy/scriptops-v2-single.py`` as the execution substrate and
closes only the five accepted Phase-6 blockers:

B1 durable task checkpoint before preflight;
B2 clean Git lifecycle for generated evidence/candidate input;
B3 accepted scene hash recalculated after status transition;
B4 mandatory human approval rationale;
B5 persisted impact report + deterministic smokeable path.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType

SOURCE_ROOT = Path(__file__).resolve().parents[1]
LEGACY_PATH = SOURCE_ROOT / "legacy" / "scriptops-v2-single.py"


def _load_legacy() -> ModuleType:
    spec = importlib.util.spec_from_file_location("scriptops_v2_legacy", LEGACY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load legacy ScriptOps: {LEGACY_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


legacy = _load_legacy()
ROOT = legacy.PROJECT_ROOT


class Phase6Error(RuntimeError):
    pass


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise Phase6Error(f"git {' '.join(args)} failed: {detail}")
    return result


def _dirty_paths() -> tuple[str, ...]:
    result = _git("status", "--porcelain=v1", "--untracked-files=all")
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return tuple(sorted(paths))


def _require_clean(label: str) -> None:
    dirty = _dirty_paths()
    if dirty:
        raise Phase6Error(f"{label}: working tree must be clean; dirty={list(dirty)}")


def _commit_paths(message: str, paths: list[Path]) -> None:
    rels: list[str] = []
    for path in paths:
        if not path.exists():
            raise Phase6Error(f"expected checkpoint artifact missing: {path}")
        rels.append(str(path.resolve().relative_to(ROOT)))
    _git("add", "--", *rels)
    staged = _git("diff", "--cached", "--quiet", check=False)
    if staged.returncode == 0:
        raise Phase6Error(f"checkpoint produced no staged change: {message}")
    if staged.returncode != 1:
        raise Phase6Error("cannot determine staged checkpoint state")
    _git("commit", "-m", message)
    _require_clean(message)


def _task_pack(task_id: str) -> dict:
    path = ROOT / "tasks" / task_id / "task-pack.yaml"
    if not path.exists():
        raise Phase6Error(f"task pack missing: {path}")
    value = legacy.yaml_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Phase6Error("task pack is not an object")
    return value


def cmd_review(args: argparse.Namespace) -> None:
    """B1: the task becomes a durable checkpoint before preflight."""
    _require_clean("review pre-state")
    before = set(_dirty_paths())
    legacy.cmd_review(args)
    changed = set(_dirty_paths()) - before
    packs = [ROOT / p for p in changed if p.startswith("tasks/") and p.endswith("/task-pack.yaml")]
    if len(changed) != 1 or len(packs) != 1:
        raise Phase6Error(f"review produced unexpected delta: {sorted(changed)}")
    task_id = packs[0].parent.name
    _commit_paths(f"scriptops phase6: checkpoint task {task_id}", packs)
    print(f"[PHASE6] Task checkpoint committed: {task_id}")


def cmd_check_pre(args: argparse.Namespace) -> None:
    """B2: generated preflight evidence is committed immediately."""
    _require_clean("check-pre pre-state")
    legacy.cmd_check_pre(args)
    task_dir = ROOT / "tasks" / args.task
    expected = [task_dir / "validation-report.json", task_dir / "prompt-ready.md"]
    dirty = set(_dirty_paths())
    expected_rel = {str(p.relative_to(ROOT)) for p in expected}
    if dirty != expected_rel:
        raise Phase6Error(f"check-pre produced unexpected delta: {sorted(dirty)}")
    _commit_paths(f"scriptops phase6: record preflight {args.task}", expected)
    print(f"[PHASE6] Preflight evidence committed: {args.task}")


def cmd_context_build(args: argparse.Namespace) -> None:
    """B2: context pack is an immutable Git checkpoint, not hidden dirt."""
    _require_clean("context-build pre-state")
    legacy.cmd_context_build(args)
    pack = ROOT / "tasks" / args.task / "context-pack.md"
    dirty = set(_dirty_paths())
    expected = {str(pack.relative_to(ROOT))}
    if dirty != expected:
        raise Phase6Error(f"context-build produced unexpected delta: {sorted(dirty)}")
    _commit_paths(f"scriptops phase6: record context {args.task}", [pack])
    print(f"[PHASE6] Context checkpoint committed: {args.task}")


def _checkpoint_candidate_input(task_id: str, source_name: str) -> Path:
    source = ROOT / "tasks" / task_id / source_name
    if not source.exists():
        raise Phase6Error(f"candidate input missing: {source}")
    dirty = set(_dirty_paths())
    source_rel = str(source.relative_to(ROOT))
    unexpected = dirty - {source_rel}
    if unexpected:
        raise Phase6Error(
            f"candidate import refuses unrelated dirty state: {sorted(unexpected)}"
        )
    if source_rel in dirty:
        _commit_paths(f"scriptops phase6: record candidate input {task_id}", [source])
    else:
        _require_clean("candidate input checkpoint")
    return source


def _latest_candidate(scene_id: str) -> Path:
    pattern = re.compile(
        rf"^{re.escape(scene_id)}-v([1-9][0-9]*)-candidate\.fountain$"
    )
    candidates: list[tuple[int, Path]] = []
    staging = ROOT / "staging" / "scenes"
    if staging.is_dir():
        for candidate in staging.iterdir():
            match = pattern.fullmatch(candidate.name)
            if match is not None and candidate.is_file() and not candidate.is_symlink():
                candidates.append((int(match.group(1)), candidate))
    if not candidates:
        raise Phase6Error(f"no staged candidate for {scene_id}")
    return max(candidates, key=lambda item: item[0])[1]


def _write_impact_report(task_id: str, source: Path) -> Path:
    pack = _task_pack(task_id)
    scene_id = str(pack.get("scene_id", ""))
    if not scene_id:
        raise Phase6Error("task pack has no scene_id")
    candidate = _latest_candidate(scene_id)
    report = ROOT / "tasks" / task_id / "validation-report.json"
    if not report.exists():
        raise Phase6Error("post-validation report missing")
    fm, _ = legacy.parse_front_matter(candidate)
    impact = {
        "schema_version": "scriptops-phase6-impact/0.1",
        "task_id": task_id,
        "scene_id": scene_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "REVIEW_REQUIRED",
        "candidate": {
            "path": str(candidate.relative_to(ROOT)),
            "file_sha256": legacy.compute_sha256(candidate.read_text(encoding="utf-8")),
            "declared_scene_hash": fm.get("hash"),
            "source_path": str(source.relative_to(ROOT)),
            "source_sha256": legacy.compute_sha256(source.read_text(encoding="utf-8")),
        },
        "proposed_effect": {
            "action": "ACCEPT_SCENE_CANDIDATE",
            "target": f"scenes/{scene_id}.fountain",
            "canonical_target_changed": False,
        },
        "validation": {
            "path": str(report.relative_to(ROOT)),
            "sha256": legacy.compute_sha256(report.read_text(encoding="utf-8")),
        },
        "impact": [
            "candidate is staged as a proposal artifact",
            "canonical scene remains unchanged until explicit human approve --why",
            "approval will create/update only the canonical scene and decision log",
        ],
        "requires_human_decision": True,
    }
    path = ROOT / "tasks" / task_id / "impact-report.json"
    path.write_text(json.dumps(impact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _commit_paths(f"scriptops phase6: record impact {task_id}", [path])
    return path


def cmd_check_post(args: argparse.Namespace) -> None:
    """B2+B5: checkpoint candidate input, validate/stage, then persist impact."""
    source_name = args.source or "webai-output.md"
    source = _checkpoint_candidate_input(args.task, source_name)
    _require_clean("check-post pre-state")
    legacy.cmd_check_post(args)
    _require_clean("legacy check-post post-state")
    impact = _write_impact_report(args.task, source)
    print(f"[PHASE6] Impact report committed: {impact}")


def _impact_for_candidate(scene_id: str, candidate: Path) -> tuple[Path, dict]:
    candidate_sha = legacy.compute_sha256(candidate.read_text(encoding="utf-8"))
    matches: list[tuple[Path, dict]] = []
    for path in (ROOT / "tasks").glob("*/impact-report.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (
            data.get("scene_id") == scene_id
            and data.get("candidate", {}).get("file_sha256") == candidate_sha
            and data.get("status") == "REVIEW_REQUIRED"
        ):
            matches.append((path, data))
    if not matches:
        raise Phase6Error("no exact REVIEW_REQUIRED impact report for candidate")
    return sorted(matches, key=lambda item: str(item[0]))[-1]


def cmd_approve(args: argparse.Namespace) -> None:
    """B3+B4: human rationale precedes canonical write; accepted hash is fresh."""
    _require_clean("approve pre-state")
    why = args.why.strip()
    if not why:
        raise Phase6Error("approve --why must be non-empty")

    scene_id = args.scene
    candidate = _latest_candidate(scene_id)
    impact_path, impact = _impact_for_candidate(scene_id, candidate)
    fm, body = legacy.parse_front_matter(candidate)
    if fm.get("status") != "candidate":
        raise Phase6Error("only candidate status can be approved")

    # The proposal artifact already exists, but the canonical effect does not.
    # Human approval happens before writing the canonical target.
    fm["status"] = "accepted"
    target = ROOT / "scenes" / f"{scene_id}.fountain"
    accepted_scene_hash = legacy.write_scene_file(target, fm, body)
    accepted_text = target.read_text(encoding="utf-8")

    decision = {
        "id": f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scope": [scene_id],
        "status": "active",
        "type": "scene_accepted",
        "approver": "human",
        "why": why,
        "task_id": impact.get("task_id"),
        "impact_report": str(impact_path.relative_to(ROOT)),
        "candidate_file_sha256": impact["candidate"]["file_sha256"],
        "scene_hash": accepted_scene_hash,
        "artifact_hash": legacy.compute_sha256(accepted_text),
        "scene_version": fm.get("version", 1),
    }
    log_path = legacy.SCRIPTOPS_DIR / "decision-log.ndjson"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(decision, ensure_ascii=False) + "\n")

    _commit_paths(f"scriptops phase6: accept {scene_id}", [target, log_path])
    print(f"Accepted: {target}")
    print(f"[PHASE6] accepted scene hash: {accepted_scene_hash}")
    print("[PHASE6] evidence: canonical effect committed after explicit human rationale")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ScriptOps v2 Phase-6 hardening shim (reuse, no rewrite)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    review = sub.add_parser("review")
    review.add_argument("--scene", required=True)

    pre = sub.add_parser("check-pre")
    pre.add_argument("--task", required=True)
    pre.add_argument("--max-tokens", type=int, default=14000)

    ctx = sub.add_parser("context-build")
    ctx.add_argument("--scene", required=True)
    ctx.add_argument("--mode", required=True)
    ctx.add_argument("--task", required=True)
    ctx.add_argument("--target", choices=["file", "clipboard"], default="file")

    post = sub.add_parser("check-post")
    post.add_argument("--task", required=True)
    post.add_argument("--source", default=None)

    approve = sub.add_parser("approve")
    approve.add_argument("--scene", required=True)
    approve.add_argument("--why", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    command = args.command.replace("-", "_")
    try:
        globals()[f"cmd_{command}"](args)
        return 0
    except Phase6Error as exc:
        print(f"PHASE6 BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
