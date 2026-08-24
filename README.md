# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Status

`PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / BOUNDED PROPOSAL VIEW INTEGRATED / P3 RUN003 OBSERVED PASS / SCN-012+027 HUMAN SEMANTIC ACCEPTED / CANONICAL EFFECT PREPARED NOT APPLIED / GOAL DONE NO / NO MATURITY CLAIM`

Current work-state:

```text
CANONICAL_EFFECT_PREPARED / WAITING_FOR_SEPARATE_HUMAN_EFFECT_GATE
```

Jawna decyzja użytkownika: `legacy/scriptops-v2-single.py` jest bazą historycznego Phase 6. `REWRITE: NO`. `NEW CAPABILITY: NO` dla tego zamrożonego baseline.

## Uruchomienie nowej sesji

Nowe AI ma przeczytać w tej kolejności:

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`
6. `evidence/P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md`
7. `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`
8. `IDEA_ARCHIVE.md`
9. `SOURCE_MANIFEST.md`
10. `RECONSTRUCTION_REPORT.md`

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

2026-08-21 Human jawnie ograniczył zamierzony zakres decyzji do `SCN-012 → SCN-027`, zaakceptował proposal state obu scen i uznał bounded no-carrier goal za semantycznie spełniony. Autoryzowane zostało wyłącznie przygotowanie exact canonical effect; wykonanie pozostaje za osobnym Human effect gate (`DEC-SO-011`).

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

Human semantic decision dla `SCN-012 + SCN-027` również jest zamknięta. Current state:

```text
CANONICAL_EFFECT_PREPARED / WAITING_FOR_SEPARATE_HUMAN_EFFECT_GATE
```

Nie szukać dalszego downstream material dla tej decyzji i nie wracać do semantic review SCN-012/027.

Przed jakimkolwiek canonical effect trzeba przedstawić Human exact target project/canonical scene identities, exact accepted source/candidate identities zgodne z `DEC-SO-011`, exact `why` oraz potwierdzenie braku unrelated canonical changes. Dopiero osobny Human gate może autoryzować `approve --why` / canonical write.

`MATURITY CLAIM`: **NONE**.
