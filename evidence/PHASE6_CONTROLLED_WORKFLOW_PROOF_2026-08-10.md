# ScriptOps Phase 6 — Controlled Workflow Proof

Date: 2026-08-10
Status: `CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM`

## Human decision under test

`DEC-SO-010`:

```text
DECISION: YES
BASE: legacy/scriptops-v2-single.py
REWRITE: NO
NEW CAPABILITY: NO
PHASE 6: reuse + hardening + proof
MATURITY CLAIM: NONE
FUNCTIONAL_SADDLE_ACCEPTED: NOT YET
```

## Implementation boundary

The historical v2 file is not rewritten. `phase6/scriptops-v2-hardening.py` loads it as the execution substrate and closes only B1–B5 identified in `analysis/RC1_V2_GAP_2026-08-10.md`.

No model API, browser automation, autonomous approval, agent framework, multi-agent, GUI, vector DB, semantic graph or multi-user capability was added.

## Controlled path proved

The deterministic smoke creates a fresh temporary Git-backed ScriptOps project and executes:

```text
review
→ durable task checkpoint
→ check-pre
→ durable preflight evidence
→ context-build
→ durable context checkpoint
→ manual candidate artifact
→ durable candidate-input checkpoint
→ check-post validation/staging
→ impact report
→ explicit human-style approve --why
→ canonical accepted scene write
→ recomputed accepted scene hash
→ decision log
→ Git commit
```

The test also proves:

- each generated intermediate checkpoint leaves the working tree clean;
- unrelated dirty state blocks candidate import;
- `approve` cannot be invoked without `--why`;
- the candidate is a proposal artifact and the canonical target is reported unchanged before approval;
- the accepted scene's declared hash matches accepted content after the status transition;
- decision log records `why`, task ID, impact-report reference, candidate hash and accepted scene hash;
- Git history contains explicit checkpoints and the final acceptance commit.

## GitHub Actions evidence

PR: `litrgratis-pixel/scriptops#7`

Final verified implementation head before this evidence commit:

`f5560719530ffe07c5f61524007839431eee43e1`

Observed runs for that head:

1. `Phase 6 ScriptOps smoke`
   - run id: `31421551632`
   - run number: `5`
   - conclusion: `success`

2. `Verify repository state`
   - run id: `31421551982`
   - run number: `15`
   - conclusion: `success`

The existing repository verifier had initially failed because it still asserted the historical `ACCESS CHECK REQUIRED` state even after PR #6 had advanced the repo to the base-selection gate. The verifier was updated to test the current Phase-6 state, preserve historical v2 byte identity and include the bounded hardening proof contract. It then passed on the same head as the workflow smoke.

## B1–B5 result

| Blocker | Result | Evidence |
|---|---|---|
| B1 task creation vs clean preflight | PASS | task is committed as a checkpoint before preflight |
| B2 generated artifacts dirty approval path | PASS | preflight/context/candidate input/impact are explicit checkpoints; unrelated dirt blocks |
| B3 stale accepted hash | PASS | canonical accepted file is written through `write_scene_file` after status change; smoke recomputes and matches |
| B4 approval rationale absent | PASS | CLI requires non-empty `--why`; decision log persists it |
| B5 impact report / smoke proof absent | PASS | persisted `impact-report.json` plus GitHub Actions end-to-end smoke |

## What this proves

It proves that the existing ScriptOps v2 substrate can be hardened, without rewrite or new capability, into one controlled end-to-end effect path where a proposal artifact does not become canonical until an explicit human rationale is supplied, and the resulting accepted identity/evidence are durable.

## What this does NOT prove

- no ScriptOps v5/RC1 maturity claim;
- no independent external user test;
- no production narrative-value claim;
- no AI model quality claim;
- no live Saddle ModelGateway → Executor run;
- no production identity/request-origin provider;
- no `FUNCTIONAL_SADDLE_ACCEPTED`.

The Saddle live Sol/Terra (or current approved equivalent) benchmark/effect-path evidence remains open and is the next capability proof after this bounded workflow slice is merged.
