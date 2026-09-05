#!/usr/bin/env python3
"""Deterministic offline ScriptOps repository verification.

This verifier implements the X1B-FRAME two-layer closed-world authority model.
It verifies checkout-local coherence only. It never infers remote main,
deployment, release, or active-product remediation from the checkout.

F006 repair note: the same real runtime-profile validation path accepts both
recognized local transition profiles while the published active-product state
remains CURRENTNESS_UNESTABLISHED. Unknown/mixed profiles fail closed.

F008 repair note: Main_Theme Human-authorship promotion is rejected on the
real fenced document, and R14 verifies the intended rejection reason.

F009 repair note: Layer-B path denial is backed by a self-promotion validator
that rejects self-referential authority claims beyond the legacy exact-string
marker list. Representative free-form claims are exercised non-vacuously.

F010 repair note: ordinary inert technical wording such as effect-method
binding is not itself an authority-promotion verb.

F011 repair note: clear local negation around an authority-promotion phrase is
recognized structurally rather than only through a few exact negation strings.

F012 repair note: negation/currentness context is evaluated for each promotion
inside its local conjunction segment so one negative assertion cannot mask a
distinct positive self-promotion in the same clause.

F013 repair note: comma-separated/asydetic clause boundaries reset local
negation scope before a later authority promotion is evaluated.

F014 repair note: colon and explicit dash-style clause boundaries also reset
local negation scope without treating ordinary internal hyphens as separators.

F015 repair note: a later independent self-reference starts a fresh local
negation subject scope, so unenumerated delimiters cannot let an earlier
negative authority assertion mask a later positive self-promotion.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]

CURRENT_BOOTSTRAP = {
    "README.md",
    "PROJECT_STATE.md",
    "HANDOFF.md",
}

REGISTRY_ENTRIES = [
    ("README.md", "CURRENT_BOOTSTRAP_AUTHORITY"),
    ("PROJECT_STATE.md", "CURRENT_BOOTSTRAP_AUTHORITY"),
    ("HANDOFF.md", "CURRENT_BOOTSTRAP_AUTHORITY"),
    ("DECISION_LOG.md", "DECISION_PROVENANCE_ONLY"),
    ("RECONSTRUCTION_REPORT.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("SOURCES.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("SOURCE_AUDIT_SUMMARY.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("SOURCE_MANIFEST.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY"),
    ("sources/Decision_Summary_Current_State.md", "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY"),
    ("sources/RC1_SCOPE_LOCK.md", "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY"),
    ("sources/ScriptOps_Main_Theme_Summary.md", "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY"),
    ("CODEX_START.md", "PRE_FENCED_NONAUTHORITY_PROVENANCE"),
    ("IDEA_ARCHIVE.md", "PRE_FENCED_NONAUTHORITY_PROVENANCE"),
]

FROZEN_REGISTRY = {path for path, _ in REGISTRY_ENTRIES}

LAYER_B_PREFIXES = (
    "analysis/",
    "continuity/",
    "evidence/",
    "acceptance/",
    "sources/prototype/",
    "legacy/",
    "phase6/",
    "tests/",
    ".github/",
    "scripts/",
)

EXPECTED_FIELDS = {
    "X1B_RESEARCH_CLOSURE": "CLOSED",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION": "CURRENTNESS_UNESTABLISHED",
    "X1B_ACTIVE_PRODUCT_ASSERTION_AUTHORITY": "EXTERNAL_CURRENTNESS_REBIND_REQUIRED",
    "X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE": "NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION",
    "X1B_REVIEWED_REMEDIATION_PROVENANCE": "PR #35 / REVIEWED HEAD 7c40a92165714023743e91c63b5b11b102fadd92 / UNMERGED",
    "X1B_CURRENT_AUTHORITY_BOOTSTRAP": "README.md -> PROJECT_STATE.md -> HANDOFF.md",
    "X1B_AUTHORITY_MODEL": "TWO_LAYER_CLOSED_WORLD_V1",
}

PROVENANCE_MARKERS = {
    "DECISION_LOG.md": [
        "DECISION_PROVENANCE_ONLY",
        "generic Human approval",
        "DEC-SO-010",
        "DEC-SO-011",
    ],
    "SOURCE_MANIFEST.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "SOURCE_MANIFEST CANONICAL LABEL != CURRENT X1B AUTHORITY",
        "PATH-CLASS DENIAL != REGISTRY MEMBERSHIP",
    ],
    "SOURCES.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "SOURCE_MANIFEST canonical label != current X1B authority",
        "Decision_Summary_Current_State filename != current X1B authority",
        "historical ACCESS CHECK gap != current next action",
    ],
    "SOURCE_AUDIT_SUMMARY.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "not current X1B HumanDecision authorship evidence",
    ],
    "RECONSTRUCTION_REPORT.md": [
        "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY",
        "OLD NEXT STEP != CURRENT NEXT ACTION",
        "HISTORICAL HUMAN APPROVAL != X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
    "sources/Decision_Summary_Current_State.md": [
        "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY",
        "filename word `Current` does not grant current authority",
        "GENERIC HUMAN APPROVAL",
        "X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
    "sources/RC1_SCOPE_LOCK.md": [
        "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY",
        "GENERIC HUMAN DECISION IN HISTORICAL RC1",
        "X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
    "sources/ScriptOps_Main_Theme_Summary.md": [
        "HISTORICAL_PRODUCT_GOVERNANCE_PROVENANCE_ONLY",
        "PRODUCT VISION / GENERIC HUMAN APPROVAL",
        "X1B HumanDecision AUTHORSHIP EVIDENCE",
    ],
}

FORBIDDEN_PROVENANCE_MARKERS = {
    "SOURCES.md": (
        "ACCESS CHECK REQUIRED = CURRENT NEXT",
    ),
    "sources/ScriptOps_Main_Theme_Summary.md": (
        "GENERIC HUMAN APPROVAL = X1B HumanDecision AUTHORSHIP EVIDENCE",
    ),
}

# Paths which are outside the frame/status correction surface and are not part
# of the separately reviewed X1B runtime transition profile remain immutable.
IMMUTABLE_PROTECTED_BLOBS = {
    "CODEX_START.md": "5f28888f98a245503fcfc28548133e9ef4b44961",
    "IDEA_ARCHIVE.md": "c7cde73b821e197b9fcf2f51105d466ab308e2f6",
    "phase6/bounded-proposal-view.py": "27f50f0df85fe6b66cfd3c33be00c6d975762b45",
    ".github/pull_request_template.md": "805cd965c6645a0ca8ee4700fb4fe23e1d78a528",
    ".github/workflows/phase6-scriptops-smoke.yml": "a811dc75b4d3c7a1ebd8375c24fc71c74586ddf5",
    ".github/workflows/verify-repository.yml": "7d896d425012479c97bf1e6539f9a861a4a17aa5",
    "tests/test_phase6_bounded_proposal_evidence.py": "dc2e51cad4580010f43ebf59b48c59ea53f81a95",
    "tests/test_phase6_bounded_proposal_view.py": "d5ed0e4e2186145c12ccde1f15886aa3bb93ec19",
    "tests/test_phase6_candidate_selection.py": "28448e2cd0b22cd5bf29df69a7a5c21961208f76",
    "tests/test_phase6_p3_evidence_record.py": "e4ac0b8f2bb6531e90aff0ae49f2a55ce8c1d7b5",
    "tests/test_phase6_p3_evidence_record_002.py": "8d61618e4cde290ade4d4ef329b01d3b46db9c62",
    "tests/test_phase6_p3_evidence_record_003.py": "cb3178ac706d6c6ee888c453284f610b5f81298b",
    "tests/test_phase6_p3_real_workload_001.py": "22b8f1176eb2bed65f763078a059359ba04894c4",
    "tests/test_phase6_p3_real_workload_002.py": "0c06ddd34049cd1608a892df6a86eff13d0c662b",
    "tests/test_phase6_p3_real_workload_003.py": "c0490aa8e9ee96d61d5179c31afafc9fd6499a17",
    "tests/test_phase6_review_task_identity.py": "55d1d6c0a5a5b0630be1f3e3c0d12c9363754a14",
}

# F006 repair: transition-sensitive files have exact, internally consistent
# profiles. The legacy profile is the frozen ScriptOps base. The V2 profile is
# the independently reviewed X1B implementation provenance at PR #35 HEAD
# 7c40a92165714023743e91c63b5b11b102fadd92. The current frame/status docs are
# deliberately not part of either runtime profile.
RUNTIME_PROFILES: dict[str, dict[str, str | None]] = {
    "LEGACY_PRE_X1B": {
        "legacy/scriptops-v2-single.py": "9baa7b3a1eb746e34b79207a382eea1f5dd4ec55",
        "phase6/scriptops-v2-hardening.py": "4f379960ed5677634dd234af6aa39626782b6133",
        "scripts/restore_v2.py": "fa2099d7d4530bce2256051690935625dab0e927",
        "sources/prototype/RESTORE.md": "8a79aca4c93b23c4842792bea9ecaae146e1fc48",
        "tests/test_phase6_scriptops_smoke.py": "d6065047268cee5591883a3065ce49886ec85bcf",
        "phase6/x1b_human_decision.py": None,
        "tests/test_x1b_human_decision.py": None,
        ".github/workflows/x1b-human-decision.yml": None,
    },
    "X1B_V2_CHECKOUT": {
        "legacy/scriptops-v2-single.py": "883669a4a141519483b56d9cde54897fb4c7b17c",
        "phase6/scriptops-v2-hardening.py": "9da50a3e33c982396049c7618f7154b360194350",
        "scripts/restore_v2.py": "20b0b506e537640d0859b687ba0d6ddc78e8ccd0",
        "sources/prototype/RESTORE.md": "fe84dc8d8fb066eaca2d196ecf1e41dc50c22f28",
        "tests/test_phase6_scriptops_smoke.py": "733e929bda33e30dd2de8a53c35eb910a84cbe0d",
        "phase6/x1b_human_decision.py": "1673a15060cc2a5c094acca1ceaf249eaa418c55",
        "tests/test_x1b_human_decision.py": "26ec92b789b38faf5cfc1fb5446ede4ffb2700a6",
        ".github/workflows/x1b-human-decision.yml": "4d71639b9afcb21d6e017a9dedd69459951f40a5",
    },
}

TRANSITION_COMMON_REQUIRED = {
    "legacy/scriptops-v2-single.py",
    "phase6/scriptops-v2-hardening.py",
    "scripts/restore_v2.py",
    "sources/prototype/RESTORE.md",
    "tests/test_phase6_scriptops_smoke.py",
}

POSITIVE_AUTHORITY_MARKERS = (
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CONFIRMED_NOT_REMEDIATED",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CONFIRMED_REMEDIATED",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: YES",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: NO",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: TRUE",
    "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: FALSE",
    "MERGE AUTHORITY = YES",
    "DEPLOYMENT AUTHORITY = YES",
    "RELEASE AUTHORITY = YES",
    "V1 AUTHORITY = YES",
    "CURRENT X1B AUTHORITY = YES",
)

# F009: Layer-B denial must not depend only on exact authority strings. These
# terms define a conservative self-referential promotion grammar. Historical
# statements remain readable; only claims that the text itself grants or is
# authority are rejected.
LAYER_B_SELF_REFERENCE_TERMS = (
    "THIS DOCUMENT",
    "THIS FILE",
    "THIS RECORD",
    "THIS PAGE",
    "THIS MARKDOWN",
    "THIS NOTE",
    "THIS ARTIFACT",
    "THESE WORDS",
    "THESE INSTRUCTIONS",
    "HEREBY",
)

# F015: HEREBY is self-referential/promotion context but not a grammatical
# subject boundary. The remaining phrases can introduce a fresh authority
# subject whose local negation must be evaluated independently.
LAYER_B_SELF_REFERENCE_SUBJECT_TERMS = tuple(
    term for term in LAYER_B_SELF_REFERENCE_TERMS if term != "HEREBY"
)

LAYER_B_PROMOTION_TERMS = (
    "AUTHORITY",
    "AUTHORITATIVE",
    "AUTHORIZE",
    "AUTHORIZES",
    "AUTHORIZED",
    "PERMIT",
    "PERMITS",
    "PERMITTED",
    "ALLOW",
    "ALLOWS",
    "ALLOWED",
    "GRANT",
    "GRANTS",
    "GOVERNS",
    "GOVERN",
    "CONTROLS",
    "CURRENT X1B",
    "CANONICAL X1B",
)

LAYER_B_LOCAL_NONCURRENT_TERMS = (
    "HISTORICAL",
    "PROVENANCE ONLY",
    "UNMERGED",
    "CURRENTNESS UNESTABLISHED",
    "WITHOUT SEPARATE HUMAN",
    "REQUIRES SEPARATE HUMAN",
)

LAYER_B_CONJUNCTION_BOUNDARIES = {
    "AND",
    "OR",
    "BUT",
    "HOWEVER",
    "YET",
}


class VerificationError(RuntimeError):
    pass


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise VerificationError(f"{relative_path} is not UTF-8: {exc}") from exc


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def observed_blob(relative_path: str, root: Path = ROOT) -> str | None:
    path = root / relative_path
    if not path.is_file():
        return None
    return git_blob_sha1(path)


def registry_map_from_entries(entries: Iterable[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for path, klass in entries:
        if path in result:
            raise VerificationError(f"duplicate registry class for {path}")
        result[path] = klass
    return result


def enumerate_registry_surface(root: Path = ROOT) -> list[str]:
    root_md = sorted(
        p.name for p in root.iterdir()
        if p.is_file() and p.suffix == ".md"
    )
    sources = root / "sources"
    direct_sources_md = sorted(
        f"sources/{p.name}" for p in sources.iterdir()
        if p.is_file() and p.suffix == ".md"
    )
    return root_md + direct_sources_md


def classify_nonregistry_markdown_path(relative_path: str) -> str:
    if relative_path in FROZEN_REGISTRY:
        raise VerificationError(f"registry member passed to Layer B: {relative_path}")
    for prefix in LAYER_B_PREFIXES:
        if relative_path.startswith(prefix):
            return "DENIED_BY_PATH_CLASS"
    raise VerificationError(f"UNCLASSIFIED_MARKDOWN_LOCATION: {relative_path}")


def enumerate_layer_b_markdown(root: Path = ROOT) -> list[str]:
    result: list[str] = []
    for path in sorted(root.rglob("*.md")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel not in FROZEN_REGISTRY:
            result.append(rel)
    return result


def validate_registry(actual: Iterable[str], entries: Iterable[tuple[str, str]]) -> dict[str, str]:
    actual_set = set(actual)
    mapping = registry_map_from_entries(entries)
    if actual_set != FROZEN_REGISTRY:
        missing = sorted(FROZEN_REGISTRY - actual_set)
        extra = sorted(actual_set - FROZEN_REGISTRY)
        raise VerificationError(f"Layer-A registry mismatch missing={missing} extra={extra}")
    if len(actual_set) != 13:
        raise VerificationError(f"Layer-A registry cardinality must be 13, got {len(actual_set)}")
    if set(mapping) != actual_set:
        raise VerificationError("registry mapping keys do not equal Layer-A set")
    if len(mapping) != 13:
        raise VerificationError("registry mapping must contain exactly 13 keys")
    current = {p for p, klass in mapping.items() if klass == "CURRENT_BOOTSTRAP_AUTHORITY"}
    if current != CURRENT_BOOTSTRAP:
        raise VerificationError(f"current bootstrap set mismatch: {sorted(current)}")
    return mapping


def parse_x1b_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        for key in EXPECTED_FIELDS:
            prefix = key + ":"
            if stripped.startswith(prefix):
                value = stripped[len(prefix):].strip()
                if key in fields and fields[key] != value:
                    raise VerificationError(f"conflicting {key} values")
                fields[key] = value
    return fields


def validate_current_schema(texts: dict[str, str]) -> None:
    if set(texts) != CURRENT_BOOTSTRAP:
        raise VerificationError("current schema must be checked on exactly the bootstrap trio")
    observed: dict[str, dict[str, str]] = {}
    for path, text in texts.items():
        fields = parse_x1b_fields(text)
        if fields != EXPECTED_FIELDS:
            raise VerificationError(f"{path} X1B schema mismatch: {fields}")
        observed[path] = fields
    first = next(iter(observed.values()))
    if any(fields != first for fields in observed.values()):
        raise VerificationError("current bootstrap trio disagrees")


def validate_provenance_text(path: str, text: str) -> None:
    for marker in PROVENANCE_MARKERS.get(path, []):
        if marker not in text:
            raise VerificationError(f"{path} missing provenance fence marker: {marker}")
    for marker in FORBIDDEN_PROVENANCE_MARKERS.get(path, ()):
        if marker in text:
            if path == "SOURCES.md":
                raise VerificationError(
                    f"{path} publishes forbidden stale current-next authority: {marker}"
                )
            if path == "sources/ScriptOps_Main_Theme_Summary.md":
                raise VerificationError(
                    f"{path} publishes forbidden Human-authorship promotion: {marker}"
                )
            raise VerificationError(f"{path} publishes forbidden provenance authority: {marker}")
    for marker in POSITIVE_AUTHORITY_MARKERS:
        if marker in text:
            raise VerificationError(f"{path} publishes forbidden current authority: {marker}")


def _normalized_authority_line(line: str) -> str:
    normalized = line.upper().replace("`", " ")
    for ch in "\t:;,()[]{}*#>_/\\|.-":
        normalized = normalized.replace(ch, " ")
    return " ".join(normalized.split())


def _term_positions(tokens: list[str], terms: Iterable[str]) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for term in terms:
        parts = term.split()
        width = len(parts)
        for index in range(0, len(tokens) - width + 1):
            if tokens[index:index + width] == parts:
                positions.append((index, width))
    return sorted(set(positions))


def _promotion_positions(tokens: list[str]) -> list[int]:
    return [index for index, _ in _term_positions(tokens, LAYER_B_PROMOTION_TERMS)]


def _latest_independent_self_reference_start(
    tokens: list[str],
    promotion_index: int,
    segment_start: int,
) -> int:
    latest = segment_start
    for subject_index, width in _term_positions(tokens, LAYER_B_SELF_REFERENCE_SUBJECT_TERMS):
        if subject_index < segment_start or subject_index >= promotion_index:
            continue
        between = tokens[subject_index + width:promotion_index]
        # Preserve a negated embedded infinitive such as:
        # "This document does not authorize this file to grant authority."
        # In that shape THIS FILE is an object/complement, not a fresh subject.
        if "TO" in between:
            continue
        latest = max(latest, subject_index)
    return latest


def _promotion_locally_noncurrent(tokens: list[str], index: int) -> bool:
    segment_start = 0
    for prior in range(index - 1, -1, -1):
        if tokens[prior] in LAYER_B_CONJUNCTION_BOUNDARIES:
            segment_start = prior + 1
            break
    segment_start = _latest_independent_self_reference_start(
        tokens,
        index,
        segment_start,
    )
    prefix_tokens = tokens[segment_start:index]
    if any(token in {"NOT", "NO", "CANNOT"} for token in prefix_tokens):
        return True
    prefix_text = " ".join(prefix_tokens)
    return any(term in prefix_text for term in LAYER_B_LOCAL_NONCURRENT_TERMS)


def _all_promotions_locally_noncurrent(line: str) -> bool:
    tokens = line.split()
    positions = _promotion_positions(tokens)
    return bool(positions) and all(
        _promotion_locally_noncurrent(tokens, index)
        for index in positions
    )


def _authority_clauses(raw_line: str) -> list[str]:
    parts = re.split(
        r"[,;:.!?]+|\s+(?:—|–|--)\s+|\b(?:BUT|HOWEVER|YET)\b",
        raw_line.upper(),
    )
    return [
        normalized
        for part in parts
        if (normalized := _normalized_authority_line(part))
    ]


def layer_b_self_promotion_claim(text: str) -> str | None:
    """Return the first self-referential Layer-B authority claim, if any."""
    for raw_line in text.splitlines():
        for line in _authority_clauses(raw_line):
            self_referential = any(term in line for term in LAYER_B_SELF_REFERENCE_TERMS)
            promotion = any(term in line for term in LAYER_B_PROMOTION_TERMS)
            if self_referential and promotion:
                if _all_promotions_locally_noncurrent(line):
                    continue
                return raw_line.strip()
    return None


def validate_layer_b_non_authority_text(path: str, text: str) -> None:
    for marker in POSITIVE_AUTHORITY_MARKERS:
        if marker in text:
            raise VerificationError(f"Layer-B document {path} publishes forbidden authority: {marker}")
    claim = layer_b_self_promotion_claim(text)
    if claim is not None:
        raise VerificationError(
            f"Layer-B document {path} publishes forbidden self-promotion: {claim}"
        )


def classify_runtime_text(text: str) -> str:
    legacy = (
        'approve.add_argument("--why", required=True)' in text
        and '"approver": "human"' in text
        and "x1b.approve_scene(" not in text
        and '"--decision-pr"' not in text
    )
    if legacy:
        return "LEGACY_PRE_X1B"
    v2 = (
        "x1b.approve_scene(" in text
        and 'approve.add_argument("--decision-pr", required=True, type=int)' in text
        and "HumanDecision=TRUE" in text
    )
    if v2:
        return "X1B_V2_CHECKOUT"
    return "UNKNOWN"


def validate_runtime_currentness(runtime_class: str, assertion: str) -> None:
    if assertion != "CURRENTNESS_UNESTABLISHED":
        raise VerificationError("local runtime class may not promote active-product state")
    if runtime_class not in {"LEGACY_PRE_X1B", "X1B_V2_CHECKOUT"}:
        raise VerificationError(f"unknown local runtime class: {runtime_class}")


def observe_runtime_profile(root: Path = ROOT) -> dict[str, str | None]:
    all_paths: set[str] = set()
    for profile in RUNTIME_PROFILES.values():
        all_paths.update(profile)
    return {path: observed_blob(path, root) for path in sorted(all_paths)}


def validate_runtime_profile(
    runtime_class: str,
    observed: dict[str, str | None],
    assertion: str,
) -> None:
    """Validate the real transition profile used by repository verification.

    Both recognized rows are admissible only with CURRENTNESS_UNESTABLISHED.
    Exact profile matching prevents a legacy/V2 Frankenstein checkout from
    borrowing the semantic label of either reviewed runtime.
    """
    validate_runtime_currentness(runtime_class, assertion)
    expected = RUNTIME_PROFILES[runtime_class]
    if set(observed) != set(expected):
        missing = sorted(set(expected) - set(observed))
        extra = sorted(set(observed) - set(expected))
        raise VerificationError(
            f"runtime profile key mismatch for {runtime_class}: missing={missing} extra={extra}"
        )
    mismatches = [
        f"{path}: expected={expected[path]} actual={observed[path]}"
        for path in sorted(expected)
        if observed[path] != expected[path]
    ]
    if mismatches:
        raise VerificationError(
            f"runtime profile mismatch for {runtime_class}: " + "; ".join(mismatches)
        )


def check_required_paths() -> None:
    required = (
        FROZEN_REGISTRY
        | set(IMMUTABLE_PROTECTED_BLOBS)
        | TRANSITION_COMMON_REQUIRED
        | {"scripts/verify_repository.py"}
    )
    missing = sorted(path for path in required if not (ROOT / path).is_file())
    if missing:
        raise VerificationError(f"missing required paths: {missing}")
    print(f"[PASS] required bounded/protected paths present: {len(required)}")


def check_immutable_blobs() -> None:
    mismatches: list[str] = []
    for relative_path, expected in IMMUTABLE_PROTECTED_BLOBS.items():
        actual = git_blob_sha1(ROOT / relative_path)
        if actual != expected:
            mismatches.append(f"{relative_path}: expected={expected} actual={actual}")
    if mismatches:
        raise VerificationError("immutable protected baseline drift: " + "; ".join(mismatches))
    print(f"[PASS] immutable protected sentinels unchanged: {len(IMMUTABLE_PROTECTED_BLOBS)} blobs")


def check_layer_a() -> None:
    actual = enumerate_registry_surface()
    validate_registry(actual, REGISTRY_ENTRIES)
    if "sources/prototype/RESTORE.md" in actual:
        raise VerificationError("RESTORE.md must not enter Layer-A registry")
    print("[PASS] Layer A exact: 13 root/direct-sources Markdown registry members")


def check_layer_b() -> None:
    paths = enumerate_layer_b_markdown()
    for path in paths:
        result = classify_nonregistry_markdown_path(path)
        if result != "DENIED_BY_PATH_CLASS":
            raise VerificationError(f"unexpected Layer-B classification: {path} -> {result}")
    if "sources/prototype/RESTORE.md" not in paths:
        raise VerificationError("RESTORE.md must be present in Layer B")
    print(f"[PASS] Layer B path-class denial: {len(paths)} Markdown files; registry count unchanged")


def check_current_bootstrap() -> None:
    texts = {path: read_text(path) for path in CURRENT_BOOTSTRAP}
    validate_current_schema(texts)
    readme = texts["README.md"]
    state = texts["PROJECT_STATE.md"]
    handoff = texts["HANDOFF.md"]
    required_separations = [
        "CURRENTNESS_UNESTABLISHED != FALSE",
        "CURRENTNESS_UNESTABLISHED != TRUE",
        "PR HEAD != ACTIVE DEFAULT BRANCH",
        "GREEN VERIFICATION != DEPLOYED ENFORCEMENT",
        "GENERIC HUMAN APPROVAL != X1B HumanDecision AUTHORSHIP EVIDENCE",
    ]
    for marker in required_separations:
        if marker not in readme:
            raise VerificationError(f"README missing boundary: {marker}")
    if "No current `approve --why` / canonical-write instruction is authorized by this file." not in state:
        raise VerificationError("PROJECT_STATE does not fence legacy effect route")
    if "PR #35 must not be merged as-is" not in handoff:
        raise VerificationError("HANDOFF does not fence stale PR #35")
    print("[PASS] current bootstrap trio agrees on CURRENTNESS_UNESTABLISHED and TWO_LAYER_CLOSED_WORLD_V1")


def check_provenance_surfaces() -> None:
    for path in PROVENANCE_MARKERS:
        validate_provenance_text(path, read_text(path))
    for path in enumerate_layer_b_markdown():
        validate_layer_b_non_authority_text(path, read_text(path))
    print("[PASS] registry provenance fences and Layer-B non-current authority are explicit")


def check_runtime_separation() -> None:
    hardening = read_text("phase6/scriptops-v2-hardening.py")
    runtime_class = classify_runtime_text(hardening)
    profile = observe_runtime_profile()
    validate_runtime_profile(
        runtime_class,
        profile,
        EXPECTED_FIELDS["X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION"],
    )
    print(
        f"[PASS] checkout runtime profile = {runtime_class}; "
        "active-product state remains CURRENTNESS_UNESTABLISHED"
    )


def check_historical_decision_preservation() -> None:
    decision_log = read_text("DECISION_LOG.md")
    for marker in [
        "DEC-SO-001",
        "DEC-SO-010",
        "DEC-SO-011",
        "BASE: legacy/scriptops-v2-single.py",
        "REWRITE: NO",
        "NEW CAPABILITY: NO",
        "MATURITY CLAIM: NONE",
        "CANONICAL EFFECT EXECUTION:",
        "NOT AUTHORIZED WITHOUT SEPARATE HUMAN GATE",
    ]:
        if marker not in decision_log:
            raise VerificationError(f"historical decision marker missing: {marker}")
    scope = read_text("sources/RC1_SCOPE_LOCK.md")
    for marker in [
        "browser helper",
        "direct API calls",
        "autonomous writing",
        "multi-user",
        "AI Guard",
        "Retcon Engine",
        "cloud sync",
    ]:
        if marker not in scope:
            raise VerificationError(f"historical RC1 exclusion missing: {marker}")
    print("[PASS] historical decisions/scope preserved behind non-current authority fences")


def expect_failure(label: str, func: Callable[[], object]) -> None:
    try:
        func()
    except VerificationError:
        return
    raise VerificationError(f"synthetic rejection did not fail: {label}")


def expect_failure_message(
    label: str,
    expected_message: str,
    func: Callable[[], object],
) -> None:
    try:
        func()
    except VerificationError as exc:
        if expected_message not in str(exc):
            raise VerificationError(
                f"synthetic rejection failed for wrong reason: {label}: {exc}"
            ) from exc
        return
    raise VerificationError(f"synthetic rejection did not fail: {label}")


def check_synthetic_rejections_and_transition_positives() -> None:
    base = list(FROZEN_REGISTRY)

    # R1-R2: new Layer-A members.
    expect_failure("R1 new root Markdown", lambda: validate_registry(base + ["CURRENT_STATUS.md"], REGISTRY_ENTRIES))
    expect_failure("R2 new direct sources Markdown", lambda: validate_registry(base + ["sources/CurrentFoo.md"], REGISTRY_ENTRIES))

    # R3-R5: registry mapping integrity/current authority count.
    duplicate = list(REGISTRY_ENTRIES) + [("README.md", "HISTORICAL_RECONSTRUCTION_PROVENANCE_ONLY")]
    expect_failure("R3 duplicate registry class", lambda: validate_registry(base, duplicate))
    expect_failure("R4 omitted registry class", lambda: validate_registry(base, REGISTRY_ENTRIES[:-1]))
    four_current = [
        (p, "CURRENT_BOOTSTRAP_AUTHORITY" if p in CURRENT_BOOTSTRAP | {"DECISION_LOG.md"} else c)
        for p, c in REGISTRY_ENTRIES
    ]
    expect_failure("R5 four current bootstrap members", lambda: validate_registry(base, four_current))

    # R6-R8: nested RESTORE cannot enter Layer A or cardinality 14.
    expect_failure("R6 recursive RESTORE inclusion", lambda: validate_registry(base + ["sources/prototype/RESTORE.md"], REGISTRY_ENTRIES))
    expect_failure("R7 special-case RESTORE append", lambda: validate_registry(base + ["sources/prototype/RESTORE.md"], REGISTRY_ENTRIES))
    expect_failure("R8 Layer-A cardinality 14", lambda: validate_registry(base + ["extra.md"], REGISTRY_ENTRIES))

    # R9-R10: Layer-B known prefix allowed; unknown location fails closed.
    if classify_nonregistry_markdown_path("sources/prototype/extra.md") != "DENIED_BY_PATH_CLASS":
        raise VerificationError("R9 known nested provenance path not denied")
    expect_failure("R10 unknown docs prefix", lambda: classify_nonregistry_markdown_path("docs/Current.md"))

    # R11-R16: provenance fences cannot disappear or promote authority.
    expect_failure("R11 SOURCES fence removed", lambda: validate_provenance_text("SOURCES.md", "historical text only"))
    sources_with_stale_current_next = (
        read_text("SOURCES.md") + "\nACCESS CHECK REQUIRED = CURRENT NEXT\n"
    )
    expect_failure_message(
        "R12 ACCESS CHECK restored as current next",
        "publishes forbidden stale current-next authority",
        lambda: validate_provenance_text("SOURCES.md", sources_with_stale_current_next),
    )
    expect_failure(
        "R13 decision provenance mapped active",
        lambda: validate_provenance_text(
            "DECISION_LOG.md",
            read_text("DECISION_LOG.md")
            + "\nX1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CONFIRMED_REMEDIATED\n",
        ),
    )
    main_theme_with_authorship_promotion = (
        read_text("sources/ScriptOps_Main_Theme_Summary.md")
        + "\nGENERIC HUMAN APPROVAL = X1B HumanDecision AUTHORSHIP EVIDENCE\n"
    )
    expect_failure_message(
        "R14 Main Theme generic approval promoted",
        "publishes forbidden Human-authorship promotion",
        lambda: validate_provenance_text(
            "sources/ScriptOps_Main_Theme_Summary.md",
            main_theme_with_authorship_promotion,
        ),
    )
    expect_failure(
        "R15 RC1 scope promoted",
        lambda: validate_provenance_text(
            "sources/RC1_SCOPE_LOCK.md",
            read_text("sources/RC1_SCOPE_LOCK.md") + "\nCURRENT X1B AUTHORITY = YES\n",
        ),
    )
    expect_failure("R16 source audit fence removed", lambda: validate_provenance_text("SOURCE_AUDIT_SUMMARY.md", "audit"))

    # R17-R20: current trio disagreement / ontic promotion.
    good = {p: read_text(p) for p in CURRENT_BOOTSTRAP}
    disagree = dict(good)
    disagree["HANDOFF.md"] = disagree["HANDOFF.md"].replace(
        "X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE: NONE_ACCEPTED_FOR_THIS_STATUS_PUBLICATION",
        "X1B_ACTIVE_PRODUCT_ASSERTION_EVIDENCE: SOMETHING_ELSE",
        1,
    )
    expect_failure("R17 trio disagreement", lambda: validate_current_schema(disagree))

    for label, value in [
        ("R18 confirmed not remediated", "CONFIRMED_NOT_REMEDIATED"),
        ("R19 confirmed remediated", "CONFIRMED_REMEDIATED"),
        ("R20 boolean collapse", "YES"),
    ]:
        bad = dict(good)
        bad["README.md"] = bad["README.md"].replace(
            "X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: CURRENTNESS_UNESTABLISHED",
            f"X1B_ACTIVE_PRODUCT_REMEDIATION_ASSERTION: {value}",
            1,
        )
        expect_failure(label, lambda bad=bad: validate_current_schema(bad))

    # P7/P8 and R21-R23: exercise the same full profile validator used by main().
    legacy_text = 'approve.add_argument("--why", required=True)\n"approver": "human"\n'
    v2_text = (
        'x1b.approve_scene(scene, decision_pr)\n'
        'approve.add_argument("--decision-pr", required=True, type=int)\n'
        'HumanDecision=TRUE\n'
    )
    if classify_runtime_text(legacy_text) != "LEGACY_PRE_X1B":
        raise VerificationError("synthetic legacy classifier failed")
    if classify_runtime_text(v2_text) != "X1B_V2_CHECKOUT":
        raise VerificationError("synthetic V2 classifier failed")

    validate_runtime_profile(
        "LEGACY_PRE_X1B",
        dict(RUNTIME_PROFILES["LEGACY_PRE_X1B"]),
        "CURRENTNESS_UNESTABLISHED",
    )
    validate_runtime_profile(
        "X1B_V2_CHECKOUT",
        dict(RUNTIME_PROFILES["X1B_V2_CHECKOUT"]),
        "CURRENTNESS_UNESTABLISHED",
    )

    expect_failure(
        "R21 V2 promotes active state",
        lambda: validate_runtime_profile(
            "X1B_V2_CHECKOUT",
            dict(RUNTIME_PROFILES["X1B_V2_CHECKOUT"]),
            "CONFIRMED_REMEDIATED",
        ),
    )
    expect_failure(
        "R22 legacy promotes negative active state",
        lambda: validate_runtime_profile(
            "LEGACY_PRE_X1B",
            dict(RUNTIME_PROFILES["LEGACY_PRE_X1B"]),
            "CONFIRMED_NOT_REMEDIATED",
        ),
    )
    expect_failure(
        "R23 unknown runtime class",
        lambda: validate_runtime_currentness("UNKNOWN", "CURRENTNESS_UNESTABLISHED"),
    )

    # R24 supporting document cannot publish consequential authority.
    expect_failure(
        "R24 supporting merge authority",
        lambda: validate_provenance_text(
            "DECISION_LOG.md",
            read_text("DECISION_LOG.md") + "\nMERGE AUTHORITY = YES\n",
        ),
    )

    # F006-specific mixed-profile regression: a recognized V2 label cannot pass
    # with legacy transition blobs (or vice versa).
    expect_failure(
        "F006 mixed V2/legacy runtime profile",
        lambda: validate_runtime_profile(
            "X1B_V2_CHECKOUT",
            dict(RUNTIME_PROFILES["LEGACY_PRE_X1B"]),
            "CURRENTNESS_UNESTABLISHED",
        ),
    )

    # F009: free-form Layer-B self-promotion must fail through the same
    # validator used by production check_provenance_surfaces().
    layer_b_baseline = "Historical supporting provenance. No current authority is granted here."
    for label, claim in [
        ("F009 current authority self-promotion", "THIS DOCUMENT IS THE CURRENT X1B AUTHORITY"),
        ("F009 merge authorization self-promotion", "MERGE IS AUTHORIZED BY THIS DOCUMENT"),
        ("F009 free-form grant self-promotion", "THIS FILE GRANTS CANONICAL X1B AUTHORITY"),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda claim=claim: validate_layer_b_non_authority_text(
                "sources/prototype/extra.md",
                layer_b_baseline + "\n" + claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "sources/prototype/extra.md",
        "HISTORICAL: MERGE IS NOT AUTHORIZED BY THIS DOCUMENT.\n",
    )

    # F010: inert technical binding language must not be promoted into an
    # authority verb merely because a sentence is self-referential.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file is the inert canonical payload for the X1D-A5 effect-method-binding live acceptance sequence.\n",
    )

    # F011: negation may include local modifiers between NOT and the authority
    # verb; those modifiers must not turn an explicit denial into promotion.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This artifact does not itself authorize a merge, Human D0, OperationAdmission, corrective closure, release, deployment, or tag.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not by itself grant release authority.\n",
    )

    # F012: one negative promotion may not mask a distinct positive promotion
    # in the same conjunction clause. Boundary-local context resets at AND/OR.
    for label, mixed_claim in [
        (
            "F012 second self-reference promotion",
            "This document does not authorize merge and this file grants canonical X1B authority.",
        ),
        (
            "F012 same-subject second promotion",
            "This document does not authorize merge and grants release authority.",
        ),
        (
            "F012 historical first conjunct cannot mask positive second",
            "Historical: this document authorized merge and this file grants canonical X1B authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda mixed_claim=mixed_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                mixed_claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize merge and does not grant release authority.\n",
    )

    # F013: punctuation-only/asydetic clause boundaries must also reset local
    # negation scope; the repair is generic comma segmentation, not a literal
    # match for the finding sentence.
    for label, comma_claim in [
        (
            "F013 comma asydetic hereby promotion",
            "This document does not grant release authority, it hereby authorizes merge.",
        ),
        (
            "F013 comma second self-reference promotion",
            "This record is not authoritative, these words grant merge authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda comma_claim=comma_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                comma_claim + "\n",
            ),
        )

    # F014: colon and explicit dash-style clause boundaries must reset local
    # negation scope without treating ordinary internal hyphens as separators.
    for label, boundary_claim in [
        (
            "F014 em-dash second self-reference promotion",
            "This document does not authorize merge — this file grants canonical X1B authority.",
        ),
        (
            "F014 colon second self-reference promotion",
            "This record is not authoritative: these words authorize deployment.",
        ),
        (
            "F014 spaced double-hyphen second promotion",
            "This document does not authorize merge -- this file grants release authority.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda boundary_claim=boundary_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                boundary_claim + "\n",
            ),
        )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize: merge, release, deployment, or tag.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This file is historical — this file does not grant merge authority.\n",
    )

    # F015: a later independent self-reference must reset negation subject
    # scope even when the delimiter is not enumerated by _authority_clauses().
    for label, subject_claim in [
        (
            "F015 parenthetical second self-reference promotion",
            "This document does not authorize merge (this file grants canonical X1B authority).",
        ),
        (
            "F015 bracket-delimited second self-reference promotion",
            "This document does not authorize merge [this file grants release authority].",
        ),
        (
            "F015 slash-delimited second self-reference promotion",
            "This record is not authoritative / these words authorize deployment.",
        ),
    ]:
        expect_failure_message(
            label,
            "publishes forbidden self-promotion",
            lambda subject_claim=subject_claim: validate_layer_b_non_authority_text(
                "acceptance/inert.md",
                subject_claim + "\n",
            ),
        )

    # A self-reference used as the object of a negated infinitive is not a
    # fresh authority subject and must remain an accepted negative statement.
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize this file to grant release authority.\n",
    )
    validate_layer_b_non_authority_text(
        "acceptance/inert.md",
        "This document does not authorize merge (this file does not grant release authority).\n",
    )

    print("[PASS] synthetic rejection matrix R1-R24")
    print("[PASS] F009 Layer-B free-form self-promotion regression")
    print("[PASS] F010 inert technical binding regression")
    print("[PASS] F011 local negation regression")
    print("[PASS] F012 mixed-clause masking regression")
    print("[PASS] F013 comma/asydetic masking regression")
    print("[PASS] F014 non-comma clause-boundary masking regression")
    print("[PASS] F015 independent-self-reference negation-scope regression")
    print("[PASS] runtime transition positives P7/P8 use the real profile validator")


def main() -> int:
    try:
        check_required_paths()
        check_immutable_blobs()
        check_layer_a()
        check_layer_b()
        check_current_bootstrap()
        check_provenance_surfaces()
        check_runtime_separation()
        check_historical_decision_preservation()
        check_synthetic_rejections_and_transition_positives()
    except (OSError, VerificationError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    print("[PASS] X1B two-layer closed-world frame/status correction is checkout-locally coherent")
    print("[PASS] ACTIVE PRODUCT REMEDIATION ASSERTION = CURRENTNESS_UNESTABLISHED")
    print("[PASS] recognized LEGACY and reviewed X1B_V2 runtime profiles do not promote active-product state")
    print("[PASS] offline verification != remote-main/deployment proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())