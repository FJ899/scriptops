# SOURCE MANIFEST — ScriptOps

## Active runtime / governance-relevant sources

```text
phase6/scriptops-v2-hardening.py
phase6/x1b_human_decision.py
legacy/scriptops-v2-single.py
scripts/restore_v2.py
scripts/verify_repository.py
tests/test_phase6_scriptops_smoke.py
tests/test_x1b_human_decision.py
.github/workflows/x1b-human-decision.yml
README.md
PROJECT_STATE.md
HANDOFF.md
```

`phase6/x1b_human_decision.py` is the active `X1B Human Decision Authorship V2` authority/admission/effect boundary.

`legacy/scriptops-v2-single.py` is now an active **safe compatibility shim** for pre-approval ScriptOps commands. It is intentionally not byte-identical to the historical prototype and cannot create `accepted` state.

## Historical prototype

The original full ScriptOps v2 single-file prototype is a **historical prototype** preserved by transport parts:

```text
sources/prototype/scriptops-v2-single.py.part01
sources/prototype/scriptops-v2-single.py.part02
sources/prototype/scriptops-v2-single.py.part03
sources/prototype/scriptops-v2-single.py.part04
sources/prototype/scriptops-v2-single.py.part05
sources/prototype/scriptops-v2-single.py.part06
sources/prototype/scriptops-v2-single.py.part07
```

Historical identity:

```text
SHA-256 = 881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596
SIZE = 51980 bytes
```

These parts are evidence/reconstruction material only. `scripts/restore_v2.py` may reconstruct them to a non-active output path but must refuse any output that would overwrite `legacy/scriptops-v2-single.py`.

## Historical evidence retained

Existing Phase-6, P3, continuity and reconstruction evidence remains historical provenance. It does not establish X1B closure and must not reactivate the old `approve --why` Human-attribution semantics.

## Active Human approval route

```text
approve --scene <SCN-ID> --decision-pr <PR-NUMBER>
```

Authority derives from the exact verified X1B V2 GitHub Human review and never from `--why`, caller identity or the historical prototype.
