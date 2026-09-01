# X1D-A5 Effect-Method Binding Corrective Candidate

## Status

`DESIGN-ONLY CORRECTIVE CANDIDATE`

`IMPLEMENTATION = NOT AUTHORIZED`

`A5 FAIL ACCEPTED != CORRECTIVE ACTION CLOSED`

This artifact defines the minimum enforceable correction for the Human-accepted X1D-A5 RETRY-02 finding. It does not implement, apply, activate, test, merge, or close the correction.

## 1. Bound accepted finding

This design is bound to the accepted durable records:

```text
FJ899/8 PR #91 = TERMINAL TECHNICAL FAIL
HEAD = 82ab66b00f97d3a24f02b632e4e40c6fb7a73c78
TREE = 6526249d6a5e5b530bdfed1df2471faf4e83d6ce
PATH = research/X1D_A5_RETRY02_RESULT_FAIL_T4_UNAUTHORIZED_SQUASH_AVAILABLE.md
BLOB = 772503e7c1faecb462a3dbbafbb58b70d9c6d5b4

FJ899/8 PR #92 = HUMAN ACCEPTANCE
HEAD = d68226c57c39254c1a5a796ef69bd5428dbf1229
TREE = 1bc5c0bc3016da599605a4350d7421a151a2c66c
PATH = acceptance/X1D_A5_RETRY02_HUMAN_ACCEPT.md
BLOB = d174e7445ac6f9f13c062fc934920d007590e1b5
```

Accepted finding:

`EFFECT METHOD NOT BOUND TO THE EXACT HUMAN DECISION`

Observed counterexample:

```text
D0 AUTHORIZES MERGE ONLY
SQUASH EFFECT REMAINS AVAILABLE UNDER THE SAME D0
```

Preserve:

`DECLARED EXACT EFFECT BINDING != ENFORCED EXACT EFFECT BINDING`

`AVAILABLE UNAUTHORIZED EFFECT != EXECUTED UNAUTHORIZED EFFECT`

## 2. Current-state premise observed before this design

The design-preparation preflight observed:

```text
FJ899/scriptops main = 30095c3170d16263e2db553a2b199bd6e33feace
FJ899/scriptops PR #30 = OPEN / READY / UNMERGED
PR #30 HEAD = ca54f436cb99207d7d2b125013f7b7806b2e57ec
CODEOWNERS /governance/ = @litrgratis-pixel
ruleset_id = 21147233
ruleset_name = CANONICAL_MAIN_PROTECTION_V1
ruleset_enforcement = active
ruleset allowed_merge_methods = { merge, squash, rebase }
bypass_actors = []
current_user_can_bypass = never
```

No runtime code, ruleset, CODEOWNERS, PR #30, or canonical main mutation is performed by this artifact.

## 3. Corrective objective

For the governed canonical-effect path covered by this correction:

> If a valid Human decision authorizes `merge_method = merge`, then neither `squash` nor `rebase` may remain executable under that same decision.

The correction must establish both:

1. exact decision-to-operation admission binding; and
2. platform capability closure that prevents alternate GitHub merge methods from remaining available through UI or API paths.

Neither layer substitutes for the other.

`AUTHORIZATION TEXT != ENFORCEMENT`

`OPERATION REQUEST != OPERATION ADMISSION`

## 4. Minimum corrective architecture

The minimum correction is a merge-only canonical-effect profile for this governed path.

### 4.1 Platform enforcement envelope

Future corrected `Q_K@v_next` must change only the relevant merge-method policy so that the protected canonical branch permits exactly:

```text
allowed_merge_methods = { merge }
```

The existing Human-approval, code-owner, last-push, review-thread, no-bypass, deletion, and non-fast-forward predicates remain independently required unless a separately authorized governance change says otherwise.

For this correction, repository-wide disabling of squash/rebase is optional hardening and is deliberately not required. The minimum normative change is the protected-branch ruleset restriction above, because it directly closes the observed canonical branch path without broadening scope to unrelated branches.

A future implementation must not dynamically rewrite `allowed_merge_methods` per D0. Dynamic policy mutation would turn each effect decision into a governance-rule mutation and would introduce a separate normative-authority problem.

Therefore:

`D0 METHOD SELECTION != AUTHORITY TO MUTATE Q_K`

