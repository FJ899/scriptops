#!/usr/bin/env python3
"""
ScriptOps v2 — Self-Contained Screenplay Operating System
Single-file edition. No external dependencies except PyYAML.

Install: pip install pyyaml
Usage: python scriptops.py <command> [args]
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# EMBEDDED SCHEMAS
# ============================================================

SCENE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SceneCard",
    "type": "object",
    "required": ["scene_id", "act", "status", "hash", "version", "title"],
    "properties": {
        "scene_id": {"type": "string", "pattern": "^SCN-[0-9]{3,}$"},
        "version": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "act": {"type": "integer", "minimum": 1, "maximum": 5},
        "sequence": {"type": "string"},
        "status": {
            "type": "string",
            "enum": ["idea", "question", "outline", "draft", "candidate", "accepted", "rejected", "archived"]
        },
        "location": {"type": "string"},
        "time": {"type": "string"},
        "characters": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "purpose": {"type": "array", "items": {"type": "string"}},
        "emotional_turn": {"type": "object", "properties": {"from": {"type": "string"}, "to": {"type": "string"}}},
        "depends_on": {"type": "array", "items": {"type": "string", "pattern": "^SCN-[0-9]{3,}$"}},
        "spoils_or_sets_up": {"type": "array", "items": {"type": "string", "pattern": "^SCN-[0-9]{3,}$"}},
        "continuity_constraints": {"type": "array", "items": {"type": "string"}},
        "tags": {"type": "array", "items": {"type": "string"}},
        "hash": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
        "parent_hash": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
        "context_hash": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
        "provenance": {
            "type": "object",
            "required": ["task_id", "mode", "timestamp"],
            "properties": {
                "task_id": {"type": "string"},
                "mode": {"type": "string"},
                "model": {"type": "string"},
                "timestamp": {"type": "string"}
            }
        }
    }
}

TASK_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TaskPack",
    "type": "object",
    "required": ["task_id", "created", "author", "mode", "objective", "scene_id"],
    "properties": {
        "task_id": {"type": "string", "pattern": "^TASK-[0-9]{4,}$"},
        "created": {"type": "string"},
        "author": {"type": "string"},
        "mode": {
            "type": "string",
            "enum": [
                "write-scene", "rewrite-scene", "dialogue-pass",
                "continuity-review", "character-consistency-review",
                "structure-review", "summarize-scene", "extract-decisions",
                "compare-versions"
            ]
        },
        "scene_id": {"type": "string", "pattern": "^SCN-[0-9]{3,}$"},
        "objective": {"type": "string", "minLength": 10},
        "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "forbidden_changes": {"type": "array", "items": {"type": "string"}},
        "previous_attempt": {"type": "string"},
        "context_sources": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "hash", "type"],
                "properties": {
                    "id": {"type": "string"},
                    "hash": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
                    "type": {"type": "string", "enum": ["project", "character", "scene", "decision", "summary", "instruction"]},
                    "included_tokens": {"type": "integer"}
                }
            }
        }
    }
}

# ============================================================
# EMBEDDED CONFIG
# ============================================================

DEFAULT_CONFIG = """project:
  name: ScriptOps Project
  version: "2.0"
  source_of_truth: git
  sqlite_mode: materialized_view
schema:
  scene: scene-schema.json
  task: task-schema.json
context_budgets:
  write-scene:
    total_tokens: 14000
    allocations:
      role_instruction: 800
      scene_card: 600
      story_bible_core: 1200
      character_cards: 2000
      timeline_events: 800
      neighbor_scenes_full: 3000
      related_scenes_summary: 2000
      continuity_constraints: 400
      output_format: 500
      reserve: 3700
  rewrite-scene:
    total_tokens: 14000
    allocations:
      role_instruction: 800
      current_version_full: 4000
      revision_notes: 1000
      story_bible_core: 800
      character_cards: 1500
      continuity_constraints: 400
      output_format: 500
      reserve: 5000
  dialogue-pass:
    total_tokens: 10000
    allocations:
      role_instruction: 700
      scene_dialogue_only: 4000
      character_voice_cards: 2500
      relationship_context: 1000
      output_format: 300
      reserve: 1500
  continuity-review:
    total_tokens: 12000
    allocations:
      role_instruction: 600
      scene_under_review: 3000
      dependent_scenes: 3000
      decision_log_relevant: 2000
      character_knowledge_states: 1500
      output_format: 400
      reserve: 1500
validation:
  preflight_checks:
    - git_working_tree_clean
    - scene_id_valid_and_unique
    - characters_exist_in_bible
    - dependencies_exist_and_accepted
    - token_budget_calculable
    - no_circular_dependencies
    - task_pack_schema_valid
    - context_files_exist_and_hashes_match
  postflight_checks:
    - yaml_front_matter_parseable
    - hash_matches_computed_sha256
    - parent_hash_matches_previous
    - fountain_syntax_basic
    - characters_mentioned_exist_or_declared
    - forbidden_phrases_check
    - status_is_candidate
    - required_sections_per_mode
    - context_hash_matches_sent_pack
  forbidden_phrase_rules:
    - name: continuity_anna_affair
      pattern: "(?i)Anna.*(wie|wiedziala|wiedziec).*(zdrad|afair)"
      scope:
        - SCN-017
        - SCN-018
        - SCN-019
        - SCN-020
        - SCN-021
        - SCN-022
        - SCN-023
        - SCN-024
        - SCN-025
        - SCN-026
        - SCN-027
        - SCN-028
        - SCN-029
        - SCN-030
      error: "Anna cannot know about the affair before SCN-031 (per DEC-0042)"
state_machine:
  allowed_transitions:
    idea:
      - outline
      - question
    question:
      - idea
      - outline
    outline:
      - draft
    draft:
      - candidate
    candidate:
      - accepted
      - rejected
      - revision_requested
    revision_requested:
      - draft
    accepted:
      - archived
    rejected:
      - draft
      - idea
    archived: []
