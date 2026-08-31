from __future__ import annotations

from dataclasses import replace
import json
import unittest

from phase6.x1d_a5_github_boundary import (
    ADMISSION_VERSION,
    QK_RULESET_ID,
    AdmissionAssertions,
    AdmissionDenied,
    AuthenticationUnavailable,
    BoundedGitHubMergeBoundary,
    ExecutionDenied,
    PullRequestMergeResult,
    TrustedHumanDecision,
    TrustedHumanReview,
    TrustedStateSnapshot,
    canonical_json_bytes,
    canonical_operation_digest,
    digest_path_set,
    qk_allowed_merge_methods_digest,
    serialize_admission,
    validate_admission,
)

REPO = "FJ899/scriptops"
PR = 30
REF = "refs/heads/main"
BASE_HEAD = "1" * 40
BASE_TREE = "2" * 40
CANDIDATE_HEAD = "3" * 40
CANDIDATE_TREE = "4" * 40
QK_UPDATED = "2026-08-31T12:00:00Z"
PATHS = ("governance/example-a.md", "governance/example-b.md")
PATH_DIGEST = digest_path_set(PATHS)
D0 = "D0-X1D-A5-001"
REVIEW_ID = "review-9001"
ACTOR = "human-owner"
BODY = "exact bounded Human decision body"


class FakeAuthentication:
    def __init__(self, reference: str) -> None:
        self._reference = reference

    @property
    def credential_reference(self) -> str:
        return self._reference


class FakeReadOnlyAdapter:
    def __init__(self, snapshot: TrustedStateSnapshot, authentication: FakeAuthentication) -> None:
        self.snapshot = snapshot
        self.authentication = authentication
        self.read_invocations: list[tuple[str, int, str]] = []

    def read_state(self, authentication: FakeAuthentication, *, repository: str, pr: int, canonical_ref: str) -> TrustedStateSnapshot:
        if authentication is not self.authentication:
            raise AuthenticationUnavailable("authentication context unavailable or ambiguous")
        self.read_invocations.append((repository, pr, canonical_ref))
        return self.snapshot


class RecordingMergeTransport:
    def __init__(self, authentication: FakeAuthentication) -> None:
        self.authentication = authentication
        self.invocations: list[dict[str, object]] = []

    def merge_pull_request(self, authentication: FakeAuthentication, *, repository: str, pr: int, merge_method: str, expected_head_sha: str) -> PullRequestMergeResult:
        if authentication is not self.authentication:
            raise AuthenticationUnavailable("effect authentication unavailable")
        self.invocations.append(
            {
                "repository": repository,
                "pr": pr,
                "merge_method": merge_method,
                "expected_head_sha": expected_head_sha,
            }
        )
        return PullRequestMergeResult(True, "5" * 40, "deterministic fake merge")


def decision(**changes: object) -> TrustedHumanDecision:
    value = TrustedHumanDecision(
        D0,
        REPO,
        PR,
        BASE_HEAD,
        BASE_TREE,
        CANDIDATE_HEAD,
        CANDIDATE_TREE,
        PATH_DIGEST,
        REF,
        "merge",
        CANDIDATE_TREE,
        QK_RULESET_ID,
        QK_UPDATED,
    )
    return replace(value, **changes)


def review(**changes: object) -> TrustedHumanReview:
    value = TrustedHumanReview(REVIEW_ID, ACTOR, "APPROVED", CANDIDATE_HEAD, BODY, decision())
    return replace(value, **changes)


def snapshot(**changes: object) -> TrustedStateSnapshot:
    value = TrustedStateSnapshot(
        REPO,
        PR,
        "open",
        False,
        REF,
        BASE_HEAD,
        BASE_TREE,
        CANDIDATE_HEAD,
        CANDIDATE_TREE,
        PATHS,
        REF,
        BASE_HEAD,
        BASE_TREE,
        (review(),),
        QK_RULESET_ID,
        "CANONICAL_MAIN_PROTECTION_V1",
        "active",
        QK_UPDATED,
        ("merge",),
        (),
        False,
        True,
    )
    return replace(value, **changes)


def assertions(**changes: object) -> AdmissionAssertions:
    value = AdmissionAssertions(
        D0,
        REVIEW_ID,
        ACTOR,
        BODY,
        REPO,
        PR,
        BASE_HEAD,
        BASE_TREE,
        CANDIDATE_HEAD,
        CANDIDATE_TREE,
        PATH_DIGEST,
        REF,
        "merge",
        CANDIDATE_TREE,
        QK_RULESET_ID,
        QK_UPDATED,
    )
    return replace(value, **changes)


