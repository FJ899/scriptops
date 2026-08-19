# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Status

`PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / NO MATURITY CLAIM / POST-SADDLE STATE RECONCILED`

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

PR #7 został zweryfikowany i scalony. Jego merge commit jest aktualnym historycznym checkpointem Phase 6: `daa6e5dc210e09171a530eeffe5601e0e74ae041`.

## Downstream Saddle context — accepted external fact

Historyczny następny gate `SADDLE LIVE MODEL EVIDENCE NEXT` został później zamknięty w repo Saddle. `FUNCTIONAL_SADDLE_ACCEPTED` jest zaakceptowanym faktem Saddle i **nie** podnosi automatycznie maturity ScriptOps.

ScriptOps nadal ma tylko własny udowodniony zakres Phase 6 i `MATURITY CLAIM: NONE`.

## Zakaz rozbudowy

Nie dodawać browser helpera, direct model/API automation, autonomous approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph ani multi-user.

## Co dalej

Nie wracać do merge PR #7 ani do historycznego Saddle live-worker gate.

Najbliższa praca ekosystemowa może użyć **istniejącego** mechanizmu Phase 6 w jednym materially-different bounded workload. To jest working evaluation, nie aktywacja nowego produktu ani zgoda na nowe capability. Dokładny workload i jego evidence contract muszą pozostać w granicach istniejących możliwości i Human approval.

`MATURITY CLAIM`: **NONE**.