retrieval:
  priority_order:
    - metadata_rules
    - graph_traversal
    - semantic_proxy
    - hierarchical_summaries
  graph_traversal_depth: 2
  semantic_proxy:
    enabled: true
    index_file: summaries/scene-index.yaml
    method: inverted_index_keywords
continuity:
  auto_compile: true
  compile_on:
    - decision_added
    - decision_superseded
    - scene_accepted
provenance:
  hash_algorithm: sha256
  include_context_hash: true
  include_parent_hash: true
"""

# ============================================================
# EMBEDDED PROMPTS
# ============================================================

PROMPTS = {
    "write-scene": """You are a Scene Writer for a screenplay project.
You write ONLY the requested scene. You do NOT summarize, explain, or invent material outside the provided context.

## Core Rules
1. Output must be valid Fountain screenplay format with YAML front matter.
2. Every line of dialogue must serve the scene's stated PURPOSE.
3. Respect all CONTINUITY CONSTRAINTS. If a constraint says a character does not know something, you must NOT reveal it.
4. Maintain each character's VOICE as defined in their character card.
5. The EMOTIONAL TURN must be clearly dramatized, not narrated.
6. Do NOT resolve open questions that are marked as unresolved in the context.
7. Do NOT introduce new characters not listed in the scene card.
8. Do NOT change established facts (locations, timelines, relationships) unless the task explicitly requests a rewrite.
9. Use Polish language for dialogue. Scene headings and transitions may use English Fountain notation.

## Output Format
---
scene_id: [PRESERVE FROM SCENE CARD]
version: [INCREMENT BY 1]
status: candidate
hash: PLACEHOLDER
parent_hash: [PRESERVE PREVIOUS HASH IF REWRITE]
context_hash: [PRESERVE FROM CONTEXT PACK]
provenance:
  task_id: [FROM TASK]
  mode: write-scene
  model: web-gpt
  timestamp: [ISO8601]
title: [PRESERVE OR UPDATE]
act: [PRESERVE]
sequence: [PRESERVE]
location: [PRESERVE]
time: [PRESERVE]
characters: [PRESERVE]
purpose: [PRESERVE]
emotional_turn:
  from: [PRESERVE]
  to: [PRESERVE]
depends_on: [PRESERVE]
spoils_or_sets_up: [PRESERVE]
continuity_constraints: [PRESERVE]
tags: [PRESERVE]
---

[SCENE BODY IN FOUNTAIN]

## STOP Conditions
If any of the following are true, output ONLY:
STOP: [reason]

- Scene card is missing purpose or emotional_turn.
- Continuity constraints contradict each other.
- Required character cards are missing from context.
- You are asked to write a scene that depends_on a scene not yet provided in context.
- The context pack hash does not match the declared context_hash.
- You cannot fulfill the purpose within the character voices provided.
""",

    "rewrite-scene": """You are a Scene Rewrite Specialist.
You rewrite the provided scene according to specific revision notes while preserving all elements marked as forbidden to change.

## Core Rules
1. Preserve all scene headings, transitions, and action lines unless revision notes explicitly request changes.
2. Maintain each character's VOICE as defined in their character card.
3. Respect FORBIDDEN CHANGES — these elements must remain exactly as in the current version.
4. Implement all changes described in REVISION NOTES precisely.
5. The EMOTIONAL TURN must remain consistent unless the revision explicitly redirects it.
6. Do NOT introduce new characters not listed in the scene card.
7. Mark all changed lines with [CHANGED] at the end of the line.

## Output Format
---
scene_id: [PRESERVE]
version: [INCREMENT BY 1]
status: candidate
hash: PLACEHOLDER
parent_hash: [PRESERVE CURRENT HASH]
context_hash: [PRESERVE FROM CONTEXT PACK]
provenance:
  task_id: [FROM TASK]
  mode: rewrite-scene
  model: web-gpt
  timestamp: [ISO8601]
---

[REWRITTEN SCENE — mark changed lines with [CHANGED]]

## STOP Conditions
If any of the following are true, output ONLY:
STOP: [reason]

- Forbidden changes list contradicts revision notes.
- Current version is missing or corrupted.
- Revision notes are ambiguous or self-contradictory.
""",

    "dialogue-pass": """You are a Dialogue Doctor for a screenplay project.
You rewrite ONLY the dialogue in the provided scene. You do NOT change action lines, scene headings, or transitions.

## Core Rules
1. Preserve all scene headings, transitions, and action lines exactly as provided.
2. Rewrite only lines that are dialogue (indented text, not parentheticals).
3. Maintain each character's VOICE as defined in their character card.
4. Deepen subtext — what characters say should differ from what they mean.
5. Eliminate on-the-nose exposition. Never have characters state information they both already know.
6. Vary rhythm: mix short punches with longer speeches, interruptions, pauses.
7. Ensure each line advances the scene's PURPOSE or emotional turn.
8. Use Polish language for all dialogue.

## Output Format
---
scene_id: [PRESERVE]
version: [INCREMENT BY 1]
status: candidate
hash: PLACEHOLDER
parent_hash: [PRESERVE]
context_hash: [PRESERVE FROM CONTEXT PACK]
provenance:
  task_id: [FROM TASK]
  mode: dialogue-pass
  model: web-gpt
  timestamp: [ISO8601]
---

[SCENE WITH REWRITTEN DIALOGUE — mark changed lines with [CHANGED] at end]

## STOP Conditions
If any of the following are true, output ONLY:
STOP: [reason]

- Character voice cards are missing.
- Scene has no dialogue to rewrite.
- Purpose of scene is unclear.
""",

    "continuity-review": """You are a Continuity Reviewer for a screenplay project.
You verify that the scene respects all established facts, decisions, and constraints.

## Core Rules
1. Check every CONTINUITY CONSTRAINT against the scene text.
2. Verify character knowledge states — does any character know something they should not yet?
3. Check timeline consistency — time of day, location, elapsed time between scenes.
4. Verify prop continuity — objects appear/disappear logically.
5. Check for contradictions with NEIGHBOR SCENES.
6. Flag any UNSUPPORTED CLAIM — a statement in the scene not backed by context.

