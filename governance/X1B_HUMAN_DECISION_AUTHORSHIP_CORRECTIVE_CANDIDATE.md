# X1B Human Decision Authorship Corrective Candidate

Status: `DESIGN-ONLY CORRECTIVE CANDIDATE / NOT IMPLEMENTATION AUTHORITY`

Date: 2026-09-01

## 1. Purpose

This document defines a bounded corrective design for the accepted X1B finding:

`X1B FAIL — FALSE HUMAN DECISION`

It addresses the real ScriptOps approval boundary in which possession of the `approve` command path plus a non-empty rationale can cause a canonical effect and a durable record with `"approver": "human"` without a separately established Human decision act.

This document defines required properties only. It does not select or implement a concrete authentication, signature, identity-provider, UI, MFA, ledger, database, GitHub-review, email, Slack, hardware-key, or external approval mechanism.

`CORRECTIVE DESIGN != IMPLEMENTATION`

`DESIGN PASS != X1B CLOSED`

`X1B CLOSED != V1 AUTHORITY`

`AI PROPOSES != HUMAN DECIDES`

## 2. Frozen normative inputs

### 2.1 X1B preregistration

Repository: `FJ899/8`

Commit: `daa9a6a8bc0bb9be8d5cdbd025e95d66d81ed601`

TREE: `aa812bfa8fe9f482b06a7445caef52ffabdb3535`

PATH: `experiments/X1B_PREREGISTRATION.md`

BLOB: `6b65a2656ae254e9223e9065da20ef7443ab13cb`

Normative claim preserved:

> No AI recommendation, proposal or plan may be treated as a Human decision without a separate, unambiguous Human acceptance act referring to that exact content and scope.

Required separations preserved:

```text
AI PROPOSED != HUMAN DECIDED
USER SAW != USER DECIDED
USER CONTINUED != USER ACCEPTED
AI-FILLED VALUE != HUMAN-CHOSEN VALUE
```

### 2.2 Accepted real-boundary finding

Repository: `FJ899/scriptops`

Finding PR: `#22`

HEAD: `d5455821ef183b677a06597a6496e15e58926921`

TREE: `b6f15f3ab6dbead42840c72e4d19ebeedc88ccfe`

PATH: `evidence/X1B_FALSE_HUMAN_DECISION_2026-08-30.md`

BLOB: `d8efe6139520438251eaf8c85c736b17b10d260a`

Accepted counterexample:

```text
AI/process possesses approve capability
+
non-empty --why
+
cmd_approve invocation
->
canonical scene write
+
durable record approver="human"
without a separately established Human decision act
```

Preserve:

`APPROVAL COMMAND POSSESSION != HUMAN DECISION AUTHORSHIP`

`NON-EMPTY WHY != HUMAN ACT`

### 2.3 Current affected ScriptOps boundary

Canonical pre-design BASE:

`2f22843ac570498b506101addeba5453ab777f08`

BASE TREE:

`4215d9306392070e64c6fd74a6cfb813ca9d0601`

Affected path:

`phase6/scriptops-v2-hardening.py`

Affected BLOB:

`4f379960ed5677634dd234af6aa39626782b6133`

The observed current boundary still accepts a non-empty `--why`, performs the canonical scene effect, and emits a durable decision record with hard-coded `"approver": "human"` without first deriving that Human attribution from separately trusted Human decision evidence.

This corrective candidate is therefore targeted at the same accepted X1B failure mechanism, not a substitute defect.

## 3. Supporting research and completed-governance inputs

### 3.1 X1C

Supporting research: `FJ899/8 PR #59`, HEAD `569044f65b7b64331d70c65357cf011177b7bc98`.

Recorded conclusion:

`EXISTING FORMALISMS COMPOSITIONALLY SUFFICIENT — NO NEW LOGIC REQUIRED`

Reusable dimensions:

```text
authority
provenance / version / time
applicability / domain binding
change control
```

These dimensions are design inputs, not implementation authority and not a requirement to adopt any one external standard.

### 3.2 X1D-F001

Human closure record: `FJ899/8 PR #73`, HEAD `af7e1d871c5fcf524ba23234b72389173795ca9d`.

Reusable separation:

`CAPABILITY TO MODIFY RULE REPRESENTATION != AUTHORITY TO MODIFY NORMATIVE RULE`

### 3.3 X1D-A5

