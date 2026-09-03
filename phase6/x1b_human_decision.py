#!/usr/bin/env python3
"""X1B Human decision authorship V2.

Authority chain:
Human GitHub review -> verified admission -> prospective Git commit -> atomic main CAS.

The module is intentionally stdlib-only until the isolated network-child dispatch.
Parent-side scene projection lazily imports PyYAML, matching the active ScriptOps shim.
"""
from __future__ import annotations

import base64
import contextlib
import fcntl
import hashlib
import http.client
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import quote

SOURCE_ROOT = Path(__file__).resolve().parents[1]
TRUSTED_HUMAN_GITHUB_USER_ID = 226907434
EVIDENCE_REPOSITORY = "FJ899/8"
SCRIPTOPS_REPOSITORY = "FJ899/scriptops"
REVIEW_MARKER_VERSION = "X1B-HUMAN-DECISION-V2"
REQUEST_SCHEMA = "x1b-human-decision-request/v2"
ADMISSION_SCHEMA = "x1b-operation-admission/v2"
DECISION_SCHEMA = "scriptops-x1b-decision/v2"
CHILD_REQUEST_SCHEMA = "x1b-github-reader-child-request/v1"
CHILD_RESULT_SCHEMA = "x1b-github-reader-child-result/v1"
API_VERSION = "2026-03-10"
USER_AGENT = "scriptops-x1b-human-decision/2"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SCENE_ID = re.compile(r"^SCN-[0-9]{3,}$")
MAX_HTTP_BODY = 2 * 1024 * 1024
MAX_PR_NUMBER = 2_147_483_647
MACHINE_NAME = "ScriptOps X1B Executor"
MACHINE_EMAIL = "scriptops-x1b@example.invalid"


class X1BError(RuntimeError):
    """Fail-closed X1B rejection."""


