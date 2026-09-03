#!/usr/bin/env python3
"""Safe ScriptOps v2 compatibility shim.

The historical 2026-08 prototype is preserved only under ``sources/prototype``.
This active legacy-path module preserves the pre-approval interfaces used by
Phase-6 and bounded-proposal-view, but it cannot create ``accepted`` state.
Canonical acceptance is owned exclusively by ``phase6/x1b_human_decision.py``.
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
context_budgets:
  write-scene:
    total_tokens: 14000
    allocations: {}
  rewrite-scene:
    total_tokens: 14000
    allocations: {}
  dialogue-pass:
    total_tokens: 10000
    allocations: {}
  continuity-review:
    total_tokens: 12000
    allocations: {}
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

PROMPTS: dict[str, str] = {
    "write-scene": "Write only the requested scene and respect the supplied constraints.",
    "rewrite-scene": "Rewrite only the requested scene according to the task and supplied context.",
    "dialogue-pass": "Revise only dialogue while preserving scene facts and constraints.",
    "continuity-review": "Review continuity against the supplied scene, neighbors and constraints.",
}


class LegacyApprovalDisabled(RuntimeError):
    """Raised before any legacy accepted-state mutation."""


class ContextBudgetError(RuntimeError):
    pass


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
        if isinstance(value, dict):
            # Older repositories may have the original richer config; keep it.
            # Fresh X1B fixtures get the budgets from DEFAULT_CONFIG.
            if "context_budgets" not in value:
                defaults = yaml_load(DEFAULT_CONFIG)
                value["context_budgets"] = defaults["context_budgets"]
            return value
    value = yaml_load(DEFAULT_CONFIG)
    return value if isinstance(value, dict) else {}


def compute_sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def estimate_tokens(text: str) -> int:
    return len(text) // 4


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


class ContextBuilder:
    """Compatibility-preserved canonical-first context builder.

    BoundedProposalContextBuilder subclasses this class and overrides only
    ``_load_scene_card`` for exact task-bound proposals. Keeping this interface
    is required for historical Phase-6/P3 regressions and does not confer any
    accepted-state authority.
    """

    def __init__(self, project_root: Path):
        self.root = Path(project_root)
        self.config = load_config()
        self.bible = self._load_bible()
        self.scene_index = self._load_scene_index()

    def _load_bible(self) -> dict[str, Any]:
        bible_dir = self.root / "bible"
        bible: dict[str, Any] = {}
        for name in (
            "characters.yaml",
            "locations.yaml",
            "timeline.yaml",
            "premise.md",
            "themes.md",
            "style-guide.md",
        ):
            path = bible_dir / name
            if path.exists():
                bible[path.stem] = (
                    path.read_text(encoding="utf-8")
                    if name.endswith(".md")
                    else yaml_load(path.read_text(encoding="utf-8"))
                )
        return bible

    def _load_scene_index(self) -> dict[str, Any]:
        path = self.root / "summaries" / "scene-index.yaml"
        if not path.exists():
            return {}
        value = yaml_load(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}

    def _load_scene_card(self, scene_id: str) -> dict[str, Any]:
        # Canonical-first behavior is intentional. Staged proposals are visible
        # to downstream context only through BoundedProposalContextBuilder.
        canonical = self.root / "scenes" / f"{scene_id}.fountain"
        if canonical.exists():
            fm, body = parse_front_matter(canonical)
            fm["_body"] = body.strip()
            return fm
        exact_staged = self.root / "staging" / "scenes" / f"{scene_id}.fountain"
        if exact_staged.exists():
            fm, body = parse_front_matter(exact_staged)
            fm["_body"] = body.strip()
            return fm
        raise FileNotFoundError(f"Scene {scene_id} not found")

    def _hash_content(self, text: str) -> str:
        return compute_sha256(text)

    def build(self, scene_id: str, mode: str, task_id: str) -> Path:
        budgets = self.config.get("context_budgets", {})
        if mode not in budgets:
            raise ValueError(f"Unknown mode: {mode}. Available: {list(budgets)}")
        budget = budgets[mode]
        total = int(budget.get("total_tokens", 14000))
        scene_card = self._load_scene_card(scene_id)
        sections: list[str] = []
        sources: list[dict[str, Any]] = []

        def add_section(title: str, content: str, source_id: str, source_type: str) -> None:
            if not content or not content.strip():
                return
            sections.append(f"# {title}\n\n{content}")
            sources.append(
                {
                    "id": source_id,
                    "hash": self._hash_content(content),
                    "type": source_type,
                    "included_tokens": estimate_tokens(content),
                }
            )

        add_section(
            "ROLE INSTRUCTION",
            PROMPTS.get(mode, f"# Role: {mode}\nFollow the scene card and constraints precisely."),
            f"PROMPT-{mode}",
            "instruction",
        )

        task_dir = self.root / "tasks" / task_id
        task_pack_path = task_dir / "task-pack.yaml"
        if task_pack_path.exists():
            task_pack = yaml_load(task_pack_path.read_text(encoding="utf-8"))
            if not isinstance(task_pack, dict):
                raise RuntimeError("task pack is not an object")
            task_text = f"OBJECTIVE: {task_pack.get('objective', '')}\n\nACCEPTANCE CRITERIA:\n"
            task_text += "\n".join(f"- {c}" for c in task_pack.get("acceptance_criteria", []))
            if task_pack.get("forbidden_changes"):
                task_text += "\n\nFORBIDDEN CHANGES:\n" + "\n".join(
                    f"- {item}" for item in task_pack["forbidden_changes"]
                )
            add_section("TASK PACK", task_text, task_id, "task")

        scene_card_text = yaml_dump(
            {k: v for k, v in scene_card.items() if not k.startswith("_")},
            sort_keys=False,
        )
        add_section("SCENE CARD", scene_card_text, scene_id, "scene")

        if mode in (
            "write-scene",
            "rewrite-scene",
            "dialogue-pass",
            "continuity-review",
            "character-consistency-review",
        ):
            bible_parts: list[str] = []
            if "premise" in self.bible:
                bible_parts.append(f"PREMISE:\n{self.bible['premise']}")
            if "themes" in self.bible:
                bible_parts.append(f"THEMES:\n{self.bible['themes']}")
            if "style-guide" in self.bible:
                bible_parts.append(f"STYLE:\n{self.bible['style-guide']}")
            add_section("STORY BIBLE CORE", "\n\n".join(bible_parts), "BIBLE-CORE", "project")

        if mode in (
            "write-scene",
            "rewrite-scene",
            "dialogue-pass",
            "character-consistency-review",
        ):
            chars = self.bible.get("characters", {})
            char_cards: list[str] = []
            if isinstance(chars, dict):
                for name in scene_card.get("characters", []):
                    if name in chars:
                        char_cards.append(yaml_dump({name: chars[name]}, sort_keys=False))
            add_section("CHARACTER CARDS", "\n---\n".join(char_cards), "CHARS-RELEVANT", "character")

        if mode in ("write-scene", "rewrite-scene", "continuity-review"):
            deps = list(scene_card.get("depends_on", [])) + list(scene_card.get("spoils_or_sets_up", []))
            neighbor_texts: list[str] = []
            for dep_id in deps[:2]:
                try:
                    dep = self._load_scene_card(str(dep_id))
                    body = str(dep.get("_body", ""))[:1500]
                    neighbor_texts.append(f"### {dep_id}\n{body}")
                except FileNotFoundError:
                    neighbor_texts.append(f"### {dep_id}\n[SCENE NOT FOUND — CHECK DEPENDENCIES]")
            add_section("NEIGHBOR SCENES", "\n\n".join(neighbor_texts), "NEIGHBORS", "scene")

        if mode in ("write-scene", "continuity-review", "structure-review"):
            related: list[str] = []
            for tag in scene_card.get("tags", []):
                entries = self.scene_index.get("by_tag", {}).get(tag, [])
                for entry in entries[:3]:
                    if isinstance(entry, dict) and entry.get("scene_id") != scene_id:
                        related.append(f"- {entry['scene_id']}: {entry.get('summary', '')}")
            add_section("RELATED SCENES", "\n".join(related), "RELATED", "scene")

        if mode in ("write-scene", "rewrite-scene", "continuity-review"):
            constraints = "\n".join(str(v) for v in scene_card.get("continuity_constraints", []))
            add_section("CONTINUITY CONSTRAINTS", constraints, "CONTINUITY", "decision")

        if mode == "rewrite-scene":
            add_section("CURRENT VERSION", str(scene_card.get("_body", "")), f"{scene_id}-CURRENT", "scene")
            if task_pack_path.exists():
                task_pack = yaml_load(task_pack_path.read_text(encoding="utf-8"))
                if isinstance(task_pack, dict):
                    add_section("REVISION NOTES", str(task_pack.get("objective", "")), "REVISION", "task")

        add_section(
            "OUTPUT FORMAT",
            f"Output must follow the format specified for mode: {mode}. See ROLE INSTRUCTION for details.",
            f"FORMAT-{mode}",
            "instruction",
        )

        used = sum(int(source["included_tokens"]) for source in sources)
        if used > total:
            raise ContextBudgetError(f"Context over budget: {used}/{total} tokens")
        pack = {
            "context_pack_id": f"CTX-{task_id[-4:]}-{scene_id}",
            "task_id": task_id,
            "scene": scene_id,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "token_audit": {
                "budget": total,
                "used": used,
                "reserve": total - used,
                "status": "ok",
            },
            "included_sources": sources,
            "excluded_sources": self._list_excluded(scene_card, mode),
            "known_gaps": [],
        }
        pack_path = task_dir / "context-pack.md"
        pack_path.parent.mkdir(parents=True, exist_ok=True)
        body = "\n\n---\n\n".join(sections)
        pack_path.write_text(
            "---\n" + yaml_dump(pack, sort_keys=False) + "---\n\n" + body,
            encoding="utf-8",
        )
        return pack_path

    def _list_excluded(self, scene_card: dict[str, Any], mode: str) -> list[dict[str, str]]:
        excluded: list[dict[str, str]] = []
        all_scenes = set(self.scene_index.get("all_scenes", []))
        included = set(scene_card.get("depends_on", [])) | set(scene_card.get("spoils_or_sets_up", []))
        for sid in all_scenes - included:
            if sid != scene_card.get("scene_id"):
                excluded.append({"id": str(sid), "reason": "not_graph_adjacent", "type": "scene"})
        return excluded[:10]


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
    builder = ContextBuilder(PROJECT_ROOT)
    pack_path = builder.build(args.scene, args.mode, args.task)
    print(f"Context pack written to: {pack_path}")


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