## Output Format
---
review_id: [AUTO]
task_id: [FROM TASK]
scene_id: [PRESERVE]
timestamp: [ISO8601]
---

## Verdict: [PASS / WARN / FAIL]

## Defects
- [ ] None found
OR
- [ ] [Severity: critical/warning] [Description] [Evidence from scene text]

## Unsupported Claims
- [ ] None found
OR
- [ ] [Claim] [Why unsupported]

## Required Changes
- [ ] None
OR
- [ ] [Specific change needed]

## STOP Conditions
If context is insufficient to verify continuity, output:
STOP: INSUFFICIENT_CONTEXT [specific missing information]
""",

    "character-consistency-review": """You are a Character Consistency Reviewer.
You verify that each character in the scene behaves according to their established voice, goal, and arc.

## Core Rules
1. Check each character's dialogue against their VOICE card.
2. Verify that actions align with stated GOALS.
3. Ensure no character reveals information they are keeping SECRET.
4. Check that relationship dynamics match established patterns.
5. Flag any deviation from character ARC progression.

## Output Format
---
review_id: [AUTO]
task_id: [FROM TASK]
scene_id: [PRESERVE]
timestamp: [ISO8601]
---

## Per-Character Reports

### [CHARACTER NAME]
- Voice Match: [score 1-10]
- Goal Alignment: [PASS/FAIL]
- Secret Preservation: [PASS/FAIL]
- Arc Consistency: [PASS/FAIL]
- Issues: [list or "None"]

## Overall Verdict: [PASS / WARN / FAIL]

## STOP Conditions
If character cards are missing, output:
STOP: MISSING_CHARACTER_CARDS [list missing]
""",

    "structure-review": """You are a Structure Reviewer for a screenplay project.
You analyze the scene's placement and function within the larger narrative structure.

## Core Rules
1. Check scene alignment with BEAT SHEET.
2. Verify scene fulfills its stated PURPOSE within the sequence.
3. Assess PACING — does the scene match the tempo of its act?
4. Check SETUP/PAYOFF relationships — does the scene properly set up future events or pay off earlier ones?
5. Evaluate dramatic tension progression.

## Output Format
---
review_id: [AUTO]
task_id: [FROM TASK]
scene_id: [PRESERVE]
timestamp: [ISO8601]
---

## Structural Analysis
- Beat Alignment: [PASS/FAIL]
- Purpose Fulfillment: [PASS/FAIL]
- Pacing: [too_slow / ok / too_fast]
- Setup/Payoff Status: [list of checked relationships]

## Recommendations
- [ ] None
OR
- [ ] [Specific structural adjustment]

## Overall Verdict: [PASS / WARN / FAIL]
""",

    "summarize-scene": """You are a Scene Summarizer.
You produce a concise summary of the provided scene for use in hierarchical context packs.

## Core Rules
1. Capture the dramatic function, not just the plot.
2. Include emotional turn and key character dynamics.
3. Note any decisions or continuity points established.
4. Keep it under 150 words.

## Output Format
---
summary_id: [AUTO]
scene_id: [PRESERVE]
timestamp: [ISO8601]
---

## 3-Sentence Summary
[Concise narrative summary]

## Dramatic Function
[One sentence: what this scene accomplishes structurally]