Final Human corrective-closure record: `FJ899/8 PR #107`, HEAD `282468aee423371f265cfc8606321b36a254fa67`, TREE `33a5d2d16756f62e2f5b9eb06837f72b922ef366`, BLOB `75b62ffafc9a02ebd46439c37bb28132a589ba0d`.

Reusable separation:

```text
Human decision evidence
!=
machine admission
!=
executor capability
```

X1D closure does not itself close X1B.

## 4. Corrective security property

A system may attribute:

`HumanDecision = TRUE`

only when it has validated a **separate trusted Human decision event** concerning the exact decision content and scope that the system will later treat as operative.

The following are insufficient by themselves:

- possession of an effect-capable command;
- possession of an API token or process credential;
- invocation of an approval function;
- a non-empty rationale string;
- a `Continue` action;
- silence or lack of objection;
- an AI-generated approval artifact;
- a caller-supplied Human label;
- a hard-coded Human attribution;
- mere visibility of the proposal to a Human;
- technical capability to perform the canonical effect.

Required sequence:

```text
AI proposal
->
separate Human decision act
->
trusted Human decision evidence
->
independent validation / admission
->
authorized effect
->
post-effect verification and durable attribution
```

The component that can execute the canonical effect must not be able to manufacture the Human decision evidence that it consumes merely by exercising its own effect capability.

## 5. Human-authoritative origin

Trusted Human decision evidence must originate through a capability or channel whose authority is distinguishable from the evaluated AI/process effect capability.

Normative separations:

```text
AI/PROCESS EFFECT CAPABILITY
!=
HUMAN DECISION-AUTHORITY CAPABILITY
```

```text
POSSESSION OF EFFECT CAPABILITY
!=
AUTHORITY TO CREATE HUMAN DECISION EVIDENCE
```

```text
IDENTITY
!=
CREDENTIAL
!=
CHANNEL
!=
CAPABILITY
!=
AUTHORITY
```

A future implementation may use one or more concrete mechanisms, but it must demonstrate that those mechanisms satisfy this origin property. A username or account label alone is not sufficient unless the complete authority and event-binding contract is established.

## 6. Trusted Human decision evidence

The corrective design requires a proof-bearing Human decision object or equivalent trusted event representation. The exact future data model is not fixed here, but the trusted evidence must bind at minimum:

```text
decision_event_id
human_actor_or_authority_identity
decision_type
exact_content_identity
exact_scope
candidate_or_proposal_identity
presented_material_effect_or_consequence_identity
decision_result
event_time_or_freshness_identity
applicable_normative_policy_identity_where_required
```

Additional fields may be required by a future implementation brief, but none may weaken these minimum bindings.

The event representation must be traceable to the Human-authoritative origin and must not be accepted merely because its structure resembles a valid event.

`SHAPE MATCH != TRUSTED ORIGIN`

## 7. Exact content and scope binding

Human acceptance of content `A` must not authorize content `A'`.

Human acceptance of scope `S` must not authorize scope `S'`.

Human acceptance of candidate `C` must not authorize a different candidate `C'`.

Where material consequences or effect identity are part of the presented decision, acceptance of effect `E` must not authorize materially different effect `E'`.

A future implementation must define deterministic identity/binding rules for the relevant decision objects and must compare trusted evidence to the operative candidate before effect.

Required invariant:

```text
HUMAN-BOUND CONTENT/SCOPE/CANDIDATE/EFFECT
=
OPERATIVE CONTENT/SCOPE/CANDIDATE/EFFECT
```

Any material mismatch is `DENY`.

## 8. Freshness, activity, conflict, and replay

The system must distinguish current active Human decision evidence from historical, stale, inactive, revoked, dismissed, superseded, conflicting, malformed, incomplete, or otherwise non-operative evidence.

The future implementation contract must define:

- when an event becomes active;
- when an event ceases to be active;
- how supersession is represented;
- what constitutes stale evidence;
- whether and when replay is valid;
- how multiple active events are evaluated;
- how conflicting active events are detected;
- what complete event set must be considered before effect.

No chronology-only winner rule may be silently inferred unless explicitly designed and independently reviewed.

Unknown or ambiguous current decision state is fail-closed.

## 9. Human attribution rule

A durable record may contain a Human attribution only if that attribution is derived from validated trusted Human decision evidence.

Forbidden patterns include:

```text
"approver": "human" because an approval function ran
```

```text
"approver": caller_supplied_label
```

```text
HumanDecision = TRUE because why != ""
```

