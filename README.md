# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Current security route

`X1B Human Decision Authorship V2` is the active acceptance mechanism in this implementation candidate.

The old rule that a non-empty `--why` could be treated as Human approval is retired. **--why is not Human authority**. Proposal rationale may still exist as proposer/process text, but it cannot establish Human authorship.

Canonical scene acceptance is invoked only as:

```text
approve --scene <SCN-ID> --decision-pr <PR-NUMBER>
```

and follows this boundary:

```text
proposal/candidate
-> exact HumanDecisionRequestV2 + exact accepted-scene presentation in FJ899/8
-> APPROVED GitHub review by durable Human user ID 226907434
-> isolated credential-free GitHubDecisionReaderV2
-> X1BOperationAdmissionV2
-> prospective two-path Git commit
-> atomic refs/heads/main old->new compare-and-swap
-> worktree/index synchronization and post-effect verification
-> HumanDecision=TRUE only after post-effect verification
```

`AI PROPOSES != HUMAN DECIDES` remains normative.

## Human authority

The authority selector is GitHub numeric user ID `226907434`, not a mutable login string. The exact Human review body is bound to the request digest and the immutable `review.commit_id`. Comments, labels, reactions, `Continue`, caller identity, proposal rationale and Human-looking AI text are not decision evidence.

The GitHub authority reader runs in a dedicated isolated Python child with a fresh environment, direct verified TLS to `api.github.com:443`, no Authorization header, no proxy input and no caller-selected CA bundle. The parent independently revalidates all returned evidence.

## Canonical effect

A successful X1B acceptance changes exactly:

```text
.scriptops/decision-log.ndjson
scenes/<SCN-ID>.fountain
```

The executor constructs and verifies a prospective commit first. `refs/heads/main` advances only through an old-value compare-and-swap. Git author/committer identity is `ScriptOps X1B Executor <scriptops-x1b@example.invalid>`, never the Human.

A durable X1B record derives Human attribution from the verified review and carries the request/review/admission chain. Generic `approver="human"` is forbidden.

## Active files

```text
phase6/scriptops-v2-hardening.py   Phase-6 pre-approval workflow + X1B approve CLI
phase6/x1b_human_decision.py       Human authority, admission, anchored Git and CAS executor
legacy/scriptops-v2-single.py      safe compatibility shim; legacy accepted-state routes disabled
scripts/verify_repository.py       active/historical consistency verification
scripts/restore_v2.py              historical reconstruction only; cannot overwrite active legacy shim
```

## Historical prototype

The original 2026-08 single-file prototype is preserved only as historical reconstruction material in:

```text
sources/prototype/scriptops-v2-single.py.part01 ... part07
```

It is not the active approval executable. `scripts/restore_v2.py` deliberately refuses to restore those historical bytes over `legacy/scriptops-v2-single.py`.

Historical Phase-6/P3 evidence remains provenance and is not relabeled as X1B closure.

## Tests

```bash
python -m unittest -v tests.test_x1b_human_decision tests.test_phase6_scriptops_smoke
python scripts/verify_repository.py
python scripts/restore_v2.py --check-only
```

CI entrypoint:

```text
.github/workflows/x1b-human-decision.yml
```

## Governance state

This branch is an **X1B implementation candidate**, not corrective closure. It authorizes no live Human decision-evidence PR, real positive control, canonical screenplay effect, merge, release, deployment, Agency Kernel V1 or maturity claim.

The legal sequence remains:

```text
implementation candidate
-> independent implementation review
-> preregistered corrective-verification packet
-> separate Human execution authorization
-> negative matrix + real Human positive control
-> independent closure review
-> Human closure acceptance
```

Only the final Human closure acceptance can close X1B.
