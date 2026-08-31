#!/usr/bin/env python3
"""Bounded X1D-A5 application-side GitHub trust/effect boundary.

No live GitHub client, credential provisioning, governance mutation, or generic
endpoint facility is implemented here. The trusted-state side is read-only and
the effect side exposes exactly one pull-request merge operation.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re
from typing import Any, Protocol, Sequence, runtime_checkable

ADMISSION_VERSION = "x1d-a5-operation-admission/v1"
SUPPORTED_MERGE_METHOD = "merge"
QK_RULESET_ID = 21147233
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class AdmissionDenied(RuntimeError):
    pass


class AuthenticationUnavailable(AdmissionDenied):
    pass


class ExecutionDenied(RuntimeError):
    pass


@runtime_checkable
class GitHubAuthentication(Protocol):
    """Opaque auth context only; no secret/provisioning API."""

    @property
    def credential_reference(self) -> str: ...


@dataclass(frozen=True, slots=True)
class TrustedHumanDecision:
    decision_id: str
    repository: str
    pr: int
    base_head: str
    base_tree: str
    candidate_head: str
    candidate_tree: str
    path_set_digest: str
    canonical_ref: str
    merge_method: str
    expected_post_tree: str
    qk_ruleset_id: int
    qk_ruleset_updated_at: str


@dataclass(frozen=True, slots=True)
class TrustedHumanReview:
    review_id: str
    actor: str
    state: str
    commit_id: str
    body: str
    decision: TrustedHumanDecision | None
    submitted_at: str | None = None


@dataclass(frozen=True, slots=True)
class TrustedStateSnapshot:
    repository: str
    pr: int
    pr_state: str
    pr_merged: bool
    pr_base_ref: str
    pr_base_head: str
    pr_base_tree: str
    candidate_head: str
    candidate_tree: str
    changed_paths: tuple[str, ...]
    canonical_ref: str
    canonical_head: str
    canonical_tree: str
    human_reviews: tuple[TrustedHumanReview, ...]
    qk_ruleset_id: int
    qk_ruleset_name: str
    qk_ruleset_enforcement: str
    qk_ruleset_updated_at: str
    allowed_merge_methods: tuple[str, ...]
    bypass_actors: tuple[str, ...]
    current_process_can_bypass: bool | None
    human_reviews_complete: bool


@runtime_checkable
class AuthenticatedTrustedStateAdapter(Protocol):
    """Read-only trusted-state interface."""

    def read_state(
        self,
        authentication: GitHubAuthentication,
        *,
        repository: str,
        pr: int,
        canonical_ref: str,
    ) -> TrustedStateSnapshot: ...


@dataclass(frozen=True, slots=True)
class AdmissionAssertions:
    human_decision_id: str
    human_review_id: str
    human_actor: str
    human_review_body: str
    repository: str
    pr: int
    base_head: str
    base_tree: str
    candidate_head: str
    candidate_tree: str
    path_set_digest: str
    canonical_ref: str
    merge_method: str
    expected_post_tree: str
    qk_ruleset_id: int
    qk_ruleset_updated_at: str


@dataclass(frozen=True, slots=True)
class OperationAdmission:
    admission_version: str
    admission_id: str
    human_decision_id: str
    human_review_id: str
    human_actor: str
    repository: str
    pr: int
    base_head: str
    base_tree: str
    candidate_head: str
    candidate_tree: str
    path_set_digest: str
    canonical_ref: str
    merge_method: str
    expected_post_tree: str
    qk_ruleset_id: int
    qk_ruleset_updated_at: str
    qk_allowed_merge_methods_digest: str
    canonical_operation_digest: str
    admission_digest: str

    def payload(self) -> dict[str, str | int]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class PullRequestMergeResult:
    merged: bool
    commit_sha: str | None
    message: str


@runtime_checkable
class PullRequestMergeTransport(Protocol):
    """Effect allowlist: exactly one PR merge operation."""

    def merge_pull_request(
        self,
        authentication: GitHubAuthentication,
        *,
        repository: str,
        pr: int,
        merge_method: str,
        expected_head_sha: str,
    ) -> PullRequestMergeResult: ...


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
        raise AdmissionDenied(f"not canonical-JSON serializable: {exc}") from exc
    return text.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_path_set(paths: Sequence[str]) -> str:
    values = list(paths)
    if any(not isinstance(p, str) or not p or p != p.strip() for p in values):
        raise AdmissionDenied("invalid path set")
    if len(values) != len(set(values)):
        raise AdmissionDenied("duplicate path in path set")
    return sha256_hex(canonical_json_bytes(sorted(values)))


def canonical_operation_digest(
    *,
    repository: str,
    pr: int,
    candidate_head: str,
    canonical_ref: str,
    merge_method: str,
    expected_post_tree: str,
) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {
                "repository": repository,
                "pr": pr,
                "candidate_head": candidate_head,
                "canonical_ref": canonical_ref,
                "merge_method": merge_method,
                "expected_post_tree": expected_post_tree,
            }
        )
    )


def qk_allowed_merge_methods_digest(methods: Sequence[str]) -> str:
    if tuple(methods) != (SUPPORTED_MERGE_METHOD,):
        raise AdmissionDenied("Q_K allowed merge methods are not exactly merge-only")
    return sha256_hex(canonical_json_bytes([SUPPORTED_MERGE_METHOD]))


def serialize_admission(admission: OperationAdmission) -> bytes:
    return canonical_json_bytes(admission.payload())


def _text(label: str, value: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise AdmissionDenied(f"{label} must be non-empty exact text")


def _sha1(label: str, value: str) -> None:
    if not isinstance(value, str) or _HEX40.fullmatch(value) is None:
        raise AdmissionDenied(f"{label} must be lowercase 40-hex")


def _sha256(label: str, value: str) -> None:
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        raise AdmissionDenied(f"{label} must be lowercase 64-hex")


def _validate_assertions(a: AdmissionAssertions) -> None:
    for name in (
        "human_decision_id",
        "human_review_id",
        "human_actor",
        "human_review_body",
        "repository",
        "canonical_ref",
        "qk_ruleset_updated_at",
    ):
        _text(name, getattr(a, name))
    if "/" not in a.repository:
        raise AdmissionDenied("repository must be owner/name")
    if not isinstance(a.pr, int) or isinstance(a.pr, bool) or a.pr <= 0:
        raise AdmissionDenied("pr must be positive integer")
    for name in ("base_head", "base_tree", "candidate_head", "candidate_tree", "expected_post_tree"):
        _sha1(name, getattr(a, name))
    _sha256("path_set_digest", a.path_set_digest)
    if a.merge_method != SUPPORTED_MERGE_METHOD:
        raise AdmissionDenied("unsupported merge method")
    if a.expected_post_tree != a.candidate_tree:
        raise AdmissionDenied("expected post tree must equal candidate tree")
    if a.qk_ruleset_id != QK_RULESET_ID:
        raise AdmissionDenied("Q_K ruleset id mismatch")


def _validate_review_record(review: TrustedHumanReview) -> None:
    if not isinstance(review, TrustedHumanReview):
        raise AdmissionDenied("Human review missing or malformed")
    _text("Human review id", review.review_id)
    _text("Human review actor", review.actor)
    _text("Human review state", review.state)
    _sha1("Human review commit id", review.commit_id)
    _text("Human review body", review.body)


def _validate_review_collection(snapshot: TrustedStateSnapshot) -> None:
    if snapshot.human_reviews_complete is not True:
        raise AdmissionDenied("Human review collection incomplete or ambiguous")
    seen: set[str] = set()
    for review in snapshot.human_reviews:
        _validate_review_record(review)
        if review.review_id in seen:
            raise AdmissionDenied("duplicate Human review identity")
        seen.add(review.review_id)


def _review(snapshot: TrustedStateSnapshot, review_id: str) -> TrustedHumanReview:
    matches = [r for r in snapshot.human_reviews if r.review_id == review_id]
    if len(matches) != 1:
        raise AdmissionDenied("Human review missing or ambiguous")
    return matches[0]


def _validate_decision(d: TrustedHumanDecision | None, a: AdmissionAssertions) -> None:
    if not isinstance(d, TrustedHumanDecision):
        raise AdmissionDenied("Human decision missing or malformed")
    pairs = {
        "decision_id": a.human_decision_id,
        "repository": a.repository,
        "pr": a.pr,
        "base_head": a.base_head,
        "base_tree": a.base_tree,
        "candidate_head": a.candidate_head,
        "candidate_tree": a.candidate_tree,
        "path_set_digest": a.path_set_digest,
        "canonical_ref": a.canonical_ref,
        "merge_method": a.merge_method,
        "expected_post_tree": a.expected_post_tree,
        "qk_ruleset_id": a.qk_ruleset_id,
        "qk_ruleset_updated_at": a.qk_ruleset_updated_at,
    }
    for name, expected in pairs.items():
        if getattr(d, name) != expected:
            raise AdmissionDenied(f"Human decision mismatch: {name}")


def _validate_human_currency(s: TrustedStateSnapshot, a: AdmissionAssertions) -> TrustedHumanReview:
    _validate_review_collection(s)
    bound = _review(s, a.human_review_id)
    if bound.actor != a.human_actor:
        raise AdmissionDenied("Human actor mismatch")
    if bound.state != "APPROVED":
        raise AdmissionDenied("Human review not APPROVED")
    if bound.commit_id != a.candidate_head:
        raise AdmissionDenied("Human review commit mismatch")
    if bound.body != a.human_review_body:
        raise AdmissionDenied("Human review body mismatch")
    _validate_decision(bound.decision, a)

    for review in s.human_reviews:
        if review.actor != a.human_actor or review.commit_id != a.candidate_head:
            continue
        if review.state == "DISMISSED":
            continue
        if review.state == "COMMENTED":
            continue
        if review.state == "APPROVED":
            if review.body != a.human_review_body:
                raise AdmissionDenied("conflicting active Human approval body")
            try:
                _validate_decision(review.decision, a)
            except AdmissionDenied as exc:
                raise AdmissionDenied("conflicting active Human approval decision") from exc
            continue
        if review.state == "CHANGES_REQUESTED":
            raise AdmissionDenied("active Human CHANGES_REQUESTED conflicts with bound D0")
        raise AdmissionDenied("unknown or unsupported active Human review state")
    return bound


def _validate_snapshot(s: TrustedStateSnapshot, a: AdmissionAssertions) -> TrustedHumanReview:
    checks = (
        (s.repository == a.repository, "repository mismatch"),
        (s.pr == a.pr, "PR mismatch"),
        (s.pr_state == "open" and not s.pr_merged, "PR not open/unmerged"),
        (s.pr_base_ref == a.canonical_ref == s.canonical_ref, "canonical ref mismatch"),
        (s.pr_base_head == a.base_head == s.canonical_head, "base HEAD drift"),
        (s.pr_base_tree == a.base_tree == s.canonical_tree, "base TREE drift"),
        (s.candidate_head == a.candidate_head, "candidate HEAD drift"),
        (s.candidate_tree == a.candidate_tree, "candidate TREE drift"),
        (digest_path_set(s.changed_paths) == a.path_set_digest, "path-set mismatch"),
        (a.expected_post_tree == s.candidate_tree, "expected-post-tree mismatch"),
        (s.qk_ruleset_id == a.qk_ruleset_id, "Q_K ruleset id mismatch"),
        (s.qk_ruleset_updated_at == a.qk_ruleset_updated_at, "Q_K freshness mismatch"),
        (s.qk_ruleset_enforcement == "active", "Q_K not active"),
        (not s.bypass_actors, "Q_K bypass actors present"),
        (s.current_process_can_bypass is False, "process bypass ambiguous/capable"),
    )
    for ok, message in checks:
        if not ok:
            raise AdmissionDenied(message)
    qk_allowed_merge_methods_digest(s.allowed_merge_methods)
    return _validate_human_currency(s, a)


def _identity_payload(a: AdmissionAssertions) -> dict[str, Any]:
    return {
        "admission_version": ADMISSION_VERSION,
        "human_decision_id": a.human_decision_id,
        "human_review_id": a.human_review_id,
        "human_actor": a.human_actor,
        "human_review_body_sha256": sha256_hex(a.human_review_body.encode("utf-8")),
        "repository": a.repository,
        "pr": a.pr,
        "base_head": a.base_head,
        "base_tree": a.base_tree,
        "candidate_head": a.candidate_head,
        "candidate_tree": a.candidate_tree,
        "path_set_digest": a.path_set_digest,
        "canonical_ref": a.canonical_ref,
        "merge_method": a.merge_method,
        "expected_post_tree": a.expected_post_tree,
        "qk_ruleset_id": a.qk_ruleset_id,
        "qk_ruleset_updated_at": a.qk_ruleset_updated_at,
    }


def _admission_id(a: AdmissionAssertions) -> str:
    return "x1d-a5:" + sha256_hex(canonical_json_bytes(_identity_payload(a)))


def _admission_digest(admission: OperationAdmission) -> str:
    payload = admission.payload()
    del payload["admission_digest"]
    return sha256_hex(canonical_json_bytes(payload))


def _assertions_from_admission(admission: OperationAdmission, review_body: str) -> AdmissionAssertions:
    return AdmissionAssertions(
        human_decision_id=admission.human_decision_id,
        human_review_id=admission.human_review_id,
        human_actor=admission.human_actor,
        human_review_body=review_body,
        repository=admission.repository,
        pr=admission.pr,
        base_head=admission.base_head,
        base_tree=admission.base_tree,
        candidate_head=admission.candidate_head,
        candidate_tree=admission.candidate_tree,
        path_set_digest=admission.path_set_digest,
        canonical_ref=admission.canonical_ref,
        merge_method=admission.merge_method,
        expected_post_tree=admission.expected_post_tree,
        qk_ruleset_id=admission.qk_ruleset_id,
        qk_ruleset_updated_at=admission.qk_ruleset_updated_at,
    )


def validate_admission(admission: OperationAdmission) -> None:
    if not isinstance(admission, OperationAdmission):
        raise ExecutionDenied("missing or malformed OperationAdmission")
    if admission.admission_version != ADMISSION_VERSION:
        raise ExecutionDenied("unknown admission version")
    try:
        _sha256("qk_allowed_merge_methods_digest", admission.qk_allowed_merge_methods_digest)
        _sha256("canonical_operation_digest", admission.canonical_operation_digest)
        _sha256("admission_digest", admission.admission_digest)
        dummy = _assertions_from_admission(admission, "bound-review-body")
        _validate_assertions(dummy)
    except AdmissionDenied as exc:
        raise ExecutionDenied(str(exc)) from exc
    expected_qk = sha256_hex(canonical_json_bytes([SUPPORTED_MERGE_METHOD]))
    if admission.qk_allowed_merge_methods_digest != expected_qk:
        raise ExecutionDenied("allowed-method digest mismatch")
    expected_operation = canonical_operation_digest(
        repository=admission.repository,
        pr=admission.pr,
        candidate_head=admission.candidate_head,
        canonical_ref=admission.canonical_ref,
        merge_method=admission.merge_method,
        expected_post_tree=admission.expected_post_tree,
    )
    if admission.canonical_operation_digest != expected_operation:
        raise ExecutionDenied("canonical-operation digest mismatch")
    if admission.admission_digest != _admission_digest(admission):
        raise ExecutionDenied("admission digest mismatch")


class TrustedStateAdmissionBroker:
    def __init__(self, adapter: AuthenticatedTrustedStateAdapter):
        self._adapter = adapter

    def admit(self, authentication: GitHubAuthentication, a: AdmissionAssertions) -> OperationAdmission:
        _validate_assertions(a)
        try:
            s = self._adapter.read_state(
                authentication,
                repository=a.repository,
                pr=a.pr,
                canonical_ref=a.canonical_ref,
            )
        except AuthenticationUnavailable:
            raise
        except Exception as exc:
            raise AdmissionDenied("trusted-state read unavailable or ambiguous") from exc
        _validate_snapshot(s, a)
        provisional = OperationAdmission(
            admission_version=ADMISSION_VERSION,
            admission_id=_admission_id(a),
            human_decision_id=a.human_decision_id,
            human_review_id=a.human_review_id,
            human_actor=a.human_actor,
            repository=s.repository,
            pr=s.pr,
            base_head=s.canonical_head,
            base_tree=s.canonical_tree,
            candidate_head=s.candidate_head,
            candidate_tree=s.candidate_tree,
            path_set_digest=digest_path_set(s.changed_paths),
            canonical_ref=s.canonical_ref,
            merge_method=SUPPORTED_MERGE_METHOD,
            expected_post_tree=s.candidate_tree,
            qk_ruleset_id=s.qk_ruleset_id,
            qk_ruleset_updated_at=s.qk_ruleset_updated_at,
            qk_allowed_merge_methods_digest=qk_allowed_merge_methods_digest(s.allowed_merge_methods),
            canonical_operation_digest=canonical_operation_digest(
                repository=s.repository,
                pr=s.pr,
                candidate_head=s.candidate_head,
                canonical_ref=s.canonical_ref,
                merge_method=SUPPORTED_MERGE_METHOD,
                expected_post_tree=s.candidate_tree,
            ),
            admission_digest="0" * 64,
        )
        admission = replace(provisional, admission_digest=_admission_digest(provisional))
        validate_admission(admission)
        return admission


class PullRequestMergeExecutor:
    def __init__(self, adapter: AuthenticatedTrustedStateAdapter, transport: PullRequestMergeTransport):
        self._adapter = adapter
        self._transport = transport

    def execute(
        self,
        authentication: GitHubAuthentication,
        admission: OperationAdmission,
        *,
        caller_method: str | None = None,
    ) -> PullRequestMergeResult:
        validate_admission(admission)
        if caller_method is not None and caller_method != admission.merge_method:
            raise ExecutionDenied("caller merge-method substitution rejected")
        if admission.merge_method != SUPPORTED_MERGE_METHOD:
            raise ExecutionDenied("unsupported admission merge method")
        try:
            s = self._adapter.read_state(
                authentication,
                repository=admission.repository,
                pr=admission.pr,
                canonical_ref=admission.canonical_ref,
            )
            _validate_review_collection(s)
            r = _review(s, admission.human_review_id)
            a = _assertions_from_admission(admission, r.body)
            _validate_snapshot(s, a)
            if admission.admission_id != _admission_id(a):
                raise AdmissionDenied("admission id / Human review binding mismatch")
        except AdmissionDenied as exc:
            raise ExecutionDenied(str(exc)) from exc
        except Exception as exc:
            raise ExecutionDenied("trusted-state revalidation unavailable or ambiguous") from exc
        validate_admission(admission)
        return self._transport.merge_pull_request(
            authentication,
            repository=admission.repository,
            pr=admission.pr,
            merge_method=admission.merge_method,
            expected_head_sha=admission.candidate_head,
        )


@dataclass(frozen=True, slots=True)
class BoundedGitHubMergeBoundary:
    broker: TrustedStateAdmissionBroker
    executor: PullRequestMergeExecutor

    @classmethod
    def compose(
        cls,
        *,
        adapter: AuthenticatedTrustedStateAdapter,
        transport: PullRequestMergeTransport,
    ) -> "BoundedGitHubMergeBoundary":
        return cls(
            broker=TrustedStateAdmissionBroker(adapter),
            executor=PullRequestMergeExecutor(adapter, transport),
        )
