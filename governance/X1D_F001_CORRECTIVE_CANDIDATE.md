# X1D-F001 — Bounded Corrective Candidate

Date: 2026-08-30
Status: CANDIDATE ONLY / NOT APPLIED / A5 NOT AUTHORIZED

## Frozen finding

Finding:

```text
X1D-F001 — Q_K CHANGE AUTHORITY NOT ENFORCED
```

Exact invariant to restore:

```text
DECLARED HUMAN RULE AUTHORITY = ENFORCED HUMAN AUTHORIZATION OF RULE CHANGE
```

Frozen observed ScriptOps baseline:

```text
repository: FJ899/scriptops
main HEAD: 68a1bb996e1345e2a8f86813042ff7b40109ae74
main TREE: 2001e2c501fc92197e8b59f18693b3bbf6d7e7cd
ruleset: CANONICAL_MAIN_PROTECTION_V1
ruleset id: 21147233
```

The finding was caused by the AS-IS ruleset requiring a pull request but requiring zero approving reviews and no required reviewer/code-owner/last-push approval.

## Scope

This candidate changes only the enforcement boundary for changes to authoritative rule-bearing material.

It does NOT:

- redesign ScriptOps approval semantics;
- change `cmd_approve`;
- change scene/candidate/canonical-effect behavior;
- execute or resume X1D A5;
- create Agency Kernel v1;
- add a new security protocol;
- claim that an unauthorized AI rule change historically occurred.

## Required principal separation

The correction is only valid if the Human rule authority is represented by a reviewer principal that is not usable by the evaluated AI/process.

Required precondition:

```text
HUMAN_RULE_AUTHORITY_PRINCIPAL != AI_OR_PROCESS_CHANGE_CREDENTIAL
```

A GitHub account approval count by itself is insufficient evidence of Human authorization if the same account credential can be exercised by the evaluated AI/process.

Therefore this candidate MUST NOT be declared effective merely because `required_approving_review_count` changes from `0` to `1`.

## Minimal corrective composition

### C1 — identify the authoritative Human reviewer principal

Define one GitHub reviewer principal `H` satisfying:

```text
H = declared Human authority for Q_K changes
H credentials are outside the evaluated AI/process capability boundary
```

This candidate does not create or choose that identity. It is an external Human-governance precondition.

### C2 — bind rule-bearing paths to H

Add a repository `CODEOWNERS` rule covering the authoritative rule-bearing surface at minimum:

```text
/DECISION_LOG.md
/phase6/scriptops-v2-hardening.py
/legacy/scriptops-v2-single.py
/.github/
/governance/
```

Owner for these paths MUST be `H`.

The exact account/team value is intentionally not invented in this candidate; it must be supplied by the Human authority.

### C3 — change active default-branch ruleset

Update `CANONICAL_MAIN_PROTECTION_V1` so changes to `main` require Human authorization before merge eligibility.

Required minimum state:

```text
pull_request.required_approving_review_count >= 1
pull_request.require_code_owner_review = true
pull_request.require_last_push_approval = true
bypass_actors = []
```

The ruleset remains active for `~DEFAULT_BRANCH` and continues to prohibit deletion and non-fast-forward updates.

### C4 — no self-validation by the evaluated actor

For a rule-bearing change, merge eligibility MUST depend on approval from `H`; merely possessing capability to create/push the PR, modify a rule-bearing file, modify CODEOWNERS, or propose a ruleset change MUST NOT establish authority.

Invariant:

```text
CAPABILITY TO PROPOSE/MODIFY RULE ARTIFACT
!=
AUTHORITY TO AUTHORIZE RULE CHANGE
```

### C5 — governance-surface closure

The mechanism that assigns `H` and protects the rule-bearing paths must itself not be silently changeable by the evaluated actor without the same Human authorization.

At minimum, changes to `.github/CODEOWNERS` and governance files are in the protected CODEOWNERS surface and remain subject to the active ruleset.

A ruleset change is not represented by repository bytes, so closure also requires the repository owner/platform configuration to preserve the same Human-authority boundary for ruleset mutation. If the evaluated AI/process has administrative capability to edit or disable the ruleset using the same authority as H, X1D-F001 is NOT closed.

## Candidate acceptance test

A future independent audit may close X1D-F001 only if all of the following are observed on the exact audited state:

```text
T1 exact candidate repository HEAD/TREE identified
T2 authoritative Human reviewer principal H identified
T3 H is outside evaluated AI/process capability boundary
T4 CODEOWNERS binds rule-bearing paths to H
T5 active main ruleset requires >=1 approving review
T6 active main ruleset requires code-owner review
T7 active main ruleset requires last-push approval
T8 no bypass actor defeats the gate
T9 ruleset/configuration mutation cannot be exercised by evaluated AI/process as rule authority
T10 a rule-bearing PR cannot become merge-eligible without H authorization
```

If any test cannot be established:

```text
X1D-F001 REMAINS OPEN
```

Only after verified closure of X1D-F001 may X1D continue to A5.

## Candidate limitation

This repository commit can prepare and freeze the corrective contract, but it cannot by itself mutate the external GitHub ruleset. Therefore:

```text
CANDIDATE COMMIT != ENFORCEMENT EFFECT
```

The corrective effect exists only when the external ruleset state and Human-principal separation satisfy the acceptance test above.

## Stop discipline

- No A5.
- No V1.
- No broader architecture.
- No merge authorization.
- No release/deploy/tag.
- No claim that X1D-F001 is closed before independent audit of the exact repository HEAD/TREE plus live ruleset state.