This corrective profile supports `merge` only. A future desire to authorize `squash` or `rebase` is outside this corrective profile and requires separately authorized governance design/change plus fresh validation.

### 4.2 OperationAdmission object

A proof-bearing `OperationAdmission` must bind the exact canonical operation before any process-controlled effect call.

Minimum fields:

```text
admission_version
admission_id
human_decision_id
human_review_id
human_actor
repository
pr
base_head
base_tree
candidate_head
candidate_tree
path_set_digest
canonical_ref
merge_method
expected_post_tree
qk_ruleset_id
qk_ruleset_updated_at
qk_allowed_merge_methods_digest
canonical_operation_digest
```

For this corrective profile:

```text
merge_method = merge
qk_allowed_merge_methods = { merge }
```

The canonical operation digest must commit to at least:

```text
repository
pr
candidate_head
canonical_ref
merge_method
expected_post_tree
```

Recommended conceptual form:

```text
canonical_operation_digest = H(
  repository,
  pr,
  candidate_head,
  canonical_ref,
  merge_method,
  expected_post_tree
)
```

The exact serialization/hash function is an implementation detail that must be frozen before implementation testing.

### 4.3 Admission broker

A component separate from the executor creates `OperationAdmission` only from trusted observed state.

It must independently verify:

```text
valid Human D0 event
actor exact
review state = APPROVED
review commit_id = exact candidate_head
review body/decision tuple = exact
current PR candidate = exact candidate_head/tree
current main = exact base_head/tree
canonical_ref = exact
D0.merge_method = merge
current Q_K@v_next allowed_merge_methods = { merge }
no bypass
expected_post_tree = exact candidate tree for the positive control
```

Any unknown, mismatch, stale decision, changed candidate, changed main, changed Q_K, ambiguous method, or unsupported method:

`DENY / BLOCKED BEFORE EFFECT`

The executor may not generate or submit its own authorization proof.

### 4.4 Executor

The executor consumes a valid `OperationAdmission` and must not accept an independently caller-selected merge method.

The GitHub merge request is constructed from the admission object.

For this profile:

```text
transport.merge_method = OperationAdmission.merge_method = merge
expected_head_sha = OperationAdmission.candidate_head
```

If a caller supplies, requests, overrides, injects, or substitutes a method different from the admission method:

`DENY BEFORE GITHUB MERGE CALL`

The executor must reject rather than normalize or reinterpret the request.

`METHOD SELECTION != AUTHORITY TO CHANGE METHOD`

### 4.5 Direct GitHub UI/API capability closure

The broker/executor control is not sufficient by itself because the accepted counterexample existed in the GitHub Web UI outside that process path.

Therefore live `Q_K@v_next` must make alternate methods unavailable on the protected canonical branch.

Required observable effect of the platform policy:

```text
Create a merge commit = potentially available when all other predicates are satisfied
Squash and merge = absent, disabled, or otherwise not executable
Rebase and merge = absent, disabled, or otherwise not executable
```

A direct GitHub API attempt specifying `squash` or `rebase` must not be able to create the canonical effect on the governed branch under this profile.

No claim of closure may rely only on the presence of text in D0 or only on an application-side executor check.

`APPLICATION GUARD != PLATFORM CAPABILITY CLOSURE`

## 5. C1-C10 requirements

### C1 — Exact authorized method in admission

`OperationAdmission.merge_method` is mandatory and exact. For this profile it equals `merge`.

PASS condition:

`admission.merge_method = D0.merge_method = merge`

Missing or unknown method:

`DENY`

### C2 — Executor cannot substitute method

The executor derives the GitHub method only from the validated admission object.

It cannot accept a free-form method override.

PASS condition:

requests for `squash`, `rebase`, or any method unequal to `admission.merge_method` are rejected before transport invocation.

### C3 — Alternate GitHub UI/API paths cannot satisfy same authorization

`Q_K@v_next` must restrict protected-branch allowed merge methods to exactly `{ merge }`.

PASS condition:

under otherwise valid C0/D0/Q_K state, GitHub does not expose an executable `Squash and merge` or `Rebase and merge` canonical action.

If either remains executable:

`CORRECTIVE VERIFICATION FAIL`

### C4 — Exact referent/effect binding

Admission binds at least:

```text
repository
pr
candidate_head
canonical_ref
merge_method
expected_post_tree
```

