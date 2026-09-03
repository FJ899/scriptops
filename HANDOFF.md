# HANDOFF — ScriptOps X1B

```yaml
project: ScriptOps
current_route: "X1B Human Decision Authorship V2"
status: "IMPLEMENTATION CANDIDATE / NOT CLOSED"
implementation_base: "2f22843ac570498b506101addeba5453ab777f08"
implementation_branch: "impl/x1b-human-decision-v2-20260903"
next_step: "independent_implementation_review_then_corrective_verification_preregistration"
blocker: "SEPARATE HUMAN EXECUTION AUTHORIZATION REQUIRED BEFORE REAL POSITIVE CONTROL OR CANONICAL EFFECT"
```

## Resume contract

Read in order:

1. `README.md`
2. `PROJECT_STATE.md`
3. this `HANDOFF.md`
4. `phase6/x1b_human_decision.py`
5. `phase6/scriptops-v2-hardening.py`
6. `tests/test_x1b_human_decision.py`
7. `SOURCE_MANIFEST.md`

Governing external brief/review chain is FJ899/8 PR #155 + PR #158 with independent PASS in PR #159.

## Active approval command

```text
approve --scene <SCN-ID> --decision-pr <PR-NUMBER>
```

**--why is not Human authority**. Do not recover `approve --why`, generic `approver="human"`, direct legacy approval or `scene-promote --to accepted` as active semantics.

## Authority chain

`X1B Human Decision Authorship V2`:

```text
separate Human GitHub APPROVED review by user.id 226907434
+ exact X1B-HUMAN-DECISION-V2 request digest
+ immutable review.commit_id evidence files
-> isolated GitHubDecisionReaderV2
-> parent independent evidence revalidation
-> X1BOperationAdmissionV2
-> AnchoredGitV2 + common-dir lock
-> prospective two-path commit
-> atomic refs/heads/main compare-and-swap
-> exact post-effect verification
-> HumanDecision=TRUE only after post-effect verification
```

The Human login is audit/display metadata only. Numeric GitHub user ID is the authority selector.

## TLS boundary

Authority HTTP executes only in a fresh isolated Python child. Parent environment is not inherited. The child uses stdlib verified TLS directly to `api.github.com:443`, no Authorization, proxy, caller CA path or alternate URL input.

## Canonical effect

Exactly two tracked paths:

```text
.scriptops/decision-log.ndjson
scenes/<SCN-ID>.fountain
```

Git author/committer is the machine executor, not the Human. The durable decision record derives Human attribution from the verified review chain.

## Legacy and recovery

`legacy/scriptops-v2-single.py` is a safe active compatibility shim; its accepted-state routes are disabled before mutation.

The full 2026-08 prototype bytes survive only under `sources/prototype/` as historical reconstruction. `scripts/restore_v2.py` must not overwrite `legacy/scriptops-v2-single.py` with them.

## Tests

```text
python -m unittest -v tests.test_x1b_human_decision tests.test_phase6_scriptops_smoke
python scripts/verify_repository.py
python scripts/restore_v2.py --check-only
```

CI: `.github/workflows/x1b-human-decision.yml`.

## STOP / Human gate

Implementation review and preregistration may proceed without executing the real Human effect. Before any real positive control or canonical screenplay effect:

```text
STOP
REQUIRE SEPARATE HUMAN EXECUTION AUTHORIZATION
```

No merge, X1B closure, Agency Kernel V1, release, deployment or tag is implied.
