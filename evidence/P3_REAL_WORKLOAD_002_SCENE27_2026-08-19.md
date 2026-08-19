# P3 REAL WORKLOAD 002 — SCENA 27 / downstream dependency on Scene 12

Date: 2026-08-19
Status: `EVALUATION CANDIDATE / CI PENDING / NO CANONICAL APPROVAL`
Authority: `USER-PROVIDED DOWNSTREAM TEST MATERIAL`
Semantic scope: `P3 WORKING EVALUATION / NOT MATURITY CLAIM / NOT PRODUCT ACTIVATION`

## 1. Why this workload exists

Real Workload 001 established:

- local rewrite candidate for SCN-012: observed PASS;
- canonical effect before Human approval: not applied;
- downstream dependency coverage: insufficient evidence;
- goal DONE: NO.

The missing evidence was a real later scene that actually depends on the physical-carrier semantics. The Human supplied SCN-027, which directly depends on all of the sensitive meanings identified in Run 001.

## 2. Human-provided downstream material

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

## 3. Dependency reconstruction

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

## 4. Candidate semantic mapping — recommendation only

A no-physical-carrier interpretation can preserve the dramatic invariant by mapping:

- physical `oryginał` → authoritative source package in encrypted remote storage;
- Adam's possession of the pendrive → Adam's exclusive control of access to the source package;
- Anna's deleted laptop copy → unchanged as a lost local working copy;
- `nie wkładaj go do komputera` → do not open/download the source package on an untrusted machine;
- `nie oddawaj nikomu` → do not share/redelegate access;
- locked drawer → no longer a valid data-custody mechanism unless it protects some non-data credential artifact, which would itself require a separate decision;
- `bez mojego udziału...` → can remain semantically true if Adam alone controls access.

A possible SCN-027 rewrite exists, but this run deliberately does not promote or stage it until the mechanism proves that its downstream context can see the staged SCN-012 proposal rather than the old accepted SCN-012.

This mapping is `AI RECOMMENDATION / NOT HUMAN DECISION / NOT CANON`.

## 5. Mechanism question

The critical test is now narrower and falsifiable:

> After a validated SCN-012 no-carrier candidate is staged but not approved, does ScriptOps build the SCN-027 rewrite context against that staged upstream candidate, or against the old canonical SCN-012 that still contains the pendrive?

If SCN-027 receives the old canonical upstream scene, ScriptOps cannot yet prove a coherent multi-scene proposal before Human approval.

## 6. Current implementation observation

Current `ContextBuilder._load_scene_card` checks the canonical `scenes/` directory before `staging/scenes/`.

For a downstream scene with `depends_on: [SCN-012]`, the context builder therefore has a plausible false-coherence path:

```text
SCN-012 accepted old canon (pendrive)
+ SCN-012 staged new candidate (no pendrive)
+ SCN-027 depends_on SCN-012
→ context-build SCN-027 may read old accepted SCN-012 first
```

This is an implementation observation, not yet the test verdict. The dedicated regression must establish the behavior in execution.

## 7. Evaluation path

Dedicated test:

`tests/test_phase6_p3_real_workload_002.py`

The test creates a fresh temporary ScriptOps project with:

- accepted SCN-012 containing the physical pendrive;
- accepted SCN-027 containing the Human-provided downstream dependency;
- explicit graph relation `SCN-012 spoils_or_sets_up SCN-027` and `SCN-027 depends_on SCN-012`;
- a validated/staged no-carrier SCN-012 candidate;
- no Human approval and no canonical SCN-012 write.

It then builds the rewrite context for SCN-027 and checks which upstream representation is actually present.

## 8. Expected fail-closed interpretation

If the SCN-027 context contains the old physical-carrier SCN-012 while a staged no-carrier candidate exists, record:

- `DEPENDENCY PRESENT: YES`
- `UPSTREAM CANDIDATE: STAGED`
- `DOWNSTREAM CONTEXT SOURCE: OLD CANONICAL`
- `CROSS-SCENE CANDIDATE COHERENCE: BLOCKED`
- `CANONICAL EFFECT: NOT APPLIED`
- `HUMAN APPROVAL: NOT REQUESTED`
- `GOAL DONE: NO`

That result is useful evidence. It must not be silently converted into a request to approve either scene.

## 9. Must not be inferred

This workload does not authorize or establish:

- canonical rewrite of SCN-012;
- canonical rewrite of SCN-027;
- approval of the proposed encrypted-storage HOW;
- a new impact-engine or transaction capability;
- ScriptOps maturity;
- product activation;
- model/API integration;
- release/deploy/tag;
- new secrets, credentials or spending;
- whole-project downstream coverage beyond the supplied SCN-027.