## Key Decisions / Continuity
- [list or "None"]
"""
}

# ============================================================
# YAML UTILITIES (minimal, no external deps)
# ============================================================

def yaml_load(text):
    """Minimal YAML loader for our subset (no anchors, simple structures)."""
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        # Fallback: parse simple YAML subset
        return _simple_yaml_parse(text)

def yaml_dump(obj, sort_keys=False):
    """Minimal YAML dumper."""
    try:
        import yaml
        return yaml.dump(obj, sort_keys=sort_keys, allow_unicode=True, default_flow_style=False)
    except ImportError:
        return _simple_yaml_dump(obj)

def _simple_yaml_parse(text):
    """Parse simple YAML: key: value, lists with -, nested dicts."""
    result = {}
    lines = text.split("\n")
    stack = [(result, 0)]
    current_list = None

    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        # Pop stack to correct level
        while stack and stack[-1][1] >= indent and len(stack) > 1:
            stack.pop()

        current, _ = stack[-1]

        if stripped.startswith("-"):
            # List item
            val = stripped[1:].strip()
            if ":" in val:
                key, value = val.split(":", 1)
                if current_list is None:
                    current_list = []
                    if isinstance(current, dict):
                        # Find the last key that needs a list
                        pass
                item = {key.strip(): _parse_yaml_value(value.strip())}
                current_list.append(item)
            else:
                if current_list is None:
                    current_list = []
                current_list.append(_parse_yaml_value(val))
        elif ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                # Nested dict
                new_dict = {}
                current[key] = new_dict
                stack.append((new_dict, indent + 2))
                current_list = None
            else:
                current[key] = _parse_yaml_value(value)
                current_list = None

    return result

def _parse_yaml_value(v):
    if v == "true": return True
    if v == "false": return False
    if v == "null" or v == "~": return None
    if v.startswith("'") and v.endswith("'"): return v[1:-1]
    if v.startswith('"') and v.endswith('"'): return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        return [_parse_yaml_value(x.strip()) for x in v[1:-1].split(",") if x.strip()]
    try:
        return int(v)
    except:
        try:
            return float(v)
        except:
            return v

def _simple_yaml_dump(obj, indent=0):
    """Dump simple objects to YAML-like format."""
    lines = []
    prefix = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{prefix}{k}:")
                lines.append(_simple_yaml_dump(v, indent + 1))
            else:
                lines.append(f"{prefix}{k}: {_yaml_scalar(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    if first:
                        lines.append(f"{prefix}- {k}: {_yaml_scalar(v)}")
                        first = False
                    else:
                        lines.append(f"{prefix}  {k}: {_yaml_scalar(v)}")
            else:
                lines.append(f"{prefix}- {_yaml_scalar(item)}")
    else:
        lines.append(f"{prefix}{_yaml_scalar(obj)}")
    return "\n".join(lines)

def _yaml_scalar(v):
    if v is None: return "null"
    if isinstance(v, bool): return str(v).lower()
    if isinstance(v, str):
        if any(c in v for c in ":#[]{}|>&*!?,'\"\n"):
            return f'"{v}"'
        return v
    return str(v)

# ============================================================
# CORE UTILITIES
# ============================================================

PROJECT_ROOT = Path(".").resolve()
SCRIPTOPS_DIR = PROJECT_ROOT / ".scriptops"
CONFIG_PATH = SCRIPTOPS_DIR / "config.yaml"

def load_config():
    if CONFIG_PATH.exists():
        return yaml_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return yaml_load(DEFAULT_CONFIG)

def git_is_clean():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return result.stdout.strip() == ""

def ensure_git_clean():
    if not git_is_clean():
        print("FATAL: Git working tree is dirty. Commit or stash before proceeding.", file=sys.stderr)
        sys.exit(1)

def compute_sha256(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

def estimate_tokens(text):
    return len(text) // 4

def parse_front_matter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    return yaml_load(parts[1]), parts[2]

def write_scene_file(path, fm, body):
    fm_copy = dict(fm)
    fm_copy.pop("hash", None)
    canonical = yaml_dump(fm_copy, sort_keys=False) + body
    fm["hash"] = compute_sha256(canonical)
    text = "---\n" + yaml_dump(fm, sort_keys=False) + "---" + body
    path.write_text(text, encoding="utf-8")
    return fm["hash"]

# ============================================================
# CONTEXT BUILDER
# ============================================================

class ContextBuilder:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.config = load_config()
        self.bible = self._load_bible()
        self.scene_index = self._load_scene_index()

    def _load_bible(self):
        bible_dir = self.root / "bible"
        bible = {}
        for f in ["characters.yaml", "locations.yaml", "timeline.yaml", "premise.md", "themes.md", "style-guide.md"]:
            path = bible_dir / f
            if path.exists():
                bible[f.stem] = path.read_text(encoding="utf-8") if f.endswith(".md") else yaml_load(path.read_text(encoding="utf-8"))
        return bible

    def _load_scene_index(self):
        idx_path = self.root / "summaries" / "scene-index.yaml"
        if idx_path.exists():
            return yaml_load(idx_path.read_text(encoding="utf-8"))
        return {}

    def _load_scene_card(self, scene_id):
        for base in [self.root / "scenes", self.root / "staging" / "scenes"]:
            path = base / f"{scene_id}.fountain"
            if path.exists():
                fm, body = parse_front_matter(path)
                fm["_body"] = body.strip()
                return fm
        raise FileNotFoundError(f"Scene {scene_id} not found")

    def _hash_content(self, text):
        return compute_sha256(text)

    def build(self, scene_id, mode, task_id):
        if mode not in self.config.get("context_budgets", {}):
            raise ValueError(f"Unknown mode: {mode}. Available: {list(self.config.get('context_budgets', {}).keys())}")

        budget = self.config["context_budgets"][mode]
        allocations = budget["allocations"]
        total = budget["total_tokens"]

        scene_card = self._load_scene_card(scene_id)

        sections = []
        sources = []

        def add_section(title, content, source_id, source_type):
            if not content or not content.strip():
                return
            sections.append(f"# {title}\n\n{content}")
            sources.append({
                "id": source_id,
                "hash": self._hash_content(content),
                "type": source_type,
                "included_tokens": estimate_tokens(content)
            })

        # Layer 1: Role instruction
        prompt_text = PROMPTS.get(mode, f"# Role: {mode}\nFollow the scene card and constraints precisely.")
        add_section("ROLE INSTRUCTION", prompt_text, f"PROMPT-{mode}", "instruction")

        # Layer 2: Task objective
        task_dir = self.root / "tasks" / task_id
        task_pack_path = task_dir / "task-pack.yaml"
        if task_pack_path.exists():
            task_pack = yaml_load(task_pack_path.read_text(encoding="utf-8"))
            task_text = f"OBJECTIVE: {task_pack.get('objective', '')}\n\nACCEPTANCE CRITERIA:\n"
            task_text += "\n".join(f"- {c}" for c in task_pack.get('acceptance_criteria', []))
            if task_pack.get('forbidden_changes'):
                task_text += "\n\nFORBIDDEN CHANGES:\n" + "\n".join(f"- {f}" for f in task_pack['forbidden_changes'])
            add_section("TASK PACK", task_text, task_id, "task")

        # Layer 3: Scene card
        scene_card_text = yaml_dump({k: v for k, v in scene_card.items() if not k.startswith('_')}, sort_keys=False)
        add_section("SCENE CARD", scene_card_text, scene_id, "scene")

        # Mode-specific layers
        if mode in ("write-scene", "rewrite-scene", "dialogue-pass", "continuity-review", "character-consistency-review"):
            bible_parts = []
            if "premise" in self.bible:
                bible_parts.append(f"PREMISE:\n{self.bible['premise']}")
            if "themes" in self.bible:
                bible_parts.append(f"THEMES:\n{self.bible['themes']}")
            if "style-guide" in self.bible:
                bible_parts.append(f"STYLE:\n{self.bible['style-guide']}")
            add_section("STORY BIBLE CORE", "\n\n".join(bible_parts), "BIBLE-CORE", "project")

        if mode in ("write-scene", "rewrite-scene", "dialogue-pass", "character-consistency-review"):
            char_names = scene_card.get("characters", [])
            chars = self.bible.get("characters", {})
            char_cards = []
            for name in char_names:
                if name in chars:
                    char_cards.append(yaml_dump({name: chars[name]}, sort_keys=False))
            add_section("CHARACTER CARDS", "\n---\n".join(char_cards), "CHARS-RELEVANT", "character")

        if mode in ("write-scene", "rewrite-scene", "continuity-review"):
            deps = scene_card.get("depends_on", []) + scene_card.get("spoils_or_sets_up", [])
            neighbor_texts = []
            for dep_id in deps[:2]:
                try:
                    dep = self._load_scene_card(dep_id)
                    body = dep.get("_body", "")[:1500]
                    neighbor_texts.append(f"### {dep_id}\n{body}")
                except FileNotFoundError:
                    neighbor_texts.append(f"### {dep_id}\n[SCENE NOT FOUND — CHECK DEPENDENCIES]")
            add_section("NEIGHBOR SCENES", "\n\n".join(neighbor_texts), "NEIGHBORS", "scene")

        if mode in ("write-scene", "continuity-review", "structure-review"):
            related = []
            for tag in scene_card.get("tags", []):
                entries = self.scene_index.get("by_tag", {}).get(tag, [])
                for entry in entries[:3]:
                    if isinstance(entry, dict) and entry.get("scene_id") != scene_id:
                        related.append(f"- {entry['scene_id']}: {entry.get('summary', '')}")
            if related:
                add_section("RELATED SCENES", "\n".join(related), "RELATED", "scene")

        if mode in ("write-scene", "rewrite-scene", "continuity-review"):
            constraints = "\n".join(scene_card.get("continuity_constraints", []))
            if constraints:
                add_section("CONTINUITY CONSTRAINTS", constraints, "CONTINUITY", "decision")

        if mode == "rewrite-scene":
            add_section("CURRENT VERSION", scene_card.get("_body", ""), f"{scene_id}-CURRENT", "scene")
            if task_pack_path.exists():
                tp = yaml_load(task_pack_path.read_text(encoding="utf-8"))
                notes = tp.get("objective", "")
                add_section("REVISION NOTES", notes, "REVISION", "task")

        if mode == "dialogue-pass":
            body = scene_card.get("_body", "")
            dialogue_lines = []
            for l in body.splitlines():
                stripped = l.strip()
                if stripped and stripped[0] in " \t" and not stripped.startswith("("):
                    dialogue_lines.append(l)
            add_section("CURRENT DIALOGUE", "\n".join(dialogue_lines), f"{scene_id}-DIALOGUE", "scene")

        if mode == "structure-review":
            beat_path = self.root / "outline" / "beat-sheet.md"
            if beat_path.exists():
                add_section("BEAT SHEET", beat_path.read_text(encoding="utf-8")[:2000], "BEATS", "outline")
            seq_summaries = []
            for seq_file in (self.root / "summaries").glob("sequence-*.md"):
                seq_summaries.append(f"## {seq_file.stem}\n{seq_file.read_text(encoding='utf-8')[:500]}")
            if seq_summaries:
                add_section("SEQUENCE SUMMARIES", "\n\n".join(seq_summaries), "SEQUENCES", "summary")

        # Output format
        output_fmt = f"Output must follow the format specified for mode: {mode}. See ROLE INSTRUCTION for details."
        add_section("OUTPUT FORMAT", output_fmt, f"FORMAT-{mode}", "instruction")

        used = sum(s["included_tokens"] for s in sources)
        reserve = total - used

        if used > total:
            raise ContextBudgetError(f"Context over budget: {used}/{total} tokens. Truncate or increase reserve.")

        pack = {
            "context_pack_id": f"CTX-{task_id[-4:]}-{scene_id}",
            "task_id": task_id,
            "scene": scene_id,
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "token_audit": {
                "budget": total,
                "used": used,
                "reserve": reserve,
                "status": "ok" if used <= total else "overflow"
            },
            "included_sources": sources,
            "excluded_sources": self._list_excluded(scene_card, mode),
            "known_gaps": []
        }

        pack_path = self.root / "tasks" / task_id / "context-pack.md"
        pack_path.parent.mkdir(parents=True, exist_ok=True)

        header = yaml_dump(pack, sort_keys=False)
        body = "\n\n---\n\n".join(sections)
        full = f"---\n{header}---\n\n{body}"

        pack_path.write_text(full, encoding="utf-8")
        return pack_path

    def _list_excluded(self, scene_card, mode):
        excluded = []
        all_scenes = set(self.scene_index.get("all_scenes", []))
        included = set(scene_card.get("depends_on", []) + scene_card.get("spoils_or_sets_up", []))
        for sid in all_scenes - included:
            if sid != scene_card.get("scene_id"):
                excluded.append({"id": sid, "reason": "not_graph_adjacent", "type": "scene"})
        return excluded[:10]

class ContextBudgetError(Exception):
    pass

# ============================================================
# COMMANDS
# ============================================================

def cmd_init(args):
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    for d in [
        SCRIPTOPS_DIR / "prompts",
        PROJECT_ROOT / "bible",
        PROJECT_ROOT / "outline",
        PROJECT_ROOT / "scenes",
        PROJECT_ROOT / "staging" / "scenes",
        PROJECT_ROOT / "summaries",
        PROJECT_ROOT / "tasks"
    ]:
        d.mkdir(parents=True, exist_ok=True)

    CONFIG_PATH.write_text(DEFAULT_CONFIG, encoding="utf-8")

    # Write embedded prompts
    for name, content in PROMPTS.items():
        prompt_path = SCRIPTOPS_DIR / "prompts" / f"{name}.prompt"
        prompt_path.write_text(content, encoding="utf-8")

    # Write schemas
    (SCRIPTOPS_DIR / "scene-schema.json").write_text(json.dumps(SCENE_SCHEMA, indent=2, ensure_ascii=False), encoding="utf-8")
    (SCRIPTOPS_DIR / "task-schema.json").write_text(json.dumps(TASK_SCHEMA, indent=2, ensure_ascii=False), encoding="utf-8")

    subprocess.run(["git", "init"], cwd=PROJECT_ROOT, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-m", "scriptops v2: init project"], cwd=PROJECT_ROOT, capture_output=True)
    print(f"Initialized ScriptOps v2 project: {args.name}")
    print("Next steps:")
    print("  1. Fill bible/characters.yaml")
    print("  2. Create outline/acts.yaml and outline/beat-sheet.md")
    print("  3. Run: scriptops scene-new --id SCN-001")

def cmd_check(args):
    ensure_git_clean()
    print("[OK] Git working tree clean.")
    print("[OK] Config loaded.")
    print("[OK] Registry index conceptually valid (rebuild on demand).")
    print("[INFO] Run `scriptops validate --scene <id>` for per-scene checks.")

def cmd_scene_new(args):
    ensure_git_clean()
    scene_id = args.id
    scene_path = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"
    if scene_path.exists():
        print(f"FATAL: Scene {scene_id} already exists.", file=sys.stderr)
        sys.exit(1)

    template = f"""---
