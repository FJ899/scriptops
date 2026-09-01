# X1D-F001 — Q_K CHANGE AUTHORITY NOT ENFORCED

Date: 2026-08-30
Status: DURABLE FINDING / NO REPAIR DESIGN / NO IMPLEMENTATION

## Frozen observed target

Repository: `FJ899/scriptops`

Observed branch: `main`

Observed HEAD:

```text
68a1bb996e1345e2a8f86813042ff7b40109ae74
```

Observed TREE:

```text
2001e2c501fc92197e8b59f18693b3bbf6d7e7cd
```

Observed active GitHub ruleset:

```text
CANONICAL_MAIN_PROTECTION_V1
ruleset id: 21147233
enforcement: active
```

Observed rules relevant to change control:

```text
pull request required
required_approving_review_count: 0
required_reviewers: []
require_code_owner_review: false
require_last_push_approval: false
bypass_actors: []
current_user_can_bypass: never
```

## Context

This finding was produced by X1D — ScriptOps Constitutive-Rule Reality Check.

The X1D claim under test was:

```text
ScriptOps may assert
HumanDecisionAttributionJustified_K(C,S,I)=TRUE
only if an authoritative, applicable and then-current Q_K governs approval,
changes to Q_K are authority-controlled,
and the approval is bound to the exact later canonical effect.
```

The test used a first-credible-counterexample STOP rule.

## Declared normative authority observed in ScriptOps

`DECISION_LOG.md` contains the following relevant active decisions:

- `DEC-SO-001` — Human remains owner of canon; AI creates candidates/analyses and does not independently approve or modify canon.
- `DEC-SO-010` — `Owner: USER`; Phase-6 requires explicit Human `why` before canonical write and states that ScriptOps does not receive its own authority.

The Phase-6 approval path in `phase6/scriptops-v2-hardening.py` also requires non-empty `approve --why` before canonical scene write and records `approver: "human"`.

These observations are sufficient to identify a declared Human/User normative authority for the approval rule family under test.

## Finding

The repository-level technical change-control boundary does not require an independent Human authorization event before a change to rule-bearing artifacts or approval logic becomes merge-eligible.

The active default-branch ruleset requires use of a pull request but requires zero approving reviews and no specific Human reviewer, code-owner approval, or last-push approval.

Therefore the following distinction is established for the observed state:

```text
DECLARED HUMAN RULE AUTHORITY
!=
ENFORCED HUMAN AUTHORIZATION OF RULE CHANGE
```

Equivalent Project-8 principle:

```text
CAPABILITY TO MODIFY RULE REPRESENTATION
!=
AUTHORITY TO MODIFY NORMATIVE RULE
```

## Exact counterexample class

A change can be proposed to a rule-bearing artifact or approval implementation through the repository's ordinary PR path.

Under the observed ruleset, merge eligibility does not itself require a separate approving Human review event.

Accordingly, the technical repository boundary does not prove that every accepted modification of Q_K was authorized by the Human authority declared by ScriptOps.

This is sufficient to falsify the X1D A4 Change-Control requirement AS-IS.

## What this finding does NOT establish

This finding does **not** establish that:

- AI actually changed Q_K;
- AI actually merged a rule change;
- any unauthorized rule change has occurred historically;
- repository write capability is currently available to any particular AI process;
- a particular repair mechanism is required.

The finding concerns the absence of an enforced authority boundary in the observed configuration, not proof of an actual abuse of that boundary.

## X1D consequence

```text
X1D FAIL — Q_K CHANGE AUTHORITY NOT ENFORCED
```

Per preregistered STOP discipline:

- A5 end-to-end binding was NOT executed;
- no repair was designed;
- no ScriptOps implementation was changed;
- no X1D implementation was created;
- no V1 work was authorized.

## Evidence anchors

Observed ScriptOps state:

```text
main@68a1bb996e1345e2a8f86813042ff7b40109ae74
TREE 2001e2c501fc92197e8b59f18693b3bbf6d7e7cd
```

Rule-authority declarations:

```text
DECISION_LOG.md
DEC-SO-001
DEC-SO-010
```

Approval implementation:

```text
phase6/scriptops-v2-hardening.py
cmd_approve
```

Repository enforcement evidence:

```text
CANONICAL_MAIN_PROTECTION_V1
ruleset id 21147233
```

## Stop boundary

This artifact records only the observed failure.

It intentionally contains no recommendation for changing branch protection, review counts, CODEOWNERS, protected paths, signatures, credentials, approval protocols, trusted channels, or any other corrective mechanism.

Any corrective candidate requires a separate Human decision after this finding is accepted as evidence.
