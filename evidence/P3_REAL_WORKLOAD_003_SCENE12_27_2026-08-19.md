# P3 REAL WORKLOAD 003 — SCN-012 → SCN-027 BOUNDED PROPOSAL COHERENCE

Date: 2026-08-19
Status: OBSERVED EVIDENCE / TECHNICALLY VERIFIED / HUMAN ACCEPTANCE PENDING

## Human-owned goal under test

> Completely remove the pendrive from the project and replace it with a way of transferring data that requires no physical carrier, while preserving scene logic and all resulting later dependencies.

This goal is Human-owned. This evidence record does not change or complete it.

## Prior observed blocker

P3 Real Workload 002 established:

- SCN-012 no-carrier candidate could be staged;
- SCN-027 contained a real dependency on original/copy/Adam-control semantics;
- ordinary downstream context still consumed old canonical SCN-012;
- result: `CROSS_SCENE_CANDIDATE_COHERENCE=BLOCKED / GOAL_DONE=NO`.

The Human then accepted the minimal direction `BOUNDED PROPOSAL VIEW / NO ATOMIC APPROVAL`, and PR #14 integrated that capability.

## Run 003 execution

The deterministic evaluation fixture used the real SCN-012 ↔ SCN-027 dependency and the integrated Phase-6 mechanisms:

1. create accepted fixture versions of the Human-provided SCN-012 and SCN-027;
2. create the SCN-012 rewrite task for the Human-owned no-carrier goal;
3. run Phase-6 preflight + context build;
4. stage the already-observed no-carrier SCN-012 proposal through normal `check-post`;
5. create the downstream SCN-027 rewrite task;
6. bind exact `SCN-012-v2-candidate.fountain` to that task by path + SHA256;
7. run Phase-6 preflight;
8. build SCN-027 context with the bounded proposal view;
9. verify that context consumes the bound no-carrier SCN-012 proposal rather than old canonical SCN-012;
10. materialize an AI-proposed SCN-027 rewrite from that bounded context;
11. run normal `check-post` and stage `SCN-027-v2-candidate.fountain`;
12. stop before any `approve --why`.

## AI proposal semantics observed in the fixture

### SCN-012 proposal

The staged upstream proposal replaces the physical carrier with:

- a one-time access link;
- encrypted transfer;
- local working copy on Anna's laptop;
- a source package remaining in encrypted remote storage.

This is an AI proposal, not Human-accepted screenplay canon.

### SCN-027 proposal

The staged downstream proposal adapts the later dependency so that:

- Anna asks whether Adam still has access to the source;
- Anna's laptop copy has been deleted;
- the only remaining source is the encrypted source package;
- Adam retains control of access;
- Anna tells Adam not to open it from any computer and not to share access;
- Adam states that nobody gets the data without his participation.

The proposal contains no physical data carrier and no pendrive.

This is an AI proposal, not Human-accepted screenplay canon.

## Observed result

`P3_REAL_WORKLOAD_003: BOUNDED_UPSTREAM_CONTEXT=PASS; DOWNSTREAM_CANDIDATE=STAGED; CROSS_SCENE_PROPOSAL_COHERENCE=OBSERVED_PASS; CANONICAL_EFFECT=NOT_APPLIED; HUMAN_APPROVAL=NOT_REQUESTED; GOAL_DONE=NO`

Interpretation:

- `BOUNDED_UPSTREAM_CONTEXT: PASS`
- `DOWNSTREAM_CANDIDATE: STAGED`
- `CROSS-SCENE PROPOSAL COHERENCE: OBSERVED PASS for this bounded SCN-012 ↔ SCN-027 workload`
- `CANONICAL EFFECT: NOT APPLIED`
- `HUMAN APPROVAL: NOT REQUESTED`
- `GOAL DONE: NO`
- `FALSE SUCCESS: BLOCKED`

## Technical verification

Initial exact-head candidate: `fd9a00b3d29ed490df304a73a4f6fa0332222ce8`

GitHub Actions:

- `Verify repository state` #49 / run `32266537521`: SUCCESS
- `Phase 6 ScriptOps smoke` #27 / run `32266537471`: SUCCESS
- deterministic Phase-6 suite: 16/16 PASS

The smoke log explicitly printed the Run 003 result above.

## Authority and scope boundaries

This record DOES establish observed technical evidence that the integrated bounded proposal view can support a coherent two-scene proposal for this real dependency.

This record DOES NOT establish:

- Human acceptance of the SCN-012 rewrite proposal;
- Human acceptance of the SCN-027 rewrite proposal;
- canonical modification of either scene;
- atomic or multi-artifact approval;
- whole-project dependency completeness beyond the supplied SCN-012 ↔ SCN-027 material;
- product maturity or general screenplay-project correctness;
- the Human-owned goal as DONE;
- release/deploy/tag authority;
- secrets/credentials/spending authority;
- ownership transfer to Saddle, COS, Executor, or any other layer.

No `approve --why` was executed in this run.
