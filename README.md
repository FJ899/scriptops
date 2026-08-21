# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Status

`PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / BOUNDED PROPOSAL VIEW INTEGRATED / P3 RUN003 OBSERVED PASS / GOAL DONE NO / NO MATURITY CLAIM`

Current work-state:

```text
WAITING_FOR_EVIDENCE / HUMAN_SEMANTIC_DECISION
```

Jawna decyzja użytkownika: `legacy/scriptops-v2-single.py` jest bazą historycznego Phase 6. `REWRITE: NO`. `NEW CAPABILITY: NO` dla tego zamrożonego baseline.

## Uruchomienie nowej sesji

Nowe AI ma przeczytać w tej kolejności:

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `evidence/P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md`
6. `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`
7. `IDEA_ARCHIVE.md`
8. `SOURCE_MANIFEST.md`
9. `RECONSTRUCTION_REPORT.md`

`CODEX_START.md` oraz `analysis/RC1_V2_GAP_2026-08-10.md` pozostają historycznym RC1/planning provenance. **Nie są current implementation route.**

## Zasady nadrzędne

- odpowiedź AI jest kandydatem, nie prawdą projektu;
- zmiana kanonu wymaga walidacji, decyzji człowieka, uzasadnienia i zapisu w Git;
- candidate artifact nie jest kanonicznym efektem;
- kanoniczny zapis Phase 6 następuje dopiero po `approve --why`;
- smoke proof nie jest maturity claim;
- nie wolno rozszerzać zakresu o nowe capability bez nowej jawnej Human decision;
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

Późniejszy `bounded proposal view` został zintegrowany i Real Workload 003 ustanowił bounded cross-scene proposal coherence bez canonical effect.

## Testy

```bash
python -m unittest discover -s tests -p 'test_phase6_*.py' -v
python scripts/verify_repository.py
```

PR #7 został zweryfikowany i scalony. Jego merge commit pozostaje historycznym checkpointem Phase 6: `daa6e5dc210e09171a530eeffe5601e0e74ae041`.

Późniejsze integrated checkpoints są opisane w `PROJECT_STATE.md`; zapisane SHA są provenance/checkpoints, nie perpetual live locks.

## Downstream Saddle context — accepted external fact

Historyczny następny gate `SADDLE LIVE MODEL EVIDENCE NEXT` został później zamknięty w repo Saddle. `FUNCTIONAL_SADDLE_ACCEPTED` jest zaakceptowanym faktem Saddle i **nie** podnosi automatycznie maturity ScriptOps.

ScriptOps nadal ma tylko własny udowodniony zakres i `MATURITY CLAIM: NONE`.

## Zakaz rozbudowy

Nie dodawać browser helpera, direct model/API automation, autonomous approval, atomic multi-scene approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph ani multi-user bez osobnej Human authority.

## Co dalej

Historyczny `materially-different bounded workload` został wykonany przez Real Workloads 001–003. **Nie jest już current NEXT.**

Current state pozostaje:

```text
WAITING_FOR_EVIDENCE / HUMAN_SEMANTIC_DECISION
```

Aby kontynuować Human-owned cel usunięcia pendrive'a, potrzebny jest jeden authoritative next input od Human:

- dodatkowy autorytatywny materiał downstream, jeżeli istnieją dalsze zależności wymagające coverage; **albo**
- jawna semantic decision dotycząca proposal state SCN-012 + SCN-027, jeżeli dostarczony materiał wyczerpuje zamierzony zakres decyzji.

ScriptOps nie wybiera między tymi ścieżkami i bez takiego inputu nie wykonuje canonical approval ani nie deklaruje `GOAL DONE`.

`MATURITY CLAIM`: **NONE**.
