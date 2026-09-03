# ScriptOps v2 prototype reconstruction — HISTORICAL ONLY

The seven `sources/prototype/scriptops-v2-single.py.partNN` files preserve the original 2026-08 prototype as historical evidence.

They are **HISTORICAL ONLY** and must not overwrite `legacy/scriptops-v2-single.py`.

The active legacy path is now an X1B-safe compatibility shim whose direct `approve` and `scene-promote --to accepted` paths fail before mutation. Restoring the historical executable over that path would reintroduce the accepted X1B defect.

## Integrity check

```bash
python scripts/restore_v2.py --check-only
```

Expected historical identity:

```text
SHA-256: 881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596
Size: 51980 B
```

The validator reconstructs the seven parts in memory, checks SHA-256, byte count, UTF-8 and Python syntax. It intentionally does **not** require the active legacy shim to equal those historical bytes.

## Optional reconstruction to a non-active path

```bash
python scripts/restore_v2.py
```

Default output:

```text
recovered/historical-scriptops-v2-single.py
```

or choose another non-active path:

```bash
python scripts/restore_v2.py --output /tmp/historical-scriptops-v2-single.py
```

An attempt to use:

```text
--output legacy/scriptops-v2-single.py
```

must fail closed, including with `--force`.

## Active route

The active canonical acceptance route is `X1B Human Decision Authorship V2` through `phase6/scriptops-v2-hardening.py` and `phase6/x1b_human_decision.py`.

Historical reconstruction is evidence preservation, not implementation authority, Human approval or canonical effect authority.