class X1DA5BoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.auth = FakeAuthentication("opaque-test-auth")
        self.adapter = FakeReadOnlyAdapter(snapshot(), self.auth)
        self.transport = RecordingMergeTransport(self.auth)
        self.boundary = BoundedGitHubMergeBoundary.compose(adapter=self.adapter, transport=self.transport)

    def admit(self, value: AdmissionAssertions | None = None):
        return self.boundary.broker.admit(self.auth, value or assertions())

    def broker_denied(self, value: AdmissionAssertions | None = None) -> None:
        before = len(self.transport.invocations)
        with self.assertRaises(AdmissionDenied):
            self.admit(value)
        self.assertEqual(len(self.transport.invocations), before)

    def executor_denied(self, admission, caller_method: str | None = None) -> None:
        before = len(self.transport.invocations)
        with self.assertRaises(ExecutionDenied):
            self.boundary.executor.execute(self.auth, admission, caller_method=caller_method)
        self.assertEqual(len(self.transport.invocations), before)

    def test_positive_exact_admission_and_executor_derivation(self) -> None:
        admission = self.admit()
        self.assertEqual(admission.admission_version, ADMISSION_VERSION)
        self.assertEqual(admission.merge_method, "merge")
        self.assertEqual(admission.expected_post_tree, CANDIDATE_TREE)
        validate_admission(admission)
        self.assertEqual(self.transport.invocations, [])
        result = self.boundary.executor.execute(self.auth, admission)
        self.assertTrue(result.merged)
        self.assertEqual(
            self.transport.invocations,
            [{"repository": REPO, "pr": PR, "merge_method": "merge", "expected_head_sha": CANDIDATE_HEAD}],
        )

    def test_canonical_json_and_serialization_are_exact(self) -> None:
        self.assertEqual(canonical_json_bytes({"z": "zażółć", "a": 1}), '{"a":1,"z":"zażółć"}'.encode())
        self.assertFalse(canonical_json_bytes({"a": 1}).endswith(b"\n"))
        one = self.admit()
        two = self.admit()
        self.assertEqual(serialize_admission(one), serialize_admission(two))
        self.assertEqual(set(json.loads(serialize_admission(one))), set(one.payload()))

    def test_operation_digest_is_field_sensitive(self) -> None:
        base = dict(repository=REPO, pr=PR, candidate_head=CANDIDATE_HEAD, canonical_ref=REF, merge_method="merge", expected_post_tree=CANDIDATE_TREE)
        original = canonical_operation_digest(**base)
        deltas = [
            {"repository": "FJ899/other"}, {"pr": PR + 1}, {"candidate_head": "6" * 40},
            {"canonical_ref": "refs/heads/other"}, {"merge_method": "squash"}, {"expected_post_tree": "7" * 40},
        ]
        for delta in deltas:
            changed = dict(base)
            changed.update(delta)
            self.assertNotEqual(original, canonical_operation_digest(**changed))

    def test_allowed_method_digest_is_exact_merge_only(self) -> None:
        self.assertEqual(qk_allowed_merge_methods_digest(("merge",)), "39c596909e5372a870034c2f8679b9c8492290764ec6c330d694b71f61bf65df")
        for methods in (("merge", "squash"), ("merge", "rebase"), ("squash",), ()):
            with self.assertRaises(AdmissionDenied):
                qk_allowed_merge_methods_digest(methods)

    def test_path_set_digest_is_order_stable_and_sensitive(self) -> None:
        self.assertEqual(digest_path_set(PATHS), digest_path_set(tuple(reversed(PATHS))))
        self.assertNotEqual(digest_path_set(PATHS), digest_path_set((PATHS[0], "other")))
        with self.assertRaises(AdmissionDenied):
            digest_path_set((PATHS[0], PATHS[0]))

    def test_squash_and_rebase_substitution_are_zero_transport(self) -> None:
        admission = self.admit()
        for method in ("squash", "rebase", "MERGE"):
            self.executor_denied(admission, method)
        self.assertEqual(self.transport.invocations, [])

    def test_changed_d0_method_does_not_admit(self) -> None:
        for method in ("squash", "rebase"):
            self.adapter.snapshot = snapshot(human_reviews=(review(decision=decision(merge_method=method)),))
            self.broker_denied()
        self.broker_denied(assertions(merge_method="squash"))

    def test_referent_and_effect_mismatches_fail_closed(self) -> None:
        cases = [
            {"repository": "FJ899/other"}, {"pr": PR + 1}, {"candidate_head": "6" * 40},
            {"candidate_tree": "6" * 40}, {"canonical_head": "6" * 40}, {"canonical_tree": "6" * 40},
            {"pr_base_head": "6" * 40}, {"pr_base_tree": "6" * 40}, {"canonical_ref": "refs/heads/other"},
            {"changed_paths": (PATHS[0], "other")},
        ]
        for delta in cases:
            self.adapter.snapshot = snapshot(**delta)
            self.broker_denied()
        self.broker_denied(assertions(expected_post_tree="7" * 40))

    def test_human_review_and_decision_mismatches_fail_closed(self) -> None:
        reviews = [
            review(state="CHANGES_REQUESTED"), review(commit_id="6" * 40), review(actor="other-human"), review(body="changed body"),
            review(decision=decision(decision_id="D0-other")), review(decision=decision(repository="FJ899/other")),
            review(decision=decision(candidate_head="6" * 40)), review(decision=decision(candidate_tree="6" * 40)),
            review(decision=decision(path_set_digest="a" * 64)), review(decision=decision(qk_ruleset_updated_at="2026-08-31T12:00:01Z")),
        ]
        for value in reviews:
            self.adapter.snapshot = snapshot(human_reviews=(value,))
            self.broker_denied()
        for values in ((), (review(), review())):
            self.adapter.snapshot = snapshot(human_reviews=values)
            self.broker_denied()

    def test_multiple_identical_approvals_are_concordant_and_order_independent(self) -> None:
        reviews = (
            review(submitted_at="2026-08-31T08:20:09Z"),
            review(review_id="review-9002", submitted_at="2026-08-31T08:34:26Z"),
            review(review_id="review-9003", submitted_at="2026-08-31T08:54:20Z"),
        )
        self.adapter.snapshot = snapshot(human_reviews=reviews)
        first = self.admit()
        reordered = (
            replace(reviews[2], submitted_at="2030-01-01T00:00:00Z"),
            replace(reviews[0], submitted_at="2040-01-01T00:00:00Z"),
            replace(reviews[1], submitted_at="2050-01-01T00:00:00Z"),
        )
        self.adapter.snapshot = snapshot(human_reviews=reordered)
        second = self.admit()
        self.assertEqual(serialize_admission(first), serialize_admission(second))
        self.assertEqual(self.transport.invocations, [])

    def test_conflicting_same_human_same_candidate_decisions_deny(self) -> None:
        conflicts = (
            review(review_id="conflict-body", body="different decision body"),
            review(review_id="conflict-d0", decision=decision(decision_id="D0-other")),
            review(review_id="conflict-negative", state="CHANGES_REQUESTED", decision=None),
            review(review_id="conflict-unknown", state="PENDING", decision=None),
        )
        for conflict in conflicts:
            self.adapter.snapshot = snapshot(human_reviews=(review(), conflict))
            self.broker_denied()

    def test_dismissed_comment_different_actor_and_different_commit_are_not_silent_winners(self) -> None:
        cases = (
            review(review_id="dismissed-old", state="DISMISSED", body="old body", decision=None),
            review(review_id="commented", state="COMMENTED", body="comment only", decision=None),
            review(review_id="other-actor", actor="other-human", state="CHANGES_REQUESTED", decision=None),
            review(review_id="other-commit", commit_id="6" * 40, state="CHANGES_REQUESTED", decision=None),
        )
        for extra in cases:
            self.adapter.snapshot = snapshot(human_reviews=(review(), extra))
            admission = self.admit()
            validate_admission(admission)
            self.assertEqual(self.transport.invocations, [])

    def test_dismissed_old_conflict_allows_separately_bound_concordant_approval(self) -> None:
        new_review_id = "review-new"
        old = review(state="DISMISSED", body="old conflicting body", decision=None)
        new = review(review_id=new_review_id, submitted_at="2026-08-31T09:00:00Z")
        self.adapter.snapshot = snapshot(human_reviews=(old, new))
        admission = self.admit(assertions(human_review_id=new_review_id))
        self.assertEqual(admission.human_review_id, new_review_id)
        self.assertEqual(self.transport.invocations, [])

    def test_bound_dismissal_unknown_completeness_and_duplicate_identity_fail_closed(self) -> None:
        self.adapter.snapshot = snapshot(human_reviews=(review(state="DISMISSED", decision=None),))
        self.broker_denied()
        for complete in (False, None):
            self.adapter.snapshot = snapshot(human_reviews_complete=complete)
            self.broker_denied()
        self.adapter.snapshot = snapshot(human_reviews=(review(), review()))
        self.broker_denied()

    def test_executor_revalidates_complete_decision_set_before_transport(self) -> None:
        admission = self.admit()
        conflict = review(review_id="late-conflict", state="CHANGES_REQUESTED", decision=None)
        self.adapter.snapshot = snapshot(human_reviews=(review(), conflict))
        self.executor_denied(admission)
        self.adapter.snapshot = snapshot(human_reviews_complete=False)
        self.executor_denied(admission)
        self.assertEqual(self.transport.invocations, [])

    def test_qk_and_bypass_mismatches_fail_closed(self) -> None:
        cases = [
            {"qk_ruleset_id": QK_RULESET_ID + 1}, {"qk_ruleset_updated_at": "2026-08-31T12:00:01Z"},
            {"qk_ruleset_enforcement": "evaluate"}, {"allowed_merge_methods": ("merge", "squash")},
            {"allowed_merge_methods": ("merge", "rebase")}, {"bypass_actors": ("RepositoryRole:5",)},
            {"current_process_can_bypass": True}, {"current_process_can_bypass": None},
        ]
        for delta in cases:
            self.adapter.snapshot = snapshot(**delta)
            self.broker_denied()

    def test_closed_or_merged_pr_fails_closed(self) -> None:
        for delta in ({"pr_state": "closed"}, {"pr_merged": True}):
            self.adapter.snapshot = snapshot(**delta)
            self.broker_denied()

    def test_equal_value_forged_auth_context_is_not_trusted(self) -> None:
        forged = FakeAuthentication(self.auth.credential_reference)
        with self.assertRaises(AuthenticationUnavailable):
            self.boundary.broker.admit(forged, assertions())
        self.assertEqual(self.transport.invocations, [])

    def test_unknown_remote_read_fails_closed(self) -> None:
        class BrokenAdapter:
            def read_state(self, authentication, **kwargs):
                raise RuntimeError("unknown remote state")

        boundary = BoundedGitHubMergeBoundary.compose(adapter=BrokenAdapter(), transport=self.transport)
        with self.assertRaises(AdmissionDenied):
            boundary.broker.admit(self.auth, assertions())
        self.assertEqual(self.transport.invocations, [])

    def test_digest_tamper_is_zero_transport(self) -> None:
        admission = self.admit()
        for field in ("qk_allowed_merge_methods_digest", "canonical_operation_digest", "admission_digest"):
            self.executor_denied(replace(admission, **{field: "a" * 64}))
        self.assertEqual(self.transport.invocations, [])

    def test_admission_digest_covers_every_required_field_except_itself(self) -> None:
        admission = self.admit()
        for field, value in admission.payload().items():
            if field == "admission_digest":
                continue
            tampered = value + 1 if isinstance(value, int) else value + "x"
            self.executor_denied(replace(admission, **{field: tampered}))

    def test_stale_state_after_admission_is_zero_transport(self) -> None:
        cases = [
            {"candidate_head": "6" * 40}, {"candidate_tree": "6" * 40}, {"canonical_head": "6" * 40},
            {"human_reviews": (review(state="DISMISSED"),)}, {"human_reviews": (review(body="changed body"),)},
            {"allowed_merge_methods": ("merge", "squash")}, {"current_process_can_bypass": None},
        ]
        for delta in cases:
            admission = self.admit()
            self.adapter.snapshot = snapshot(**delta)
            self.executor_denied(admission)
            self.transport.invocations.clear()
            self.adapter.snapshot = snapshot()

    def test_effect_auth_context_is_not_human_authority(self) -> None:
        admission = self.admit()
        forged = FakeAuthentication(self.auth.credential_reference)
        before = len(self.transport.invocations)
        with self.assertRaises(ExecutionDenied):
            self.boundary.executor.execute(forged, admission)
        self.assertEqual(len(self.transport.invocations), before)

    def test_read_adapter_has_no_write_surface_and_transport_is_merge_only(self) -> None:
        for name in ("write", "merge_pull_request", "update_ruleset", "update_codeowners", "move_ref", "create_review"):
            self.assertFalse(hasattr(self.adapter, name), name)
        public_callables = {name for name in dir(self.transport) if not name.startswith("_") and callable(getattr(self.transport, name))}
        self.assertEqual(public_callables, {"merge_pull_request"})
        for name in ("request", "call", "update_ruleset", "move_ref", "create_release", "create_tag"):
            self.assertFalse(hasattr(self.transport, name), name)

    def test_negative_matrix_proves_zero_effect_invocations(self) -> None:
        admission = self.admit()
        negatives = [(admission, "squash"), (admission, "rebase"), (replace(admission, admission_digest="a" * 64), None)]
        for value, method in negatives:
            self.transport.invocations.clear()
            self.executor_denied(value, method)
            self.assertEqual(self.transport.invocations, [])


if __name__ == "__main__":
    unittest.main()
