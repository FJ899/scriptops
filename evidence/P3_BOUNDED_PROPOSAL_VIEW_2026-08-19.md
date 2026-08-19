# P3 BOUNDED PROPOSAL VIEW — CROSS-SCENE COHERENCE

Date: 2026-08-19
Status: `IMPLEMENTATION CANDIDATE / TECHNICALLY OBSERVED / HUMAN ACCEPTANCE PENDING`
Semantic scope: `MINIMAL CROSS-SCENE PROPOSAL VIEW / NO ATOMIC APPROVAL / NO MATURITY CLAIM`

## 1. Human decision

`AKCEPTUJĘ KIERUNEK SCRIPTOPS: MINIMALNY BOUNDED PROPOSAL VIEW DLA CROSS-SCENE COHERENCE, BEZ ATOMIC APPROVAL`

This decision authorizes the bounded capability direction. It does not itself accept the implementation candidate, merge it, approve SCN-012/SCN-027, or authorize atomic multi-scene approval.

## 2. Observed blocker from Real Workload 002

Integrated evidence before this candidate established:

- `DEPENDENCY PRESENT: YES`
- `UPSTREAM CANDIDATE: STAGED`
- `DOWNSTREAM CONTEXT SOURCE: OLD CANONICAL`
- `CROSS-SCENE CANDIDATE COHERENCE: BLOCKED`
- `CANONICAL EFFECT: NOT APPLIED`
- `HUMAN APPROVAL: NOT REQUESTED`
- `GOAL DONE: NO`

The concrete defect was not merely missing dependency analysis. A downstream rewrite context could not see an explicitly relevant staged upstream proposal before Human approval because legacy scene resolution preferred canonical `scenes/` state.

## 3. Minimal candidate

The implementation intentionally does not change legacy/global scene resolution order.

New explicit helper:

`phase6/bounded-proposal-view.py`

It provides two narrow operations:

1. `bind` — persist one exact upstream proposal identity into an existing downstream task pack;
2. `context-build` — build that downstream task's context using only those exact task-bound proposal identities.

A binding records:

- exact repository-relative candidate path;
- exact full-file SHA256;
- existing exact `REVIEW_REQUIRED` impact evidence remains required.

The helper also requires:

- candidate under `staging/scenes`;
- regular non-symlink single-hardlink file;
- exact scene-specific candidate filename;
- front matter `scene_id` match;
- `status: candidate`;
- graph adjacency between the downstream task target and bound upstream scene;
- task target and requested context-build scene to match.

## 4. Semantic boundary

This capability means:

`explicit task binding → exact proposal identity → bounded context resolution`

It does **not** mean:

`staging globally outranks canon`.

Unbound scenes retain the existing canonical-first resolver. A bound proposal is labeled in the generated context pack as:

- `BOUNDED_NONCANONICAL`
- `PROPOSAL_NOT_CANON`

Binding does not approve, merge, mutate or otherwise promote the candidate.

## 5. SCN-012 ↔ SCN-027 regression

The Human-provided real workload remains the regression target.

Observed on implementation head `834300d9c20201f423b6f2bd268cc328d968d960`:

- `Verify repository state` #40 / run `32230752024`: SUCCESS
- `Phase 6 ScriptOps smoke` #20 / run `32230751885`: SUCCESS
- unittest result: `Ran 13 tests ... OK`

The dedicated bounded-proposal tests establish:

### Exact binding

`EXPLICIT_BINDING=PASS`

`DOWNSTREAM_CONTEXT_SOURCE=BOUND_CANDIDATE`

SCN-027 context contains the staged no-carrier SCN-012 proposal, including the one-time-link / encrypted-source-package semantics, instead of the old SCN-012 line `Oryginał schowamy w sejfie`.

### No global precedence

The integrated Run-002 regression still passes and still observes `DOWNSTREAM_CONTEXT_SOURCE=OLD_CANONICAL` when ordinary Phase-6 context-build is used without the bounded helper.

Therefore the implementation does not silently convert staging into project truth.

### Identity drift

After a task binds a candidate, changing that candidate's file identity causes bounded context-build to fail closed on SHA mismatch.

### Missing binding

Calling bounded context-build without an explicit binding fails closed rather than selecting a staged candidate automatically.

### Consequences

Both SCN-012 and SCN-027 canonical files remain unchanged during the tests and no Human decision log is created by the bounded proposal operation.

## 6. Current interpretation

The specific Run-002 context-coherence blocker has a technically observed minimal candidate fix.

This does **not** yet establish:

- Human acceptance of the implementation;
- merge authority;
- canonical SCN-012 rewrite;
- canonical SCN-027 rewrite;
- correctness of the encrypted-storage HOW as project meaning;
- all-project dependency coverage;
- atomic/multi-artifact approval;
- ScriptOps maturity;
- product activation;
- model/API integration;
- release/deploy/tag;
- secrets, credentials or spending;
- ownership transfer to Saddle, COS, Executor or another layer.

## 7. Next gate

Fresh exact-head CI after this evidence record and its lock must pass before requesting Human acceptance of the implementation PR.
