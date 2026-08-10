# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Status

`PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM`

Jawna decyzja użytkownika: `legacy/scriptops-v2-single.py` jest bazą Phase 6. `REWRITE: NO`. `NEW CAPABILITY: NO`.

## Uruchomienie nowej sesji

Nowe AI ma przeczytać w tej kolejności:

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`
6. `analysis/RC1_V2_GAP_2026-08-10.md`
7. `IDEA_ARCHIVE.md`
8. `SOURCE_MANIFEST.md`
9. `RECONSTRUCTION_REPORT.md`

## Zasady nadrzędne

- odpowiedź AI jest kandydatem, nie prawdą projektu;
- zmiana kanonu wymaga walidacji, decyzji człowieka, uzasadnienia i zapisu w Git;
- candidate artifact nie jest kanonicznym efektem;
- kanoniczny zapis Phase 6 następuje dopiero po `approve --why`;
- smoke proof nie jest maturity claim;
- nie wolno rozszerzać zakresu o nowe capability;
- pełne rozmowy i dane prywatne pozostają poza aktywnym drzewem.

## Phase 6 — reuse + hardening + proof

Wybrana historyczna baza:

```text
legacy/scriptops-v2-single.py
```

Historyczny plik pozostaje niezmieniony. Ograniczony hardening:

```text
phase6/scriptops-v2-hardening.py
```

zamknął B1–B5:

1. task clean-tree checkpoint;
2. generated evidence/candidate-input lifecycle;
3. fresh accepted hash;
4. mandatory human `why`;
5. impact report + deterministic smoke proof.

Evidence:

```text
evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md
```

## Testy

```bash
python -m unittest discover -s tests -p 'test_phase6_*.py' -v
python scripts/verify_repository.py
```

Na zweryfikowanym head PR #7 oba GitHub Actions checks zakończyły się sukcesem; finalny head po zapisaniu evidence również musi pozostać zielony przed merge.

## Zakaz rozbudowy

Nie dodawać browser helpera, direct model/API automation, autonomous approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph ani multi-user.

## Co dalej

Po merge Phase 6 wynik wraca do Saddle. Następnym brakującym dowodem jest live AI-worker benchmark/effect path; ScriptOps nie powinien być dalej rozbudowywany przed tym gate'em.

`MATURITY CLAIM`: **NONE**.

`FUNCTIONAL_SADDLE_ACCEPTED`: **NOT YET**.
