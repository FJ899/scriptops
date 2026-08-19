# P3 REAL WORKLOAD 002 — SCENA 27 / downstream dependency on Scene 12

Date: 2026-08-19
Status: `OBSERVED WORKING RESULT / DEPENDENCY PRESENT / CROSS-SCENE CANDIDATE COHERENCE BLOCKED / NO CANONICAL APPROVAL`
Authority: `USER-PROVIDED DOWNSTREAM TEST MATERIAL`
Semantic scope: `P3 WORKING EVALUATION / NOT MATURITY CLAIM / NOT PRODUCT ACTIVATION`

## 1. Observed result

Fresh execution on PR #13 established:

- `DEPENDENCY PRESENT: YES`
- `UPSTREAM CANDIDATE: STAGED`
- `DOWNSTREAM CONTEXT SOURCE: OLD CANONICAL`
- `CROSS-SCENE CANDIDATE COHERENCE: BLOCKED`
- `CANONICAL EFFECT: NOT APPLIED`
- `HUMAN APPROVAL: NOT REQUESTED`
- `GOAL DONE: NO`

Exact evidence run before this record update:

- `Phase 6 ScriptOps smoke` #17 / run `32229072060`: SUCCESS
- `Verify repository state` #36 / run `32229072057`: SUCCESS

The smoke log explicitly emitted:

`P3_REAL_WORKLOAD_002: DEPENDENCY_PRESENT=YES; UPSTREAM_CANDIDATE=STAGED; DOWNSTREAM_CONTEXT_SOURCE=OLD_CANONICAL; CROSS_SCENE_CANDIDATE_COHERENCE=BLOCKED; CANONICAL_EFFECT=NOT_APPLIED; HUMAN_APPROVAL=NOT_REQUESTED; GOAL_DONE=NO`

This is a fail-closed result, not a product failure claim and not authority to implement a new mechanism.

## 2. Why this workload exists

Real Workload 001 established:

- local rewrite candidate for SCN-012: observed PASS;
- canonical effect before Human approval: not applied;
- downstream dependency coverage: insufficient evidence;
- goal DONE: NO.

The missing evidence was a real later scene that actually depends on the physical-carrier semantics. The Human supplied SCN-027, which directly depends on all of the sensitive meanings identified in Run 001.

## 3. Human-provided downstream material

`SCENA 27 — MIESZKANIE ADAMA / NOC`

Adam zamyka drzwi na dwa zamki i podchodzi do biurka.

Telefon wibruje.

**ANNA:** Masz jeszcze oryginał?

Adam otwiera dolną szufladę. Wyciąga czerwony pendrive.

**ADAM:** Mam.

**ANNA:** Kopia z mojego laptopa zniknęła. Ktoś ją usunął.

Adam patrzy na pendrive, ale nie podłącza go do komputera.

**ADAM:** Czyli zostało tylko to, co jest u mnie.

Po drugiej stronie zapada cisza.

**ANNA:** Nie wkładaj go do żadnego komputera. I nie oddawaj nikomu.

Adam chowa pendrive z powrotem do szuflady i przekręca klucz.

**ADAM:** Bez mojego udziału nikt tych danych nie dostanie.

Rozłącza się.

## 4. Dependency reconstruction

SCN-027 proves that the Scene-12 change is not a local prop substitution. It depends on at least these meanings:

1. `oryginał` — SCN-027 assumes a uniquely privileged surviving source;
2. `czerwony pendrive` — the source is embodied as a physical object;
3. `kopia z laptopa Anny` — a secondary copy can disappear independently;
4. `zostało tylko to, co jest u mnie` — Adam retains sole possession/control of the remaining source;
5. `nie wkładaj go do żadnego komputera` — risk is expressed as connecting a physical carrier;
6. `nie oddawaj nikomu` — access control is expressed as custody of the object;
7. `szuflada + klucz` — source security is expressed as physical storage;
8. `bez mojego udziału nikt tych danych nie dostanie` — the dramatic invariant is Adam's exclusive control, not the pendrive itself.

The Human-owned goal therefore requires at least a coherent two-scene proposal, not merely a rewritten SCN-012.

## 5. Candidate semantic mapping — recommendation only

A no-physical-carrier interpretation can preserve the dramatic invariant by mapping:

- physical `oryginał` → authoritative source package in encrypted remote storage;
- Adam's possession of the pendrive → Adam's exclusive control of access to the source package;
- Anna's deleted laptop copy → unchanged as a lost local working copy;
- `nie wkładaj go do komputera` → do not open/download the source package on an untrusted machine;
- `nie oddawaj nikomu` → do not share/redelegate access;
- locked drawer → no longer a valid data-custody mechanism unless it protects some non-data credential artifact, which would itself require a separate decision;
- `bez mojego udziału...` → can remain semantically true if Adam alone controls access.

A possible SCN-027 rewrite exists, but this run deliberately does not promote or stage it because the mechanism did not provide SCN-027 with the staged SCN-012 proposal as dependency context.

This mapping is `AI RECOMMENDATION / NOT HUMAN DECISION / NOT CANON`.

## 6. Mechanism question and answer

Frozen question:

> After a validated SCN-012 no-carrier candidate is staged but not approved, does ScriptOps build the SCN-027 rewrite context against that staged upstream candidate, or against the old canonical SCN-012 that still contains the pendrive?

Observed answer:

> `OLD CANONICAL SCN-012`.

The SCN-027 context included the old physical-carrier lines, including the red pendrive and the physical-safe original semantics. It did not include the staged no-carrier candidate's one-time link / encrypted source-package semantics.

Therefore ScriptOps currently cannot establish a coherent multi-scene proposal state across SCN-012 → SCN-027 before Human approval.

## 7. Mechanism cause observed

Current `ContextBuilder._load_scene_card` checks the canonical `scenes/` directory before `staging/scenes/`.

With both representations present:

```text
SCN-012 accepted old canon (pendrive)
+ SCN-012 staged new candidate (no pendrive)
+ SCN-027 depends_on SCN-012
→ context-build SCN-027 reads old accepted SCN-012 first
```

The dedicated test established that this path occurs in execution.

## 8. Evaluation path

Dedicated test:

`tests/test_phase6_p3_real_workload_002.py`

The test creates a fresh temporary ScriptOps project with:

- accepted SCN-012 containing the physical pendrive;
- accepted SCN-027 containing the Human-provided downstream dependency;
- explicit graph relation `SCN-012 spoils_or_sets_up SCN-027` and `SCN-027 depends_on SCN-012`;
- a validated/staged no-carrier SCN-012 candidate;
- no Human approval and no canonical SCN-012 write.

It then builds the rewrite context for SCN-027 and verifies which upstream representation is actually present.

## 9. Meaning of the result

This run narrows the highest current P3 constraint:

- ScriptOps can safely govern one-scene candidate/effect authority;
- a real downstream dependency can be represented;
- but the current context model cannot compose an unapproved upstream candidate into a downstream proposal context;
- therefore the project-wide Human goal cannot yet be honestly declared DONE.

The next architectural/implementation question is whether ScriptOps should support a bounded multi-artifact proposal/change-set view before Human approval. That is a potential new capability/behavior and is **not authorized by this evidence record**.

## 10. Must not be inferred

This workload does not authorize or establish:

- canonical rewrite of SCN-012;
- canonical rewrite of SCN-027;
- approval of the proposed encrypted-storage HOW;
- implementation of a multi-scene change-set, transaction layer or impact engine;
- ScriptOps maturity;
- product activation;
- model/API integration;
- release/deploy/tag;
- new secrets, credentials or spending;
- whole-project downstream coverage beyond the supplied SCN-027.