Changed repository, PR, candidate, canonical ref, method, or expected effect invalidates the admission.

### C5 — Changed method requires a new Human decision

A method different from D0 invalidates the current admission.

Within this merge-only corrective profile, a new D0 naming `squash` or `rebase` is still insufficient because `Q_K@v_next` does not admit those methods.

Supporting another method requires separate governance authorization and fresh validation.

### C6 — AI/process cannot broaden Human decision

No AI/process credential may rewrite `merge` to another method, treat another method as equivalent, mutate Q_K to make another method available, or issue an admission that broadens the D0 tuple.

`CAPABILITY TO FORM REQUEST != AUTHORITY TO BROADEN DECISION`

### C7 — Positive control for authorized method

A future fresh inert candidate with valid exact D0 and valid admission must be eligible for the exact authorized `merge` method when all other Q_K predicates are satisfied.

Positive control must use only `merge`.

### C8 — Negative controls for squash and rebase

Future verification must independently establish both:

```text
squash unavailable under same exact valid merge D0
rebase unavailable under same exact valid merge D0
```

At minimum use method-specific live GitHub UI evidence coupled to exact ruleset/API state reads.

Application-layer negative tests must also establish that an executor request attempting `squash` or `rebase` with a merge-only admission is denied before transport invocation.

Do not execute an unauthorized canonical effect merely to prove that GitHub would reject it. If platform API-path closure cannot be established without risking the unauthorized effect, classify the relevant verification predicate as `BLOCKED` rather than improvising a destructive negative test.

### C9 — Exact post-effect verification

After the authorized positive control, command success is insufficient.

For a GitHub merge-commit effect require independent truth:

```text
PR = merged
main HEAD = generated merge commit
main HEAD tree = expected_post_tree
parent1 = exact pre-effect main HEAD
parent2 = exact candidate HEAD
exact expected path/blob/content
no extra canonical change
```

The two-parent structure is part of confirming that the observed canonical effect was the authorized `merge` method rather than squash/rebase.

`COMMAND SUCCESS != EFFECT TRUTH`

### C10 — Fail closed on method ambiguity

Unknown merge method, unknown ruleset state, unresolved GitHub method-specific availability, stale D0, stale admission, candidate drift, main drift, policy drift, method mismatch, or post-effect uncertainty must not be interpreted as PASS.

Before effect:

`UNKNOWN / AMBIGUOUS -> DENY / BLOCKED`

After effect:

`UNKNOWN POST-EFFECT TRUTH -> INDETERMINATE`

## 6. Separation of authority and capability

The correction preserves:

```text
Human D0 = decision evidence
OperationAdmission = machine-checkable admission derived from trusted state
Executor credential = effect capability
Q_K = platform enforcement envelope
```

These are not interchangeable.

`HUMAN DECISION != EXECUTOR CREDENTIAL`

`EXECUTOR CREDENTIAL != AUTHORITY TO CHANGE D0`

`EXECUTOR CREDENTIAL != AUTHORITY TO CHANGE Q_K`

The process that can invoke GitHub merge is not thereby authorized to choose the merge method.

## 7. Future implementation boundary

A future implementation phase, under separate Human authorization, may need to introduce:

1. `OperationAdmission` representation and exact serialization;
2. admission broker validation;
3. executor enforcement that derives method from admission;
4. a Human-authorized ruleset change from `{ merge, squash, rebase }` to `{ merge }` for the protected canonical branch;
5. evidence capture for method-specific live GitHub state;
6. exact positive-control post-effect verification.

This design does not authorize any of those changes.

The ruleset mutation itself is governance-bearing and must use the already established Human rule-authority boundary. It cannot be applied merely because this design proposes it.

`CANDIDATE DESIGN != ENFORCEMENT EFFECT`

## 8. Concrete future acceptance tests

The following tests are specified now but must not be executed under this design-preparation authority.

### AT0 — Exact candidate and governance preregistration

Freeze exact implementation candidate HEAD/TREE, exact next Q_K identity, exact test target, exact Human decision body, and exact OperationAdmission serialization before execution.

Candidate or contract drift:

`BLOCKED`

### AT1 — Q_K method envelope

Read live protected-branch ruleset.

Require:

```text
allowed_merge_methods = { merge }
bypass_actors = []
current evaluated process cannot bypass
```