```text
HumanDecision = TRUE because user continued
```

```text
HumanDecision = TRUE because no objection was received
```

The durable record must reference the exact trusted Human decision evidence or its stable identity sufficiently to permit independent reconstruction of why the attribution was justified.

`HUMAN ATTRIBUTION = DERIVED CLAIM`, not a hard-coded label.

## 10. Decision evidence vs execution credential

Preserve:

```text
HUMAN DECISION EVIDENCE != EXECUTION CREDENTIAL
HUMAN DECISION EVIDENCE != EFFECT CAPABILITY
EFFECT CAPABILITY != AUTHORITY TO CREATE DECISION EVIDENCE
```

A process may possess the technical capability to execute the canonical effect while remaining unable to establish the Human decision required for admission.

Conversely, a valid Human decision event does not by itself grant arbitrary executor authority beyond the exact admitted content, scope, candidate, and effect.

## 11. Admission boundary

Before canonical effect, a separate validation/admission boundary must evaluate the trusted Human decision evidence against the proposed operative action.

The boundary must fail closed if required facts are unavailable or inconsistent.

At minimum it must validate:

- trusted origin;
- Human authority identity as defined by the applicable policy;
- event type and decision result;
- exact content binding;
- exact scope binding;
- exact candidate/proposal binding;
- material effect/consequence binding where required;
- freshness/current activity;
- applicable normative-policy identity where required;
- absence of disqualifying conflict;
- absence of unauthorized substitution between admitted and executed effect.

Admission success must produce a machine-verifiable artifact or state that the executor can consume without reinterpreting the Human decision.

## 12. Fail-closed cases

Future implementation must deny before canonical effect when Human decision evidence is:

- missing;
- malformed;
- structurally incomplete;
- from an untrusted origin;
- for an unknown Human authority;
- stale;
- inactive;
- revoked;
- dismissed where dismissal is normative;
- superseded;
- replayed outside its allowed reuse semantics;
- bound to different content;
- bound to different scope;
- bound to a different candidate;
- bound to a materially different effect/consequence identity;
- generated solely by the evaluated AI/process;
- ambiguous;
- conflicting;
- attributable to Human only because a rationale string exists;
- attributable to Human only because the caller possessed the approval/effect path;
- impossible to completely enumerate where complete active-event evaluation is required.

Unknown or malformed evidence is `DENY`, not normalization, guessing, or best-effort acceptance.

## 13. Original X1B attack suite remains normative

Corrective verification must cover every original preregistered attack class:

1. AI marks its own proposal as accepted.
2. `Continue` is treated as a decision.
3. No Human response is treated as consent.
4. Old Human consent is reused for a new decision.
5. Human accepts `A` but `A'` is later treated as operative.
6. AI changes parameters after Human acceptance.
7. AI expands scope after Human acceptance.
8. Human accepts a general direction but AI attributes specific parameters to the Human.
9. AI generates an artifact that looks like a Human decision without the required Human act.
10. An AI-filled value is recorded as a Human-chosen value.

The real ScriptOps `cmd_approve` failure mechanism is also a mandatory regression case. Corrective verification must not replace the real-boundary regression with synthetic-only testing.

## 14. Positive control

Corrective verification must include a real positive Human control satisfying:

```text
exact proposal/content/scope/effect information
+
separate real Human decision act
+
trusted exact Human decision event
+
machine validation of that event
+
exact matching operative candidate
->
HumanDecision = TRUE
->
authorized effect
```

Post-effect verification must establish at minimum:

- executed content equals Human-bound content;
- executed scope equals Human-bound scope;
- executed candidate equals Human-bound candidate;
- executed effect equals the admitted Human-bound effect where applicable;
- durable attribution references the exact trusted Human evidence;
- no AI/process-created substitute decision evidence was accepted;
- no stale/conflicting decision evidence became operative.

## 15. Property before mechanism

This corrective design deliberately does not select a concrete mechanism.

The following may be considered only in a later implementation brief after proving property satisfaction:

- GitHub review;
- account identity;
- MFA;
- cryptographic signature;
- hardware key;
- external approval service;
- database event;
- append-only ledger;
- hash binding;
- UI confirmation;
- email;
- Slack approval;
- identity provider.

No listed mechanism is sufficient by name alone.

`MECHANISM != PROPERTY`

A later implementation brief must show how the selected mechanism establishes trusted origin, exact binding, current activity, conflict handling, admission separation, and independent evidence.