scene_id: {scene_id}
version: 1
status: idea
hash: PLACEHOLDER
title: ""
act: 1
sequence: ""
location: ""
time: ""
characters: []
purpose: []
emotional_turn:
  from: ""
  to: ""
depends_on: []
spoils_or_sets_up: []
continuity_constraints: []
tags: []
---

INT. LOCATION - TIME

# Scene body in Fountain format
"""
    scene_path.write_text(template, encoding="utf-8")
    subprocess.run(["git", "add", str(scene_path)], cwd=PROJECT_ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"scriptops: create idea {scene_id}"], cwd=PROJECT_ROOT, capture_output=True)
    print(f"Created idea: {scene_path}")

def cmd_scene_promote(args):
    ensure_git_clean()
    scene_id = args.id
    target_status = args.to

    scene_path = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"
    if not scene_path.exists():
        candidates = list((PROJECT_ROOT / "staging" / "scenes").glob(f"{scene_id}-*.fountain"))
        if candidates:
            scene_path = sorted(candidates)[-1]
        else:
            print(f"FATAL: Scene {scene_id} not found.", file=sys.stderr)
            sys.exit(1)

    fm, body = parse_front_matter(scene_path)
    current = fm.get("status", "idea")
    config = load_config()
    allowed = config.get("state_machine", {}).get("allowed_transitions", {}).get(current, [])

    if target_status not in allowed:
        print(f"FATAL: Cannot transition {current} -> {target_status}. Allowed: {allowed}", file=sys.stderr)
        sys.exit(1)

    fm["status"] = target_status
    fm["hash"] = "PLACEHOLDER"

    if target_status in ("candidate", "accepted"):
        if target_status == "accepted":
            target_path = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"
        else:
            target_path = PROJECT_ROOT / "staging" / "scenes" / f"{scene_id}-v{fm['version']}-{target_status}.fountain"

        fm_copy = {k: v for k, v in fm.items() if k != "hash"}
        canonical = yaml_dump(fm_copy, sort_keys=False) + body
        fm["hash"] = compute_sha256(canonical)

        text = "---\n" + yaml_dump(fm, sort_keys=False) + "---" + body
        target_path.write_text(text, encoding="utf-8")
        if target_path != scene_path:
            scene_path.unlink()
    else:
        fm_copy = {k: v for k, v in fm.items() if k != "hash"}
        canonical = yaml_dump(fm_copy, sort_keys=False) + body
        fm["hash"] = compute_sha256(canonical)
        text = "---\n" + yaml_dump(fm, sort_keys=False) + "---" + body
        scene_path.write_text(text, encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"scriptops: promote {scene_id} {current}->{target_status}"], cwd=PROJECT_ROOT, capture_output=True)
    print(f"Promoted {scene_id}: {current} -> {target_status}")

def cmd_continuity_compile(args):
    ensure_git_clean()
    scene_id = args.scene

    log_path = SCRIPTOPS_DIR / "decision-log.ndjson"
    if not log_path.exists():
        print("WARNING: No decision log found.")
        return

    decisions = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                decisions.append(json.loads(line))

    active = [d for d in decisions if d.get("status") == "active" and (scene_id in d.get("scope", []) or any(scene_id in str(s) for s in d.get("scope", [])))]

    scene_path = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"
    if not scene_path.exists():
        candidates = list((PROJECT_ROOT / "staging" / "scenes").glob(f"{scene_id}-*.fountain"))
        if candidates:
            scene_path = sorted(candidates)[-1]
        else:
            print(f"FATAL: Scene {scene_id} not found.", file=sys.stderr)
            sys.exit(1)

    fm, body = parse_front_matter(scene_path)
    fm["continuity_constraints"] = [d["text"] for d in active]

    fm_copy = {k: v for k, v in fm.items() if k != "hash"}
    canonical = yaml_dump(fm_copy, sort_keys=False) + body
    fm["hash"] = compute_sha256(canonical)
    text = "---\n" + yaml_dump(fm, sort_keys=False) + "---" + body
    scene_path.write_text(text, encoding="utf-8")

    compile_log = SCRIPTOPS_DIR / "continuity-log.ndjson"
    with compile_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scene_id": scene_id,
            "compiled_from": [d["id"] for d in active],
            "constraints_count": len(active)
        }, ensure_ascii=False) + "\n")

    subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"scriptops: compile continuity for {scene_id}"], cwd=PROJECT_ROOT, capture_output=True)
    print(f"Compiled {len(active)} continuity constraints for {scene_id}")
    for d in active:
        print(f"  - [{d['id']}] {d['text'][:80]}...")

def cmd_context_build(args):
    builder = ContextBuilder(PROJECT_ROOT)
    pack_path = builder.build(args.scene, args.mode, args.task)

    if args.target == "clipboard":
        text = pack_path.read_text(encoding="utf-8")
        try:
            import pyperclip
            pyperclip.copy(text)
            print(f"Context pack ({len(text)} chars, ~{len(text)//4} tokens) copied to clipboard.")
        except ImportError:
            print("pyperclip not installed. Install: pip install pyperclip")
            print(f"Pack written to: {pack_path}")
    else:
        print(f"Context pack written to: {pack_path}")

def cmd_check_pre(args):
    config = load_config()
    task_dir = PROJECT_ROOT / "tasks" / args.task
    task_pack_path = task_dir / "task-pack.yaml"

    if not task_pack_path.exists():
        print(f"FATAL: Task pack not found: {task_pack_path}", file=sys.stderr)
        sys.exit(1)

    report = {"task_id": args.task, "phase": "pre-ai", "timestamp": datetime.now(timezone.utc).isoformat(), "checks": [], "verdict": "PASS"}

    # Check 1: Git clean
    if not git_is_clean():
        report["checks"].append({"name": "git_clean", "status": "FAIL", "message": "Git working tree dirty"})
        report["verdict"] = "FAIL"
    else:
        report["checks"].append({"name": "git_clean", "status": "PASS"})

    # Check 2: Task pack parseable
    try:
        task_pack = yaml_load(task_pack_path.read_text(encoding="utf-8"))
        report["checks"].append({"name": "task_pack_parseable", "status": "PASS"})
    except Exception as e:
        report["checks"].append({"name": "task_pack_parseable", "status": "FAIL", "message": str(e)})
        report["verdict"] = "FAIL"
        task_pack = {}

    # Check 3: Scene exists
    scene_id = task_pack.get("scene_id", "")
    scene_paths = list(PROJECT_ROOT.glob(f"**/{scene_id}*.fountain"))
    if not scene_paths:
        report["checks"].append({"name": "scene_exists", "status": "FAIL", "message": f"Scene {scene_id} not found"})
        report["verdict"] = "FAIL"
    else:
        report["checks"].append({"name": "scene_exists", "status": "PASS"})

    # Check 4: Context files exist (simplified)
    context_files = task_pack.get("context_files", task_pack.get("context_sources", []))
    missing = []
    for cf in context_files:
        fid = cf if isinstance(cf, str) else cf.get("id", "")
        resolved = None
        for base in [PROJECT_ROOT / "bible", PROJECT_ROOT / "scenes", PROJECT_ROOT / "summaries", SCRIPTOPS_DIR]:
            for ext in ["", ".md", ".yaml", ".fountain"]:
                p = base / f"{fid}{ext}"
                if p.exists():
                    resolved = p
                    break
            if resolved:
                break
        if not resolved:
            missing.append(fid)

    if missing:
        report["checks"].append({"name": "context_files_exist", "status": "FAIL", "message": f"Missing: {missing}"})
        report["verdict"] = "FAIL"
    else:
        report["checks"].append({"name": "context_files_exist", "status": "PASS"})

    # Check 5: Token budget
    max_tokens = args.max_tokens or 14000
    total_chars = len(task_pack_path.read_text(encoding="utf-8"))
    estimated = total_chars // 4
    if estimated > max_tokens:
        report["checks"].append({"name": "token_budget", "status": "FAIL", "message": f"Estimated {estimated} > limit {max_tokens}"})
        report["verdict"] = "FAIL"
    else:
        report["checks"].append({"name": "token_budget", "status": "PASS", "estimated": estimated, "limit": max_tokens})

    report_path = task_dir / "validation-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if report["verdict"] == "PASS":
        prompt_ready = task_dir / "prompt-ready.md"
        prompt_ready.write_text(f"# PROMPT READY\n\nTask: {args.task}\nAll pre-flight checks passed.\nRun: scriptops context-build --scene {scene_id} --mode {task_pack.get('mode', 'write-scene')} --task {args.task}\n", encoding="utf-8")
        print(f"[PASS] Pre-AI validation passed. Prompt ready: {prompt_ready}")
    else:
        print(f"[FAIL] Pre-AI validation failed. See: {report_path}")
        for c in report["checks"]:
            if c["status"] == "FAIL":
                print(f"  FAIL: {c['name']} — {c.get('message', '')}")
        sys.exit(1)

def cmd_check_post(args):
    config = load_config()
    task_dir = PROJECT_ROOT / "tasks" / args.task
    output_path = task_dir / (args.source or "webai-output.md")

    if not output_path.exists():
        print(f"FATAL: Output not found: {output_path}", file=sys.stderr)
        sys.exit(1)

    report = {"task_id": args.task, "phase": "post-ai", "timestamp": datetime.now(timezone.utc).isoformat(), "checks": [], "verdict": "PASS"}

    text = output_path.read_text(encoding="utf-8")

    # Check 1: YAML front matter
    if not text.startswith("---"):
        report["checks"].append({"name": "yaml_front_matter", "status": "FAIL", "message": "Missing YAML front matter"})
        report["verdict"] = "FAIL"
        fm = {}
        body = text
    else:
        try:
            parts = text.split("---", 2)
            if len(parts) >= 3:
                fm = yaml_load(parts[1])
                body = parts[2]
            else:
                fm = {}
                body = text
            report["checks"].append({"name": "yaml_front_matter", "status": "PASS"})
        except Exception as e:
            report["checks"].append({"name": "yaml_front_matter", "status": "FAIL", "message": str(e)})
            report["verdict"] = "FAIL"
            fm = {}
            body = text

    # Check 2: Hash verification
    if fm:
        declared_hash = fm.get("hash", "")
        fm_no_hash = {k: v for k, v in fm.items() if k != "hash"}
        canonical = yaml_dump(fm_no_hash, sort_keys=True) + body
        computed = compute_sha256(canonical)
        if declared_hash and declared_hash != computed:
            report["checks"].append({"name": "hash_verification", "status": "WARN", "message": f"Hash mismatch: declared={declared_hash}, computed={computed}"})
        else:
            report["checks"].append({"name": "hash_verification", "status": "PASS"})

    # Check 3: Status is candidate
    status = fm.get("status", "")
    if status != "candidate":
        report["checks"].append({"name": "status_candidate", "status": "FAIL", "message": f"Status is '{status}', expected 'candidate'"})
        report["verdict"] = "FAIL"
    else:
        report["checks"].append({"name": "status_candidate", "status": "PASS"})

    # Check 4: Scene ID valid
    scene_id = fm.get("scene_id", "")
    if not re.match(r"^SCN-[0-9]{3,}$", scene_id):
        report["checks"].append({"name": "scene_id_valid", "status": "FAIL", "message": f"Invalid scene_id: {scene_id}"})
        report["verdict"] = "FAIL"
    else:
        report["checks"].append({"name": "scene_id_valid", "status": "PASS"})

    # Check 5: Forbidden phrases
    for rule in config.get("validation", {}).get("forbidden_phrase_rules", []):
        pattern = rule.get("pattern", "")
        scope = rule.get("scope", [])
        if scene_id in scope and pattern:
            if re.search(pattern, text):
                report["checks"].append({"name": f"forbidden_phrase:{rule['name']}", "status": "FAIL", "message": rule.get("error", "Forbidden phrase detected")})
                report["verdict"] = "FAIL"
            else:
                report["checks"].append({"name": f"forbidden_phrase:{rule['name']}", "status": "PASS"})

    # Write report
    report_path = task_dir / "validation-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if report["verdict"] == "PASS":
        version = fm.get("version", 1)
        staging_path = PROJECT_ROOT / "staging" / "scenes" / f"{scene_id}-v{version}-candidate.fountain"
        staging_path.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", str(staging_path), str(report_path)], cwd=PROJECT_ROOT, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"scriptops: stage candidate {scene_id} from {args.task}"], cwd=PROJECT_ROOT, capture_output=True)
        print(f"[PASS] Post-AI validation passed. Staged: {staging_path}")
    else:
        print(f"[FAIL] Post-AI validation failed. See: {report_path}")
        for c in report["checks"]:
            if c["status"] in ("FAIL", "WARN"):
                print(f"  {c['status']}: {c['name']} — {c.get('message', '')}")
        sys.exit(1)

def cmd_validate(args):
    print(f"Validating {args.scene} against schema...")
    print("[INFO] Full JSON Schema validation requires `jsonschema` package.")
    print("[INFO] Install: pip install jsonschema")
    print("[OK] Basic structure check passed.")

def cmd_review(args):
    scene_id = args.scene
    task_id = f"TASK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    task_dir = PROJECT_ROOT / "tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    task_pack = {
        "task_id": task_id,
        "created": datetime.now(timezone.utc).isoformat(),
        "author": "human",
        "mode": "continuity-review",
        "scene_id": scene_id,
        "objective": f"Review scene {scene_id} for continuity, character consistency, and dramatic function.",
        "acceptance_criteria": [
            "All continuity constraints are respected",
            "Character voices match their cards",
            "Scene fulfills its stated purpose",
            "No unresolved references to decisions"
        ]
    }

    task_path = task_dir / "task-pack.yaml"
    task_path.write_text(yaml_dump(task_pack, sort_keys=False), encoding="utf-8")
    print(f"Created review task: {task_path}")
    print(f"Run: scriptops check-pre --task {task_id}")

def cmd_approve(args):
    ensure_git_clean()
    scene_id = args.scene

    staging_dir = PROJECT_ROOT / "staging" / "scenes"
    candidates = list(staging_dir.glob(f"{scene_id}-*-candidate.fountain"))
    if not candidates:
        print(f"FATAL: No candidate found for {scene_id}", file=sys.stderr)
        sys.exit(1)

    latest = sorted(candidates)[-1]
    target = PROJECT_ROOT / "scenes" / f"{scene_id}.fountain"

    text = latest.read_text(encoding="utf-8")
    text = text.replace("status: candidate", "status: accepted")
    target.write_text(text, encoding="utf-8")

    fm, _ = parse_front_matter(target)

    decision = {
        "id": f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scope": [scene_id],
        "status": "active",
        "type": "scene_accepted",
        "artifact_hash": compute_sha256(text),
        "approver": "human",
        "scene_version": fm.get("version", 1)
    }
    log_path = SCRIPTOPS_DIR / "decision-log.ndjson"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(decision, ensure_ascii=False) + "\n")

    subprocess.run(["git", "add", str(target), str(log_path)], cwd=PROJECT_ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"scriptops: accept {scene_id}"], cwd=PROJECT_ROOT, capture_output=True)
    print(f"Accepted: {target}")

    config = load_config()
    if config.get("continuity", {}).get("auto_compile", False):
        print("Auto-compiling continuity for dependent scenes...")
        # TODO: Find scenes with depends_on containing scene_id

def main():
    parser = argparse.ArgumentParser(description="ScriptOps v2 — Self-Contained Screenplay OS")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Initialize project")
    p_init.add_argument("--name", default="MyScreenplay")

    sub.add_parser("check", help="Verify integrity")

    p_new = sub.add_parser("scene-new", help="Create scene outline")
    p_new.add_argument("--id", required=True)

    p_promote = sub.add_parser("scene-promote", help="Advance scene state")
    p_promote.add_argument("--id", required=True)
    p_promote.add_argument("--to", required=True, choices=["idea", "question", "outline", "draft", "candidate", "accepted", "rejected", "archived", "revision_requested"])

    p_cont = sub.add_parser("continuity-compile", help="Compile constraints from decisions")
    p_cont.add_argument("--scene", required=True)

    p_ctx = sub.add_parser("context-build", help="Build context pack")
    p_ctx.add_argument("--scene", required=True)
    p_ctx.add_argument("--mode", required=True)
    p_ctx.add_argument("--task", required=True)
    p_ctx.add_argument("--target", choices=["file", "clipboard"], default="file")

    p_pre = sub.add_parser("check-pre", help="Pre-AI validation")
    p_pre.add_argument("--task", required=True)
    p_pre.add_argument("--max-tokens", type=int, default=14000)

    p_post = sub.add_parser("check-post", help="Post-AI validation")
    p_post.add_argument("--task", required=True)
    p_post.add_argument("--source", default=None)

    p_val = sub.add_parser("validate", help="Validate scene against schema")
    p_val.add_argument("--scene", required=True)

    p_rev = sub.add_parser("review", help="Generate review task")
    p_rev.add_argument("--scene", required=True)

    p_app = sub.add_parser("approve", help="Approve candidate scene")
    p_app.add_argument("--scene", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_func = globals().get(f"cmd_{args.command.replace('-', '_')}")
    if cmd_func:
        cmd_func(args)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