class RecoveryRequired(X1BError):
    """Canonical ref may have advanced, but post-effect truth is not proven."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise X1BError(f"non-canonical JSON value: {exc}") from exc
    return text.encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        ) + "\n"
    except (TypeError, ValueError) as exc:
        raise X1BError(f"non-readable JSON value: {exc}") from exc
    return text.encode("utf-8")


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise X1BError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_strict(data: bytes) -> Any:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise X1BError(f"JSON is not UTF-8: {exc}") from exc
    try:
        return json.loads(text, object_pairs_hook=_pairs_no_duplicates)
    except X1BError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise X1BError(f"invalid JSON: {exc}") from exc


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise X1BError(
            f"{label} keys mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )


def _validate_repo_path(path: Any, label: str) -> str:
    if not isinstance(path, str) or not path:
        raise X1BError(f"{label} must be non-empty string")
    if "\\" in path or path.startswith("/"):
        raise X1BError(f"{label} must be relative POSIX path")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise X1BError(f"{label} has forbidden path component")
    return path


def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise X1BError("submitted_at must be non-empty string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise X1BError("submitted_at is not parseable ISO-8601") from exc
    if parsed.tzinfo is None:
        raise X1BError("submitted_at must be timezone-aware")
    return parsed


def _git_binary() -> str:
    for candidate in ("/usr/bin/git", "/bin/git"):
        path = Path(candidate)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve())
    found = shutil.which("git", path="/usr/bin:/bin:/usr/local/bin")
    if not found:
        raise X1BError("trusted Git executable not found in fixed system paths")
    return str(Path(found).resolve())


@dataclass(frozen=True)
class AnchoredGitV2:
    root: Path
    git_bin: str
    git_dir: Path
    common_dir: Path

    @staticmethod
    def discover(root: Path = SOURCE_ROOT) -> "AnchoredGitV2":
        root = root.resolve()
        git_bin = _git_binary()
        env = AnchoredGitV2._base_env()

        def discover_cmd(*args: str) -> str:
            cp = subprocess.run(
                [git_bin, "-C", str(root), *args],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            if cp.returncode:
                detail = cp.stderr.strip() or cp.stdout.strip()
                raise X1BError(f"Git discovery failed: {detail}")
            return cp.stdout.strip()

        top = Path(discover_cmd("rev-parse", "--show-toplevel")).resolve()
        if top != root:
            raise X1BError(f"Git top-level mismatch: expected={root} actual={top}")
        git_dir = Path(discover_cmd("rev-parse", "--absolute-git-dir")).resolve()
        common_raw = discover_cmd("rev-parse", "--path-format=absolute", "--git-common-dir")
        common_dir = Path(common_raw).resolve()
        if not git_dir.exists() or not common_dir.exists():
            raise X1BError("anchored Git directory does not exist")
        return AnchoredGitV2(root=root, git_bin=git_bin, git_dir=git_dir, common_dir=common_dir)

    @staticmethod
    def _base_env(extra: dict[str, str] | None = None) -> dict[str, str]:
        env = {
            "PATH": "/usr/bin:/bin:/usr/local/bin",
            "LC_ALL": "C",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        }
        if extra:
            env.update(extra)
        return env

    def run(
        self,
        *args: str,
        input_bytes: bytes | None = None,
        check: bool = True,
        index_file: Path | None = None,
        env_extra: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        env = self._base_env(env_extra)
        if index_file is not None:
            env["GIT_INDEX_FILE"] = str(index_file)
        cp = subprocess.run(
            [
                self.git_bin,
                f"--git-dir={self.git_dir}",
                f"--work-tree={self.root}",
                *args,
            ],
            env=env,
            input=input_bytes,
            capture_output=True,
            check=False,
        )
        if check and cp.returncode:
            detail = cp.stderr.decode("utf-8", "replace").strip() or cp.stdout.decode(
                "utf-8", "replace"
            ).strip()
            raise X1BError(f"git {' '.join(args)} failed: {detail}")
        return cp

    def text(self, *args: str, check: bool = True, **kwargs: Any) -> str:
        cp = self.run(*args, check=check, **kwargs)
        try:
            return cp.stdout.decode("utf-8").strip()
        except UnicodeDecodeError as exc:
            raise X1BError("Git text output is not UTF-8") from exc

    def main_head(self) -> str:
        value = self.text("rev-parse", "refs/heads/main")
        if not HEX40.fullmatch(value):
            raise X1BError("main ref is not exact 40-hex")
        return value

    def direct_main_head(self) -> str:
        symbolic = self.run("symbolic-ref", "-q", "refs/heads/main", check=False)
        if symbolic.returncode == 0:
            target = symbolic.stdout.decode("utf-8", "replace").strip()
            raise X1BError(f"refs/heads/main must be a direct ref, got symbolic target {target!r}")
        if symbolic.returncode != 1:
            detail = symbolic.stderr.decode("utf-8", "replace").strip()
            raise X1BError(f"cannot establish direct refs/heads/main: {detail}")
        value = self.text("show-ref", "--verify", "--hash", "refs/heads/main")
        if not HEX40.fullmatch(value):
            raise X1BError("direct refs/heads/main is not exact 40-hex")
        return value

    def require_direct_main(self, expected: str | None = None) -> str:
        value = self.direct_main_head()
        if expected is not None and value != expected:
            raise X1BError(
                f"direct refs/heads/main mismatch: expected={expected} actual={value}"
            )
        return value

    def require_symbolic_main(self) -> None:
        value = self.text("symbolic-ref", "-q", "HEAD")
        if value != "refs/heads/main":
            raise X1BError(f"HEAD must be refs/heads/main, got {value!r}")

    def require_clean(self) -> None:
        status = self.text("status", "--porcelain=v1", "--untracked-files=all")
        if status:
            raise X1BError(f"working tree/index must be clean: {status.splitlines()!r}")

    def require_no_replace_refs(self) -> None:
        refs = self.text("for-each-ref", "--format=%(refname)", "refs/replace/")
        if refs:
            raise X1BError("refs/replace/* must be empty")

    def commit_file(self, commit: str, path: str, *, allow_absent: bool = False) -> bytes:
        exists = self.run("cat-file", "-e", f"{commit}:{path}", check=False)
        if exists.returncode:
            if allow_absent:
                return b""
            raise X1BError(f"required base path absent: {path}")
        return self.run("show", f"{commit}:{path}").stdout

    def tree_entry(self, commit: str, path: str) -> tuple[str, str]:
        out = self.text("ls-tree", commit, "--", path)
        if not out:
            raise X1BError(f"tree entry absent: {path}")
        line = out.splitlines()
        if len(line) != 1:
            raise X1BError(f"tree entry ambiguous: {path}")
        left, returned = line[0].split("\t", 1)
        mode, kind, oid = left.split(" ")
        if returned != path or kind != "blob" or not HEX40.fullmatch(oid):
            raise X1BError(f"invalid tree entry: {path}")
        return mode, oid

    def blob(self, oid: str) -> bytes:
        return self.run("cat-file", "blob", oid).stdout

    def cas_main(self, new_oid: str, old_oid: str) -> bool:
        try:
            self.require_direct_main(old_oid)
        except X1BError:
            return False
        cp = self.run(
            "update-ref",
            "--no-deref",
            "refs/heads/main",
            new_oid,
            old_oid,
            check=False,
        )
        return cp.returncode == 0


@contextlib.contextmanager
def x1b_lock(git: AnchoredGitV2) -> Iterator[None]:
    path = git.common_dir / "scriptops-x1b.lock"
    handle = path.open("a+b")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise X1BError("BLOCKED_CONCURRENT_X1B") from exc
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


@dataclass(frozen=True)
class LocalBinding:
    base_head: str
    scene_id: str
    candidate_path: str
    candidate_sha256: str
    candidate_bytes: bytes
    impact_report_path: str
    impact_report_sha256: str
    impact_bytes: bytes
    accepted_scene_path: str
    accepted_scene_sha256: str
    accepted_scene_bytes: bytes


def _yaml_module() -> Any:
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise X1BError("PyYAML is required for ScriptOps scene projection") from exc
    return yaml


def _parse_front_matter_bytes(data: bytes) -> tuple[dict[str, Any], str]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise X1BError("scene candidate is not UTF-8") from exc
    if not text.startswith("---"):
        raise X1BError("scene candidate has no YAML front matter")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise X1BError("scene candidate front matter is malformed")
    yaml = _yaml_module()
    value = yaml.safe_load(parts[1])
    if not isinstance(value, dict):
        raise X1BError("scene front matter is not an object")
    return value, parts[2]


def project_accepted_scene(candidate_bytes: bytes, scene_id: str) -> bytes:
    fm, body = _parse_front_matter_bytes(candidate_bytes)
    if fm.get("scene_id") != scene_id:
        raise X1BError("candidate scene_id mismatch")
    if fm.get("status") != "candidate":
        raise X1BError("only candidate status can be projected")
    yaml = _yaml_module()
    final = dict(fm)
    final["status"] = "accepted"
    without_hash = dict(final)
    without_hash.pop("hash", None)
    canonical = yaml.dump(
        without_hash,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ) + body
    final["hash"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    text = "---\n" + yaml.dump(
        final,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ) + "---" + body
    return text.encode("utf-8")


def _latest_candidate(root: Path, scene_id: str) -> Path:
    pattern = re.compile(rf"^{re.escape(scene_id)}-v([1-9][0-9]*)-candidate\.fountain$")
    staging = root / "staging" / "scenes"
    matches: list[tuple[int, Path]] = []
    if staging.is_dir():
        for path in staging.iterdir():
            match = pattern.fullmatch(path.name)
            if match and path.is_file() and not path.is_symlink():
                matches.append((int(match.group(1)), path))
    if not matches:
        raise X1BError(f"no staged candidate for {scene_id}")
    return max(matches, key=lambda item: item[0])[1]


def _matching_impact(root: Path, scene_id: str, candidate_bytes: bytes) -> Path:
    raw = _sha256(candidate_bytes)
    legacy = "sha256:" + raw
    matches: list[Path] = []
    for path in (root / "tasks").glob("*/impact-report.json"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            data = parse_json_strict(path.read_bytes())
        except X1BError:
            continue
        if not isinstance(data, dict):
            continue
        candidate = data.get("candidate")
        if (
            data.get("scene_id") == scene_id
            and data.get("status") == "REVIEW_REQUIRED"
            and isinstance(candidate, dict)
            and candidate.get("file_sha256") in {raw, legacy}
        ):
            matches.append(path)
    if not matches:
        raise X1BError("no exact REVIEW_REQUIRED impact report for candidate")
    return sorted(matches, key=lambda p: p.as_posix())[-1]


def local_preflight(git: AnchoredGitV2, scene_id: str) -> LocalBinding:
    if not SCENE_ID.fullmatch(scene_id):
        raise X1BError("invalid scene id")
    git.require_symbolic_main()
    git.require_clean()
    git.require_no_replace_refs()
    base = git.require_direct_main()
    candidate = _latest_candidate(git.root, scene_id)
    candidate_bytes = candidate.read_bytes()
    impact = _matching_impact(git.root, scene_id, candidate_bytes)
    impact_bytes = impact.read_bytes()
    accepted = project_accepted_scene(candidate_bytes, scene_id)
    return LocalBinding(
        base_head=base,
        scene_id=scene_id,
        candidate_path=candidate.relative_to(git.root).as_posix(),
        candidate_sha256=_sha256(candidate_bytes),
        candidate_bytes=candidate_bytes,
        impact_report_path=impact.relative_to(git.root).as_posix(),
        impact_report_sha256=_sha256(impact_bytes),
        impact_bytes=impact_bytes,
        accepted_scene_path=f"scenes/{scene_id}.fountain",
        accepted_scene_sha256=_sha256(accepted),
        accepted_scene_bytes=accepted,
    )


def expected_material_effect(local: LocalBinding) -> dict[str, Any]:
    return {
        "effect_version": "scriptops-x1b-scene-accept/v2",
        "canonical_ref": "refs/heads/main",
        "old_ref": local.base_head,
        "changed_paths": [
            ".scriptops/decision-log.ndjson",
            local.accepted_scene_path,
        ],
        "canonical_scene": {
            "path": local.accepted_scene_path,
            "mode": "100644",
            "sha256": local.accepted_scene_sha256,
        },
        "decision_log": {
            "path": ".scriptops/decision-log.ndjson",
            "mode": "100644",
            "operation": "append-one-x1b-decision-record",
            "human_github_user_id": TRUSTED_HUMAN_GITHUB_USER_ID,
            "request_binding": "request_sha256",
            "review_binding": "review-id-and-immutable-review-commit",
        },
        "canonicalization": "git-update-ref-compare-and-swap",
    }


def build_request(
    local: LocalBinding,
    proposal_rationale: str,
    request_nonce: str,
) -> tuple[dict[str, Any], bytes, str]:
    if not isinstance(proposal_rationale, str):
        raise X1BError("proposal_rationale must be string")
    if not HEX64.fullmatch(request_nonce):
        raise X1BError("request_nonce must be 64 lowercase hex")
    scene = local.scene_id
    payload = {
        "schema_version": REQUEST_SCHEMA,
        "request_nonce": request_nonce,
        "scriptops_repository": SCRIPTOPS_REPOSITORY,
        "scriptops_base_head": local.base_head,
        "scene_id": scene,
        "scope": [scene],
        "candidate_path": local.candidate_path,
        "candidate_sha256": local.candidate_sha256,
        "impact_report_path": local.impact_report_path,
        "impact_report_sha256": local.impact_report_sha256,
        "accepted_scene_path": local.accepted_scene_path,
        "accepted_scene_sha256": local.accepted_scene_sha256,
        "proposal_rationale": proposal_rationale,
        "decision_statement": (
            f"Approve accepting exactly the presented scene file for {scene} "
            "under the material effect below."
        ),
        "known_material_consequences": [
            f"replace {local.accepted_scene_path} with the exact presented accepted-scene bytes",
            "append exactly one derived X1B Human-decision provenance record to .scriptops/decision-log.ndjson",
            "atomically advance local FJ899/scriptops refs/heads/main from the exact Human-bound base to one commit containing exactly those two tracked logical changes",
        ],
        "material_effect": expected_material_effect(local),
        "human_authority": {
            "channel": "github-pull-request-review",
            "evidence_repository": EVIDENCE_REPOSITORY,
            "human_github_user_id": TRUSTED_HUMAN_GITHUB_USER_ID,
            "display_login_at_brief_freeze": "litrgratis-pixel",
            "review_state": "APPROVED",
            "review_marker_version": REVIEW_MARKER_VERSION,
        },
    }
    digest = _sha256(canonical_json_bytes(payload))
    return payload, pretty_json_bytes(payload), digest


REQUEST_KEYS = {
    "schema_version",
    "request_nonce",
    "scriptops_repository",
    "scriptops_base_head",
    "scene_id",
    "scope",
    "candidate_path",
    "candidate_sha256",
    "impact_report_path",
    "impact_report_sha256",
    "accepted_scene_path",
    "accepted_scene_sha256",
    "proposal_rationale",
    "decision_statement",
    "known_material_consequences",
    "material_effect",
    "human_authority",
}


def validate_request(
    request_bytes: bytes,
    expected_digest: str,
    accepted_scene_bytes: bytes,
    local: LocalBinding,
) -> dict[str, Any]:
    value = parse_json_strict(request_bytes)
    if not isinstance(value, dict):
        raise X1BError("request must be object")
    _require_exact_keys(value, REQUEST_KEYS, "request")
    if _sha256(canonical_json_bytes(value)) != expected_digest:
        raise X1BError("request digest mismatch")
    if pretty_json_bytes(value) != request_bytes:
        raise X1BError("request.json is not exact pretty V2 bytes")
    if value.get("schema_version") != REQUEST_SCHEMA:
        raise X1BError("wrong request schema")
    if not HEX64.fullmatch(str(value.get("request_nonce", ""))):
        raise X1BError("invalid request nonce")
    if value.get("scriptops_repository") != SCRIPTOPS_REPOSITORY:
        raise X1BError("wrong ScriptOps repository")
    if value.get("scriptops_base_head") != local.base_head:
        raise X1BError("ScriptOps base drift")
    if value.get("scene_id") != local.scene_id or value.get("scope") != [local.scene_id]:
        raise X1BError("scene/scope mismatch")
    if _validate_repo_path(value.get("candidate_path"), "candidate_path") != local.candidate_path:
        raise X1BError("candidate path drift")
    if value.get("candidate_sha256") != local.candidate_sha256:
        raise X1BError("candidate digest drift")
    if _validate_repo_path(value.get("impact_report_path"), "impact_report_path") != local.impact_report_path:
        raise X1BError("impact path drift")
    if value.get("impact_report_sha256") != local.impact_report_sha256:
        raise X1BError("impact digest drift")
    if value.get("accepted_scene_path") != local.accepted_scene_path:
        raise X1BError("accepted-scene path drift")
    if value.get("accepted_scene_sha256") != local.accepted_scene_sha256:
        raise X1BError("accepted-scene digest drift")
    if accepted_scene_bytes != local.accepted_scene_bytes:
        raise X1BError("Human-presented accepted-scene bytes differ from local projection")
    if _sha256(accepted_scene_bytes) != value.get("accepted_scene_sha256"):
        raise X1BError("presented accepted-scene SHA mismatch")
    if value.get("decision_statement") != (
        f"Approve accepting exactly the presented scene file for {local.scene_id} under the material effect below."
    ):
        raise X1BError("decision statement mismatch")
    expected_consequences = build_request(local, str(value.get("proposal_rationale", "")), str(value["request_nonce"]))[0][
        "known_material_consequences"
    ]
    if value.get("known_material_consequences") != expected_consequences:
        raise X1BError("known material consequences mismatch")
    if value.get("material_effect") != expected_material_effect(local):
        raise X1BError("material effect mismatch")
    if value.get("human_authority") != {
        "channel": "github-pull-request-review",
        "evidence_repository": EVIDENCE_REPOSITORY,
        "human_github_user_id": TRUSTED_HUMAN_GITHUB_USER_ID,
        "display_login_at_brief_freeze": "litrgratis-pixel",
        "review_state": "APPROVED",
        "review_marker_version": REVIEW_MARKER_VERSION,
    }:
        raise X1BError("Human authority object mismatch")
    if not isinstance(value.get("proposal_rationale"), str):
        raise X1BError("proposal_rationale must be string")
    return value


def _review_body(digest: str) -> str:
    return f"{REVIEW_MARKER_VERSION}\nrequest_sha256={digest}\ndecision=APPROVE"


def _normalize_reviews(reviews: list[Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], str]:
    normalized: list[dict[str, Any]] = []
    human: list[tuple[datetime, int, dict[str, Any], dict[str, Any]]] = []
    ids: set[int] = set()
    for row in reviews:
        if not isinstance(row, dict):
            raise X1BError("review row must be object")
        rid = row.get("id")
        user = row.get("user")
        state = row.get("state")
        submitted = row.get("submitted_at")
        body = row.get("body")
        commit_id = row.get("commit_id")
        if not isinstance(rid, int) or rid <= 0 or rid in ids:
            raise X1BError("review id invalid/duplicate")
        ids.add(rid)
        if not isinstance(user, dict) or not isinstance(user.get("id"), int):
            raise X1BError("review user.id missing")
        user_id = user["id"]
        login = user.get("login")
        node_id = user.get("node_id")
        if not isinstance(login, str):
            raise X1BError("review user.login missing")
        if node_id is not None and not isinstance(node_id, str):
            raise X1BError("review user.node_id malformed")
        if not isinstance(state, str) or not isinstance(body, str):
            raise X1BError("review state/body malformed")
        when = _parse_time(submitted)
        commit_norm = commit_id if isinstance(commit_id, str) else ""
        normalized_row = {
            "numeric_id": rid,
            "user_id": user_id,
            "user_login_observed": login,
            "user_node_id_or_empty": node_id or "",
            "state": state,
            "commit_id_or_empty": commit_norm,
            "submitted_at": submitted,
            "body_sha256": _sha256(body.encode("utf-8")),
        }
        normalized.append(normalized_row)
        if user_id != TRUSTED_HUMAN_GITHUB_USER_ID and body.startswith(REVIEW_MARKER_VERSION):
            raise X1BError("reserved X1B marker used by non-Human account")
        if user_id == TRUSTED_HUMAN_GITHUB_USER_ID:
            if state not in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED", "COMMENTED"}:
                raise X1BError(f"unknown trusted-Human review state: {state}")
            if state in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
                if not HEX40.fullmatch(commit_norm):
                    raise X1BError("authority-relevant review commit_id invalid")
                human.append((when, rid, row, normalized_row))
    if not human:
        raise X1BError("no authority-relevant Human review")
    human.sort(key=lambda item: (item[0], item[1]))
    latest = human[-1][2]
    if latest.get("state") != "APPROVED":
        raise X1BError(f"current Human decision is {latest.get('state')}, not APPROVED")
    body = latest["body"]
    match = re.fullmatch(
        rf"{re.escape(REVIEW_MARKER_VERSION)}\nrequest_sha256=([0-9a-f]{{64}})\ndecision=APPROVE",
        body,
    )
    if not match:
        raise X1BError("current Human APPROVED body is not exact V2 marker")
    normalized_by_id = sorted(normalized, key=lambda item: item["numeric_id"])
    human_rows = [item[3] for item in human]
    review_response_digest = _sha256(canonical_json_bytes(normalized_by_id))
    human_review_set_digest = _sha256(canonical_json_bytes(human_rows))
    return normalized_by_id, human_rows, latest, match.group(1)


def select_human_review(reviews_raw: bytes) -> dict[str, Any]:
    value = parse_json_strict(reviews_raw)
    if not isinstance(value, list):
        raise X1BError("review response must be array")
    if len(value) >= 100:
        raise X1BError("review response completeness cap exceeded")
    normalized, human, latest, digest = _normalize_reviews(value)
    return {
        "review_response_digest": _sha256(canonical_json_bytes(normalized)),
        "human_review_set_digest": _sha256(canonical_json_bytes(human)),
        "latest": latest,
        "request_sha256": digest,
    }


def _read_http_body(response: http.client.HTTPResponse) -> bytes:
    length = response.getheader("Content-Length")
    if length is not None:
        try:
            if int(length) > MAX_HTTP_BODY:
                raise X1BError("HTTP body exceeds bound")
        except ValueError as exc:
            raise X1BError("invalid Content-Length") from exc
    data = response.read(MAX_HTTP_BODY + 1)
    if len(data) > MAX_HTTP_BODY:
        raise X1BError("HTTP body exceeds bound")
    return data


def _github_get(path: str, context: ssl.SSLContext) -> tuple[bytes, dict[str, str]]:
    conn = http.client.HTTPSConnection("api.github.com", 443, context=context, timeout=20)
    try:
        conn.request(
            "GET",
            path,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": USER_AGENT,
            },
        )
        response = conn.getresponse()
        body = _read_http_body(response)
        headers = {key.lower(): value for key, value in response.getheaders()}
        if 300 <= response.status < 400:
            raise X1BError("GitHub redirect rejected")
        if response.status != 200:
            raise X1BError(f"GitHub HTTP status {response.status}")
        return body, headers
    finally:
        conn.close()


def _decode_contents_response(raw: bytes, expected_path: str) -> bytes:
    obj = parse_json_strict(raw)
    if not isinstance(obj, dict):
        raise X1BError("GitHub contents response must be object")
    if obj.get("type") != "file" or obj.get("path") != expected_path or obj.get("encoding") != "base64":
        raise X1BError("GitHub contents response identity mismatch")
    content = obj.get("content")
    if not isinstance(content, str):
        raise X1BError("GitHub contents base64 missing")
    try:
        data = base64.b64decode(content, validate=False)
    except (ValueError, base64.binascii.Error) as exc:
        raise X1BError("GitHub contents base64 invalid") from exc
    if len(data) > MAX_HTTP_BODY:
        raise X1BError("GitHub file exceeds bound")
    return data


def _network_child() -> int:
    try:
        request_raw = sys.stdin.buffer.read(4097)
        if len(request_raw) > 4096:
            raise X1BError("child request too large")
        request = parse_json_strict(request_raw)
        if not isinstance(request, dict):
            raise X1BError("child request must be object")
        _require_exact_keys(request, {"schema_version", "decision_pr"}, "child request")
        if request.get("schema_version") != CHILD_REQUEST_SCHEMA:
            raise X1BError("child request schema mismatch")
        pr = request.get("decision_pr")
        if not isinstance(pr, int) or not (1 <= pr <= MAX_PR_NUMBER):
            raise X1BError("decision_pr invalid")

        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        stats = context.cert_store_stats()
        if not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED:
            raise X1BError("TLS verification invariants not active")
        if int(context.minimum_version) < int(ssl.TLSVersion.TLSv1_2):
            raise X1BError("TLS minimum below 1.2")
        if stats.get("x509_ca", 0) <= 0:
            raise X1BError("isolated child has no default CA roots")

        review_path = f"/repos/FJ899/8/pulls/{pr}/reviews?per_page=100&page=1"
        reviews_raw, review_headers = _github_get(review_path, context)
        link = review_headers.get("link", "")
        if 'rel="next"' in link:
            raise X1BError("review pagination ambiguity")
        selected = select_human_review(reviews_raw)
        latest = selected["latest"]
        digest = selected["request_sha256"]
        commit_id = latest["commit_id"]

        request_path = f"decisions/x1b/requests/{digest}/request.json"
        scene_path = f"decisions/x1b/requests/{digest}/accepted-scene.fountain"
        request_api = (
            "/repos/FJ899/8/contents/" + quote(request_path, safe="/") + f"?ref={commit_id}"
        )
        scene_api = (
            "/repos/FJ899/8/contents/" + quote(scene_path, safe="/") + f"?ref={commit_id}"
        )
        request_raw_api, _ = _github_get(request_api, context)
        scene_raw_api, _ = _github_get(scene_api, context)
        request_bytes = _decode_contents_response(request_raw_api, request_path)
        scene_bytes = _decode_contents_response(scene_raw_api, scene_path)

        result = {
            "schema_version": CHILD_RESULT_SCHEMA,
            "review_response_raw_b64": base64.b64encode(reviews_raw).decode("ascii"),
            "review_response_digest": selected["review_response_digest"],
            "human_review_set_digest": selected["human_review_set_digest"],
            "human_review_numeric_id": latest["id"],
            "human_github_user_id": latest["user"]["id"],
            "human_review_login_observed": latest["user"]["login"],
            "human_review_node_id_observed_or_empty": latest["user"].get("node_id") or "",
            "human_review_state": latest["state"],
            "human_review_commit_id": latest["commit_id"],
            "human_review_submitted_at": latest["submitted_at"],
            "human_review_body_b64": base64.b64encode(latest["body"].encode("utf-8")).decode("ascii"),
            "request_sha256": digest,
            "request_json_raw_b64": base64.b64encode(request_bytes).decode("ascii"),
            "accepted_scene_raw_b64": base64.b64encode(scene_bytes).decode("ascii"),
            "tls_observation": {
                "openssl_version": ssl.OPENSSL_VERSION,
                "default_verify_paths": list(ssl.get_default_verify_paths()),
                "cert_store_stats": stats,
                "minimum_version": int(context.minimum_version),
                "verify_mode": int(context.verify_mode),
                "check_hostname": context.check_hostname,
                "environment_keys": sorted(os.environ),
            },
        }
        sys.stdout.buffer.write(canonical_json_bytes(result))
        return 0
    except Exception as exc:  # fail closed in isolated process
        print(f"X1B CHILD DENY: {exc}", file=sys.stderr)
        return 2


def network_child_env() -> dict[str, str]:
    return {"X1B_NETWORK_CHILD": "1"}


def run_network_child(decision_pr: int) -> dict[str, Any]:
    if not isinstance(decision_pr, int) or not (1 <= decision_pr <= MAX_PR_NUMBER):
        raise X1BError("decision_pr must be positive integer")
    executable = str(Path(sys.executable).resolve())
    program = str(Path(__file__).resolve())
    request = canonical_json_bytes(
        {"schema_version": CHILD_REQUEST_SCHEMA, "decision_pr": decision_pr}
    )
    try:
        cp = subprocess.run(
            [executable, "-I", program, "--_x1b-github-reader-child"],
            env=network_child_env(),
            input=request,
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise X1BError(f"isolated GitHub reader failed: {exc}") from exc
    if cp.returncode:
        detail = cp.stderr.decode("utf-8", "replace").strip()
        raise X1BError(f"isolated GitHub reader denied: {detail}")
    result = parse_json_strict(cp.stdout)
    if not isinstance(result, dict):
        raise X1BError("child result must be object")
    return result


CHILD_RESULT_KEYS = {
    "schema_version",
    "review_response_raw_b64",
    "review_response_digest",
    "human_review_set_digest",
    "human_review_numeric_id",
    "human_github_user_id",
    "human_review_login_observed",
    "human_review_node_id_observed_or_empty",
    "human_review_state",
    "human_review_commit_id",
    "human_review_submitted_at",
    "human_review_body_b64",
    "request_sha256",
    "request_json_raw_b64",
    "accepted_scene_raw_b64",
    "tls_observation",
}


def _b64_field(result: dict[str, Any], key: str) -> bytes:
    value = result.get(key)
    if not isinstance(value, str):
        raise X1BError(f"child result {key} missing")
    try:
        data = base64.b64decode(value, validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise X1BError(f"child result {key} invalid base64") from exc
    if len(data) > MAX_HTTP_BODY:
        raise X1BError(f"child result {key} exceeds bound")
    return data


def admission_from_evidence(
    local: LocalBinding,
    decision_pr: int,
    reviews_raw: bytes,
    request_bytes: bytes,
    accepted_scene_bytes: bytes,
) -> tuple[dict[str, Any], dict[str, Any]]:
    selected = select_human_review(reviews_raw)
    latest = selected["latest"]
    digest = selected["request_sha256"]
    request = validate_request(request_bytes, digest, accepted_scene_bytes, local)
    body = latest["body"]
    admission: dict[str, Any] = {
        "admission_version": ADMISSION_SCHEMA,
        "request_sha256": digest,
        "decision_repository": EVIDENCE_REPOSITORY,
        "decision_pr": decision_pr,
        "human_github_user_id": TRUSTED_HUMAN_GITHUB_USER_ID,
        "human_review_numeric_id": latest["id"],
        "human_review_commit_id": latest["commit_id"],
        "human_review_submitted_at": latest["submitted_at"],
        "human_review_body_sha256": _sha256(body.encode("utf-8")),
        "human_review_user_login_observed": latest["user"]["login"],
        "human_review_user_node_id_observed_or_empty": latest["user"].get("node_id") or "",
        "review_response_digest": selected["review_response_digest"],
        "human_review_set_digest": selected["human_review_set_digest"],
        "scriptops_repository": SCRIPTOPS_REPOSITORY,
        "scriptops_base_head": local.base_head,
        "scene_id": local.scene_id,
        "scope": [local.scene_id],
        "candidate_path": local.candidate_path,
        "candidate_sha256": local.candidate_sha256,
        "impact_report_path": local.impact_report_path,
        "impact_report_sha256": local.impact_report_sha256,
        "accepted_scene_path": local.accepted_scene_path,
        "accepted_scene_sha256": local.accepted_scene_sha256,
        "material_effect_digest": _sha256(canonical_json_bytes(request["material_effect"])),
    }
    identity = dict(admission)
    admission["admission_id"] = "x1b:v2:" + _sha256(canonical_json_bytes(identity))
    admission["admission_digest"] = _sha256(canonical_json_bytes(admission))
    return admission, request


def admission_from_child_result(
    local: LocalBinding,
    decision_pr: int,
    result: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_exact_keys(result, CHILD_RESULT_KEYS, "child result")
    if result.get("schema_version") != CHILD_RESULT_SCHEMA:
        raise X1BError("child result schema mismatch")
    reviews_raw = _b64_field(result, "review_response_raw_b64")
    request_bytes = _b64_field(result, "request_json_raw_b64")
    scene_bytes = _b64_field(result, "accepted_scene_raw_b64")
    body_bytes = _b64_field(result, "human_review_body_b64")
    admission, request = admission_from_evidence(
        local, decision_pr, reviews_raw, request_bytes, scene_bytes
    )
    selected = select_human_review(reviews_raw)
    latest = selected["latest"]
    checks = {
        "review_response_digest": selected["review_response_digest"],
        "human_review_set_digest": selected["human_review_set_digest"],
        "human_review_numeric_id": latest["id"],
        "human_github_user_id": latest["user"]["id"],
        "human_review_login_observed": latest["user"]["login"],
        "human_review_node_id_observed_or_empty": latest["user"].get("node_id") or "",
        "human_review_state": latest["state"],
        "human_review_commit_id": latest["commit_id"],
        "human_review_submitted_at": latest["submitted_at"],
        "request_sha256": selected["request_sha256"],
    }
    for key, expected in checks.items():
        if result.get(key) != expected:
            raise X1BError(f"child result self-report mismatch: {key}")
    if body_bytes.decode("utf-8") != latest["body"]:
        raise X1BError("child Human review body transport mismatch")
    tls = result.get("tls_observation")
    if not isinstance(tls, dict):
        raise X1BError("TLS observation missing")
    if tls.get("check_hostname") is not True:
        raise X1BError("TLS hostname verification observation false")
    if tls.get("verify_mode") != int(ssl.CERT_REQUIRED):
        raise X1BError("TLS CERT_REQUIRED observation missing")
    if int(tls.get("minimum_version", 0)) < int(ssl.TLSVersion.TLSv1_2):
        raise X1BError("TLS minimum observation below 1.2")
    env_keys = tls.get("environment_keys")
    if not isinstance(env_keys, list) or any(
        key in env_keys
        for key in (
            "SSL_CERT_FILE",
            "SSL_CERT_DIR",
            "OPENSSL_CONF",
            "OPENSSL_MODULES",
            "GITHUB_TOKEN",
            "GH_TOKEN",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "PYTHONPATH",
            "PYTHONHOME",
        )
    ):
        raise X1BError("isolated child environment observation contains forbidden authority input")
    return admission, request


def _scan_replay(log_bytes: bytes, request_sha256: str) -> None:
    if log_bytes and not log_bytes.endswith(b"\n"):
        raise X1BError("decision log is not newline-terminated NDJSON")
    for line in log_bytes.splitlines():
        if not line.strip():
            continue
        try:
            row = parse_json_strict(line)
        except X1BError:
            continue
        if not isinstance(row, dict):
            continue
        if row.get("schema_version") in {"scriptops-x1b-decision/v1", DECISION_SCHEMA} and row.get(
            "request_sha256"
        ) == request_sha256:
            raise X1BError("request_sha256 replay already committed")


def _decision_record(admission: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    rid = admission["human_review_numeric_id"]
    digest = admission["request_sha256"]
    record_id = "X1B2-" + _sha256(f"{digest}:{rid}".encode("utf-8"))[:32]
    return {
        "schema_version": DECISION_SCHEMA,
        "id": record_id,
        "status": "committed",
        "kind": "scene_accepted",
        "scene_id": admission["scene_id"],
        "scope": admission["scope"],
        "human_decision": True,
        "human_actor": f"github-user-id:{TRUSTED_HUMAN_GITHUB_USER_ID}",
        "human_github_user_id": TRUSTED_HUMAN_GITHUB_USER_ID,
        "human_login_observed": admission["human_review_user_login_observed"],
        "human_node_id_observed_or_empty": admission[
            "human_review_user_node_id_observed_or_empty"
        ],
        "request_sha256": digest,
        "decision_repository": EVIDENCE_REPOSITORY,
        "decision_pr": admission["decision_pr"],
        "human_review_numeric_id": rid,
        "human_review_commit_id": admission["human_review_commit_id"],
        "human_review_submitted_at": admission["human_review_submitted_at"],
        "human_review_body_sha256": admission["human_review_body_sha256"],
        "review_response_digest": admission["review_response_digest"],
        "human_review_set_digest": admission["human_review_set_digest"],
        "admission_id": admission["admission_id"],
        "admission_digest": admission["admission_digest"],
        "scriptops_base_head": admission["scriptops_base_head"],
        "candidate_path": admission["candidate_path"],
        "candidate_sha256": admission["candidate_sha256"],
        "impact_report_path": admission["impact_report_path"],
        "impact_report_sha256": admission["impact_report_sha256"],
        "accepted_scene_path": admission["accepted_scene_path"],
        "accepted_scene_sha256": admission["accepted_scene_sha256"],
        "material_effect_digest": admission["material_effect_digest"],
        "proposal_rationale": request["proposal_rationale"],
    }


def _prospective_commit(
    git: AnchoredGitV2,
    local: LocalBinding,
    admission: dict[str, Any],
    request: dict[str, Any],
) -> tuple[str, bytes, bytes]:
    base = admission["scriptops_base_head"]
    base_log = git.commit_file(base, ".scriptops/decision-log.ndjson", allow_absent=True)
    _scan_replay(base_log, admission["request_sha256"])
    record = _decision_record(admission, request)
    record_line = canonical_json_bytes(record) + b"\n"
    new_log = base_log + record_line
    new_scene = local.accepted_scene_bytes

    scene_oid = git.text("hash-object", "-w", "--stdin", input_bytes=new_scene)
    log_oid = git.text("hash-object", "-w", "--stdin", input_bytes=new_log)
    if not HEX40.fullmatch(scene_oid) or not HEX40.fullmatch(log_oid):
        raise X1BError("hash-object returned invalid oid")

    fd, name = tempfile.mkstemp(prefix="scriptops-x1b-index-", dir=git.common_dir)
    os.close(fd)
    private_index = Path(name)
    private_index.unlink(missing_ok=True)
    try:
        git.run("read-tree", base, index_file=private_index)
        git.run(
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{scene_oid},{local.accepted_scene_path}",
            index_file=private_index,
        )
        git.run(
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{log_oid},.scriptops/decision-log.ndjson",
            index_file=private_index,
        )
        tree = git.text("write-tree", index_file=private_index)
        if not HEX40.fullmatch(tree):
            raise X1BError("write-tree returned invalid oid")
        env = {
            "GIT_AUTHOR_NAME": MACHINE_NAME,
            "GIT_AUTHOR_EMAIL": MACHINE_EMAIL,
            "GIT_COMMITTER_NAME": MACHINE_NAME,
            "GIT_COMMITTER_EMAIL": MACHINE_EMAIL,
        }
        message = (
            f"scriptops x1b v2: accept {local.scene_id} via "
            f"{admission['request_sha256'][:12]}\n"
        ).encode("utf-8")
        commit = git.text(
            "-c",
            "commit.gpgSign=false",
            "commit-tree",
            tree,
            "-p",
            base,
            "-F",
            "-",
            input_bytes=message,
            env_extra=env,
        )
        if not HEX40.fullmatch(commit):
            raise X1BError("commit-tree returned invalid oid")
        _verify_prospective(git, base, commit, local, new_log)
        return commit, new_log, record_line
    finally:
        private_index.unlink(missing_ok=True)


def _verify_prospective(
    git: AnchoredGitV2,
    base: str,
    commit: str,
    local: LocalBinding,
    new_log: bytes,
) -> None:
    raw = git.run("cat-file", "-p", commit).stdout.decode("utf-8", "replace")
    parents = [line.split(" ", 1)[1] for line in raw.splitlines() if line.startswith("parent ")]
    if parents != [base]:
        raise X1BError("prospective commit parent mismatch")
    author = [line for line in raw.splitlines() if line.startswith("author ")]
    committer = [line for line in raw.splitlines() if line.startswith("committer ")]
    expected = f"{MACHINE_NAME} <{MACHINE_EMAIL}>"
    if len(author) != 1 or not author[0].startswith("author " + expected + " "):
        raise X1BError("prospective author identity mismatch")
    if len(committer) != 1 or not committer[0].startswith("committer " + expected + " "):
        raise X1BError("prospective committer identity mismatch")
    paths = git.text("diff-tree", "--no-commit-id", "--name-only", "-r", base, commit).splitlines()
    expected_paths = sorted([".scriptops/decision-log.ndjson", local.accepted_scene_path])
    if sorted(paths) != expected_paths:
        raise X1BError(f"prospective changed paths mismatch: {paths}")
    scene_mode, scene_oid = git.tree_entry(commit, local.accepted_scene_path)
    log_mode, log_oid = git.tree_entry(commit, ".scriptops/decision-log.ndjson")
    if scene_mode != "100644" or log_mode != "100644":
        raise X1BError("prospective file mode mismatch")
    if git.blob(scene_oid) != local.accepted_scene_bytes:
        raise X1BError("prospective scene bytes mismatch")
    if git.blob(log_oid) != new_log:
        raise X1BError("prospective decision-log bytes mismatch")


def execute_admission(
    git: AnchoredGitV2,
    local: LocalBinding,
    admission: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    base = admission["scriptops_base_head"]
    git.require_direct_main(base)
    git.require_clean()
    commit, new_log, _ = _prospective_commit(git, local, admission, request)
    git.require_direct_main(base)
    if not git.cas_main(commit, base):
        raise X1BError("FAILED_BASE_CHANGED at CAS")

    try:
        git.run("read-tree", commit)
        scene_path = git.root / local.accepted_scene_path
        log_path = git.root / ".scriptops" / "decision-log.ndjson"
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        scene_path.write_bytes(local.accepted_scene_bytes)
        log_path.write_bytes(new_log)
        _postverify(git, base, commit, local, new_log, admission)
    except Exception as exc:
        raise RecoveryRequired(f"RECOVERY_REQUIRED after CAS: {exc}") from exc
    return {
        "status": "COMMITTED",
        "human_decision": True,
        "commit": commit,
        "request_sha256": admission["request_sha256"],
        "admission_id": admission["admission_id"],
    }


def _postverify(
    git: AnchoredGitV2,
    base: str,
    commit: str,
    local: LocalBinding,
    new_log: bytes,
    admission: dict[str, Any],
) -> None:
    if git.require_direct_main(commit) != commit or commit == base:
        raise X1BError("post-CAS direct main mismatch")
    _verify_prospective(git, base, commit, local, new_log)
    index_tree = git.text("write-tree")
    commit_tree = git.text("rev-parse", f"{commit}^{{tree}}")
    if index_tree != commit_tree:
        raise X1BError("real index tree != canonical commit tree")
    if (git.root / local.accepted_scene_path).read_bytes() != local.accepted_scene_bytes:
        raise X1BError("working-tree scene mismatch")
    if (git.root / ".scriptops" / "decision-log.ndjson").read_bytes() != new_log:
        raise X1BError("working-tree decision log mismatch")
    git.require_clean()
    lines = [line for line in new_log.splitlines() if line.strip()]
    if not lines:
        raise X1BError("decision log missing committed record")
    row = parse_json_strict(lines[-1])
    if not isinstance(row, dict):
        raise X1BError("decision record malformed")
    if row.get("human_decision") is not True or row.get("human_github_user_id") != TRUSTED_HUMAN_GITHUB_USER_ID:
        raise X1BError("durable Human attribution mismatch")
    if row.get("request_sha256") != admission["request_sha256"]:
        raise X1BError("durable request binding mismatch")


def approve_scene(scene_id: str, decision_pr: int, root: Path = SOURCE_ROOT) -> dict[str, Any]:
    for key in (
        "GITHUB_TOKEN",
        "GH_TOKEN",
        "GITHUB_ENTERPRISE_TOKEN",
        "GH_ENTERPRISE_TOKEN",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        if os.environ.get(key):
            raise X1BError(f"forbidden parent authority environment: {key}")
    git = AnchoredGitV2.discover(root)
    with x1b_lock(git):
        local = local_preflight(git, scene_id)
        result = run_network_child(decision_pr)
        admission, request = admission_from_child_result(local, decision_pr, result)
        base_log = git.commit_file(local.base_head, ".scriptops/decision-log.ndjson", allow_absent=True)
        _scan_replay(base_log, admission["request_sha256"])
        git.require_direct_main(local.base_head)
        git.require_clean()
        return execute_admission(git, local, admission, request)


def prepare_request_artifacts(
    scene_id: str,
    proposal_rationale: str,
    request_nonce: str | None = None,
    root: Path = SOURCE_ROOT,
) -> tuple[dict[str, Any], bytes, bytes, str]:
    """Prepare inert Human-readable request evidence without canonical effect."""
    git = AnchoredGitV2.discover(root)
    with x1b_lock(git):
        local = local_preflight(git, scene_id)
        nonce = request_nonce or os.urandom(32).hex()
        request, request_bytes, digest = build_request(local, proposal_rationale, nonce)
        return request, request_bytes, local.accepted_scene_bytes, digest


if __name__ == "__main__":
    if sys.argv[1:] == ["--_x1b-github-reader-child"]:
        raise SystemExit(_network_child())
    print("This module is an internal ScriptOps X1B authority component.", file=sys.stderr)
    raise SystemExit(2)