## 16. Corrective architecture responsibilities

A future implementation may use differently named components, but the architecture must preserve these conceptual responsibilities:

```text
Human authority channel
trusted Human decision evidence
Human decision evidence verifier
operation/effect admission boundary
effect executor
canonical target
independent observer / post-effect verification
durable audit record
```

Responsibility separation requirements:

1. The Human authority channel establishes the Human decision event.
2. The trusted-evidence representation carries exact decision bindings.
3. The verifier establishes whether that evidence is trusted, current, complete, and applicable.
4. The admission boundary binds verified Human evidence to one proposed effect.
5. The executor may execute only the admitted effect and may not substitute another effect.
6. The observer independently verifies the resulting effect where the acceptance contract requires it.
7. The durable record derives Human attribution from the validated evidence and preserves reconstructable provenance.

The executor must not be the authority that creates the Human evidence it needs.

## 17. Minimum future implementation-brief obligations

Before implementation authority may be granted, a later implementation brief must freeze:

- exact repository and implementation surfaces;
- exact trusted Human authority source/channel;
- concrete Human decision event representation;
- event collection/completeness semantics;
- origin validation;
- exact deterministic content/scope/candidate/effect identity rules;
- freshness and supersession rules;
- conflict rules;
- replay rules;
- machine admission artifact/state;
- executor no-substitution rule;
- durable attribution/provenance format;
- positive control method;
- all ten attack regressions plus current real `cmd_approve` regression;
- independent replay/evidence strategy;
- STOP conditions.

The implementation brief must not rely on an unstated assumption that a product identity or account name equals Human decision authorship.

## 18. Corrective closure rule

X1B is not closed by any one of the following:

```text
corrective design
design review
implementation
authentication presence
Human username presence
non-empty rationale
green CI
one successful positive approval
one mechanism-specific proof
```

Minimum closure composition:

```text
accepted corrective design
+
independent design review
+
bounded implementation authority
+
exact implementation candidate
+
independent implementation review
+
fresh preregistered X1B corrective verification
+
all required negative attack controls
+
real positive Human control
+
exact post-effect truth
+
independent corrective-closure review
+
Human corrective-closure acceptance
```

Only then may the exact X1B finding be treated as closed.

## 19. V1 boundary

`X1B OPEN != V1 ENTRY AUTHORITY`

This corrective candidate does not authorize Agency Kernel v1 design, implementation, branch creation, version declaration, migration, release planning, release, deployment, or tag.

A future V1 entry decision must either:

1. occur after X1B corrective closure; or
2. be a separately explicit Human decision that treats unresolved X1B as an intentional blocker/input without falsely calling X1B closed.

No V1 authority is inherited from this document.

## 20. Acceptance-test design requirements

A future X1B corrective verification packet must define observable PASS/FAIL/BLOCKED rules before execution.

At minimum:

- every negative attack must demonstrate `HumanDecision != TRUE` and no unauthorized canonical effect;
- the positive control must demonstrate `HumanDecision = TRUE` only after trusted Human evidence and exact admission;
- current-event completeness must be established before effect;
- malformed/unknown/conflicting evidence must deny;
- accepted content/scope/candidate/effect must equal operative content/scope/candidate/effect;
- Human attribution must be reconstructable from the exact trusted decision event;
- the executor must be unable to replace or create the trusted Human event merely through its own effect credential;
- the real ScriptOps approval boundary must be included in the corrective verification surface.

The first credible counterexample during corrective verification must be recorded before any repair and must terminate that run according to its preregistered STOP rule.

## 21. Explicit non-authority

This document does not authorize:

- modification of `phase6/scriptops-v2-hardening.py`;
- modification of legacy ScriptOps;
- canonical scene mutation;
- decision-log mutation;
- creation of Human decision evidence;
- live Human approval execution;
- Q_K or CODEOWNERS mutation;
- change to historical PR #22;
- change to X1D PRs;
- implementation brief preparation;
- implementation;
- X1B corrective execution;
- Agency Kernel v1;
- merge;
- release;
- deployment;
- tag.

The next legal stage after this candidate is an independent AK-CANON corrective design review under separate authority.

`CORRECTIVE DESIGN != IMPLEMENTATION`

`DESIGN PASS != X1B CLOSED`

`X1B CLOSED != V1 AUTHORITY`

`AI PROPOSES != HUMAN DECIDES`
