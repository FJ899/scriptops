#!/usr/bin/env python3
"""Safe ScriptOps v2 compatibility shim.

The historical 2026-08 prototype is preserved only under ``sources/prototype``.
This active legacy-path module keeps the pre-approval commands needed by the
Phase-6 shim, but it cannot create ``accepted`` state. Canonical acceptance is
owned exclusively by ``phase6/x1b_human_decision.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(".").resolve()
SCRIPTOPS_DIR = PROJECT_ROOT / ".scriptops"
CONFIG_PATH = SCRIPTOPS_DIR / "config.yaml"

DEFAULT_CONFIG = """project:
  name: ScriptOps Project
  version: "2.0-x1b"
  source_of_truth: git
state_machine:
  allowed_transitions:
    idea: [outline, question]
    question: [idea, outline]
    outline: [draft]
    draft: [candidate]
    candidate: [rejected, revision_requested]
    revision_requested: [draft]
    accepted: [archived]
    rejected: [draft, idea]
    archived: []
continuity:
  auto_compile: false
"""


class LegacyApprovalDisabled(RuntimeError):
    """Raised before any legacy accepted-state mutation."""


def yaml_load(text: str) -> Any:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for active ScriptOps") from exc
    return yaml.safe_load(text)


def yaml_dump(obj: Any, sort_keys: bool = False) -> str:
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for active ScriptOps") from exc
    return yaml.dump(
        obj,
        sort_keys=sort_keys,
        allow_unicode=True,
        default_flow_style=False,
    )


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        value = yaml_load(CONFIG_PATH.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    value = yaml_load(DEFAULT_CONFIG)
    return value if isinstance(value, dict) else {}


def compute_sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) != 3:
        return {}, text
    value = yaml_load(parts[1])
    return (value if isinstance(value, dict) else {}), parts[2]


def write_scene_file(path: Path, fm: dict[str, Any], body: str) -> str:
    """Serialize non-authority scene bytes; caller remains responsible for policy."""
    fm_copy = dict(fm)
    fm_copy.pop("hash", None)
    canonical = yaml_dump(fm_copy, sort_keys=False) + body
    fm["hash"] = compute_sha256(canonical)
    text = "---\n" + yaml_dump(fm, sort_keys=False) + "---" + body
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(fm["hash"])


def _run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and cp.returncode:
        detail = cp.stderr.strip() or cp.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return cp


def git_is_clean() -> bool:
    return _run_git("status", "--porcelain", check=False).stdout.strip() == ""


def ensure_git_clean() -> None:
    if not git_is_clean():
        raise RuntimeError("Git working tree is dirty")


def _commit(message: str, *paths: Path) -> None:
    rels = [str(path.resolve().relative_to(PROJECT_ROOT)) for path in paths]
    _run_git("add", "--", *rels)
    _run_git("commit", "-m", message)


def cmd_init(args: argparse.Namespace) -> None:
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    for directory in (
        SCRIPTOPS_DIR,
        PROJECT_ROOT / "bible",
        PROJECT_ROOT / "outline",
        PROJECT_ROOT / "scenes",
        PROJECT_ROOT / "staging" / "scenes",
        PROJECT_ROOT / "summaries",
        PROJECT_ROOT / "tasks",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(DEFAULT_CONFIG, encoding="utf-8")
    if not (PROJECT_ROOT / ".git").exists():
        subprocess.run(["git", "init"], cwd=PROJECT_ROOT, capture_output=True, check=True)
    _run_git("add", ".")
    staged = _run_git("diff", "--cached", "--quiet", check=False)
    if staged.returncode == 1:
        _run_git("commit", "-m", "scriptops v2 x1b: init project")
    print(f"Initialized ScriptOps v2 project: {args.name}")


def cmd_check(args: argparse.Namespace) -> None:
    ensure_git_clean()
    print("[OK] Git working tree clean.")
    print("[OK] X1B active compatibility shim loaded.")


def cmd_scene_new(args: argparse.Namespace) -> None:
    ensure_git_clean()
    scene_id = args.id
    if not re.fullmatch(r"SCN-[0-9]{3,}", scene_id):
        raise RuntimeError("invalid scene id")
    path = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"
    if path.exists():
        raise RuntimeError(f"scene already exists: {scene_id}")
    fm = {
        "scene_id": scene_id,
        "version": 1,
        "status": "idea",
        "hash": "PLACEHOLDER",
        "title": "",
        "act": 1,
        "sequence": "",
        "location": "",
        "time": "",
        "characters": [],
        "purpose": [],
        "emotional_turn": {"from": "", "to": ""},
        "depends_on": [],
        "spoils_or_sets_up": [],
        "continuity_constraints": [],
        "tags": [],
    }
    write_scene_file(path, fm, "\nINT. LOCATION - TIME\n\n# Scene body in Fountain format\n")
    _commit(f"scriptops: create idea {scene_id}", path)
    print(f"Created idea: {path}")


def cmd_scene_promote(args: argparse.Namespace) -> None:
    ensure_git_clean()
    scene_id = args.id
    target_status = args.to
    if target_status == "accepted":
        raise LegacyApprovalDisabled(
            "legacy scene-promote --to accepted is disabled; use Phase6 approve --decision-pr"
        )
    scene_path = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"
    if not scene_path.exists():
        staged = sorted((PROJECT_ROOT / "staging" / "scenes").glob(f"{scene_id}-*.fountain"))
        if not staged:
            raise RuntimeError(f"scene not found: {scene_id}")
        scene_path = staged[-1]
    fm, body = parse_front_matter(scene_path)
    current = str(fm.get("status", "idea"))
    allowed = load_config().get("state_machine", {}).get("allowed_transitions", {}).get(current, [])
    if target_status not in allowed:
        raise RuntimeError(f"cannot transition {current}->{target_status}; allowed={allowed}")
    fm["status"] = target_status
    if target_status == "candidate":
        target = PROJECT_ROOT / "staging" / "scenes" / f"{scene_id}-v{fm.get('version', 1)}-candidate.fountain"
    else:
        target = scene_path
    write_scene_file(target, fm, body)
    if target != scene_path and scene_path.exists():
        scene_path.unlink()
    _run_git("add", "-A", "--", ".")
    _run_git("commit", "-m", f"scriptops: promote {scene_id} {current}->{target_status}")
    print(f"Promoted {scene_id}: {current} -> {target_status}")


def cmd_review(args: argparse.Namespace) -> None:
    task_id = f"TASK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    task_dir = PROJECT_ROOT / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    task_pack = {
        "task_id": task_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "author": "human",
        "mode": "continuity-review",
        "scene_id": args.scene,
        "objective": f"Review scene {args.scene} for continuity, character consistency, and dramatic function.",
        "acceptance_criteria": [
            "All continuity constraints are respected",
            "Character voices match their cards",
            "Scene fulfills its stated purpose",
            "No unresolved references to decisions",
        ],
    }
    path = task_dir / "task-pack.yaml"
    path.write_text(yaml_dump(task_pack, sort_keys=False), encoding="utf-8")
    print(f"Created review task: {path}")
    print(f"Run: scriptops check-pre --task {task_id}")


def cmd_check_pre(args: argparse.Namespace) -> None:
    task_dir = PROJECT_ROOT / "tasks" / args.task
    task_path = task_dir / "task-pack.yaml"
    if not task_path.exists():
        raise RuntimeError(f"task pack missing: {task_path}")
    task = yaml_load(task_path.read_text(encoding="utf-8"))
    if not isinstance(task, dict):
        raise RuntimeError("task pack malformed")
    scene_id = str(task.get("scene_id", ""))
    scene_exists = bool(list(PROJECT_ROOT.glob(f"**/{scene_id}*.fountain")))
    report = {
        "task_id": args.task,
        "phase": "pre-ai",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": [
            {"name": "git_clean", "status": "PASS" if git_is_clean() else "FAIL"},
            {"name": "task_pack_parseable", "status": "PASS"},
            {"name": "scene_exists", "status": "PASS" if scene_exists else "FAIL"},
        ],
        "verdict": "PASS" if git_is_clean() and scene_exists else "FAIL",
    }
    (task_dir / "validation-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    prompt = (
        f"# Prompt ready\n\nTask: {args.task}\nScene: {scene_id}\n"
        f"Objective: {task.get('objective', '')}\n"
    )
    (task_dir / "prompt-ready.md").write_text(prompt, encoding="utf-8")
    if report["verdict"] != "PASS":
        raise RuntimeError("pre-AI validation failed")
    print(f"[PASS] Pre-AI validation: {args.task}")


def cmd_context_build(args: argparse.Namespace) -> None:
    task_dir = PROJECT_ROOT / "tasks" / args.task
    task_path = task_dir / "task-pack.yaml"
    if not task_path.exists():
        raise RuntimeError("task pack missing")
    candidates = [PROJECT_ROOT / "scenes" / f"{args.scene}.fountain"]
    candidates += sorted((PROJECT_ROOT / "staging" / "scenes").glob(f"{args.scene}-*.fountain"))
    scene_path = next((p for p in reversed(candidates) if p.exists()), None)
    if scene_path is None:
        raise RuntimeError(f"scene not found: {args.scene}")
    scene_text = scene_path.read_text(encoding="utf-8")
    content = (
        f"---\ncontext_pack_id: CTX-{args.task}-{args.scene}\n"
        f"task_id: {args.task}\nscene: {args.scene}\nmode: {args.mode}\n---\n\n"
        "## SCENE\n\n" + scene_text
    )
    path = task_dir / "context-pack.md"
    path.write_text(content, encoding="utf-8")
    print(f"Context pack written to: {path}")


def cmd_check_post(args: argparse.Namespace) -> None:
    task_dir = PROJECT_ROOT / "tasks" / args.task
    source = task_dir / (args.source or "webai-output.md")
    if not source.exists():
        raise RuntimeError(f"candidate source missing: {source}")
    text = source.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise RuntimeError("candidate source has no front matter")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise RuntimeError("candidate source front matter malformed")
    fm = yaml_load(parts[1])
    if not isinstance(fm, dict):
        raise RuntimeError("candidate front matter malformed")
    scene_id = str(fm.get("scene_id", ""))
    if not re.fullmatch(r"SCN-[0-9]{3,}", scene_id):
        raise RuntimeError("candidate scene_id invalid")
    if fm.get("status") != "candidate":
        raise RuntimeError("post-AI output must have status candidate")
    version = int(fm.get("version", 1))
    report = {
        "task_id": args.task,
        "phase": "post-ai",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": [
            {"name": "yaml_front_matter", "status": "PASS"},
            {"name": "status_candidate", "status": "PASS"},
            {"name": "scene_id_valid", "status": "PASS"},
        ],
        "verdict": "PASS",
    }
    report_path = task_dir / "validation-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    staging = PROJECT_ROOT / "staging" / "scenes" / f"{scene_id}-v{version}-candidate.fountain"
    staging.parent.mkdir(parents=True, exist_ok=True)
    staging.write_text(text, encoding="utf-8")
    _commit(f"scriptops: stage candidate {scene_id} from {args.task}", staging, report_path)
    print(f"[PASS] Post-AI validation passed. Staged: {staging}")


def cmd_validate(args: argparse.Namespace) -> None:
    scene = PROJECT_ROOT / "scenes" / f"{args.scene}.fountain"
    if not scene.exists():
        raise RuntimeError(f"scene missing: {args.scene}")
    fm, _ = parse_front_matter(scene)
    if fm.get("scene_id") != args.scene:
        raise RuntimeError("scene id mismatch")
    print("[OK] Basic structure check passed.")


def cmd_continuity_compile(args: argparse.Namespace) -> None:
    ensure_git_clean()
    log_path = SCRIPTOPS_DIR / "decision-log.ndjson"
    if not log_path.exists():
        print("WARNING: No decision log found.")
        return
    print("[INFO] X1B decision log present; continuity compilation remains a separate non-authority operation.")


def cmd_approve(args: argparse.Namespace) -> None:
    raise LegacyApprovalDisabled(
        "direct legacy cmd_approve is disabled before mutation; use phase6/scriptops-v2-hardening.py approve --decision-pr"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ScriptOps v2 active safe compatibility shim")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--name", default="MyScreenplay")
    sub.add_parser("check")
    p_new = sub.add_parser("scene-new")
    p_new.add_argument("--id", required=True)
    p_promote = sub.add_parser("scene-promote")
    p_promote.add_argument("--id", required=True)
    p_promote.add_argument(
        "--to",
        required=True,
        choices=[
            "idea", "question", "outline", "draft", "candidate", "accepted",
            "rejected", "archived", "revision_requested",
        ],
    )
    p_cont = sub.add_parser("continuity-compile")
    p_cont.add_argument("--scene", required=True)
    p_ctx = sub.add_parser("context-build")
    p_ctx.add_argument("--scene", required=True)
    p_ctx.add_argument("--mode", required=True)
    p_ctx.add_argument("--task", required=True)
    p_ctx.add_argument("--target", choices=["file", "clipboard"], default="file")
    p_pre = sub.add_parser("check-pre")
    p_pre.add_argument("--task", required=True)
    p_pre.add_argument("--max-tokens", type=int, default=14000)
    p_post = sub.add_parser("check-post")
    p_post.add_argument("--task", required=True)
    p_post.add_argument("--source", default=None)
    p_val = sub.add_parser("validate")
    p_val.add_argument("--scene", required=True)
    p_rev = sub.add_parser("review")
    p_rev.add_argument("--scene", required=True)
    p_app = sub.add_parser("approve")
    p_app.add_argument("--scene", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        globals()[f"cmd_{args.command.replace('-', '_')}"](args)
        return 0
    except LegacyApprovalDisabled as exc:
        print(f"LEGACY APPROVAL BLOCKED: {exc}", file=sys.stderr)
        return 2
    except RuntimeError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