Any `squash` or `rebase` in the live allowed set:

`FAIL`

### AT2 — Admission exact-method positive construction

Using a fresh valid merge-only Human D0 and exact candidate state, broker creates one admission.

Require:

```text
D0.merge_method = merge
admission.merge_method = merge
operation digest = exact frozen digest
```

### AT3 — Executor substitution negative: squash

Present a request that attempts `squash` while the admission says `merge`.

Require rejection before any GitHub merge transport call.

Any transport invocation with `squash`:

`FAIL`

### AT4 — Executor substitution negative: rebase

Same as AT3 for `rebase`.

Any transport invocation with `rebase`:

`FAIL`

### AT5 — Live GitHub UI negative: squash

Under exact fresh candidate, valid merge D0, exact current Q_K, and no unrelated blocker, inspect the method-specific GitHub merge control non-destructively.

Require `Squash and merge` to be absent, disabled, or non-executable.

Enabled executable squash:

`FAIL — EFFECT METHOD NOT BOUND`

### AT6 — Live GitHub UI negative: rebase

Same as AT5 for `Rebase and merge`.

Enabled executable rebase:

`FAIL — EFFECT METHOD NOT BOUND`

### AT7 — Direct API-path closure evidence

Read exact live Q_K and GitHub method capability state sufficient to establish that protected-branch alternate methods are rejected by platform policy.

Do not perform an unauthorized canonical merge as a negative probe.

If direct API-path closure cannot be established non-destructively with trusted evidence:

`BLOCKED`

Do not downgrade uncertainty to PASS.

### AT8 — Changed-decision method negative

Attempt admission construction with the same exact candidate but a D0 tuple naming `squash` or `rebase` while Q_K remains merge-only.

Require:

`NO ADMISSION`

This establishes that a new decision cannot silently override the governance envelope.

### AT9 — Authorized merge positive control

Only after AT0-AT8 pass, use a fresh valid merge-only D0 and admission to execute exactly one authorized GitHub `merge` positive control under separate execution authorization.

Before effect require exact candidate/main/Q_K/D0/admission.

After effect require exact C9 post-effect truth.

### AT10 — Post-effect method truth

Require generated canonical commit to have:

```text
parent1 = exact pre-main
parent2 = exact candidate
TREE = exact expected_post_tree
```

If the effect shape is squash/rebase-like, has wrong parents/tree, or cannot be established:

`FAIL` if wrong effect is established;

`INDETERMINATE` if effect occurred but exact truth cannot be established.

## 9. Corrective closure rule

This finding is not closed by:

```text
design creation
design review
implementation green tests
ruleset text alone
broker unit tests alone
UI appearance alone
positive merge success alone
```

Closure requires a fresh bounded verification showing the complete composition:

```text
valid Human merge-only decision
+
exact OperationAdmission binding
+
executor no-substitution enforcement
+
platform alternate-method closure
+
positive authorized merge
+
exact post-effect truth
```

Only Human may accept closure after independent verification.

`DESIGN PASS != FINDING CLOSED`

`IMPLEMENTATION SUCCESS != HUMAN ACCEPT`

## 10. Explicit non-goals

This design does not:

- implement runtime code;
- alter `CANONICAL_MAIN_PROTECTION_V1`;
- alter CODEOWNERS;
- mutate, close, reset, approve, or merge PR #30;
- execute T5 from RETRY-02;
- create a new D0;
- authorize squash or rebase;
- define a general multi-method authorization framework;
- begin V1;
- release, deploy, or tag anything.

A general future system that supports multiple Human-authorized merge methods would require a separate design proving how the platform enforcement envelope changes without allowing the effect actor to acquire governance authority. That problem is intentionally outside this minimum corrective candidate.

## 11. Preserved invariants

`AVAILABLE UNAUTHORIZED EFFECT != EXECUTED UNAUTHORIZED EFFECT`

`AUTHORIZATION TEXT != ENFORCEMENT`

`OPERATION REQUEST != OPERATION ADMISSION`

`METHOD SELECTION != AUTHORITY TO CHANGE METHOD`

`A5 FAIL ACCEPTED != CORRECTIVE ACTION CLOSED`

`CORRECTIVE DESIGN != IMPLEMENTATION`

`DESIGN PASS != FINDING CLOSED`

`AI PROPOSES != HUMAN DECIDES`
