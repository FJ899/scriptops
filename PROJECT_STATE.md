# PROJECT STATE — ScriptOps

Date: 2026-09-03

## Current state

```text
X1B Human Decision Authorship V2
IMPLEMENTATION CANDIDATE / NOT CORRECTIVE CLOSURE
```

The Human authorized implementation after the independent AK-CANON PASS of the final composite implementation brief.

Governing planning lineage:

```text
FJ899/8 PR #155  bounded final V2 implementation brief (F001-F004)
FJ899/8 PR #158  minimal F005 TLS-trust repair brief
FJ899/8 PR #159  independent AK-CANON review = PASS
```

ScriptOps implementation baseline before this candidate:

```text
HEAD = 2f22843ac570498b506101addeba5453ab777f08
TREE = 4215d9306392070e64c6fd74a6cfb813ca9d0601
```

Current implementation work is isolated on:

```text
impl/x1b-human-decision-v2-20260903
```

No merge or canonical screenplay effect is authorized by this state file.

## Active Human-decision boundary

`X1B Human Decision Authorship V2` requires a separate trusted GitHub Human review by durable numeric user ID `226907434` bound to exact request content, scene, candidate, impact report, accepted-scene bytes, ScriptOps base and material effect.

Active invocation:

```text
approve --scene <SCN-ID> --decision-pr <PR-NUMBER>
```

**--why is not Human authority**. The old Phase-6 `approve --why` authority interpretation is removed.

The authority/effect chain is:

```text
HumanDecisionRequestV2
-> exact APPROVED review / immutable review.commit_id
-> isolated credential-free GitHubDecisionReaderV2
-> X1BOperationAdmissionV2
-> AnchoredGitV2
-> common-dir X1B lock
-> prospective two-path commit
-> update-ref refs/heads/main NEW OLD compare-and-swap
-> exact post-effect verification
-> HumanDecision=TRUE only after post-effect verification
```

## Active implementation files

```text
phase6/x1b_human_decision.py
phase6/scriptops-v2-hardening.py
legacy/scriptops-v2-single.py
scripts/restore_v2.py
scripts/verify_repository.py
tests/test_x1b_human_decision.py
tests/test_phase6_scriptops_smoke.py
.github/workflows/x1b-human-decision.yml
```

The active legacy file is now a safe compatibility shim. Direct `cmd_approve` and `scene-promote --to accepted` fail before mutation.

The original full single-file prototype is historical only in `sources/prototype/` and cannot be restored over the active shim by `scripts/restore_v2.py`.

## X1B properties implemented by the candidate

```text
F001 durable Human GitHub numeric ID
F002 one current review response + immutable reviewed commit H
F003 prospective commit + pre-canonical main CAS
F004 caller GIT_* repository-selection isolation
F005 caller-independent isolated TLS authority child
```

The canonical logical effect is exactly two tracked paths:

```text
.scriptops/decision-log.ndjson
scenes/<SCN-ID>.fountain
```

If the base decision log is absent, its exact prestate is treated as empty bytes and the authorized effect creates it as `100644`; no third logical path is introduced.

## Historical state

Phase-6, bounded-proposal-view and P3 evidence remain valid historical provenance. Their former `approve --why` mechanism is not active Human authority after X1B.

No historical evidence is silently relabeled as X1B verification or closure.

## Current gate

After the implementation candidate is frozen:

```text
NEXT = independent implementation review
THEN = preregistered corrective-verification packet
THEN = separate Human execution authorization
```

Do not perform before that Human execution authorization:

```text
live X1B decision-evidence PR for the positive control
trusted Human V2 review
canonical screenplay acceptance effect
real corrective positive-control execution
```

## Non-authority

This state does not authorize merge, X1B closure, Agency Kernel V1, release, deployment, tag or maturity claim.

Preserve:

```text
AI PROPOSES != HUMAN DECIDES
REVIEW FINDING != REPAIR AUTHORITY
AK-CANON PASS != IMPLEMENTATION AUTHORITY
IMPLEMENTATION SUCCESS != X1B CLOSURE
```
