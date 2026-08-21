---
project: "Narzędzie pisarskie / ScriptOps"
canonical_name: "ScriptOps"
cos_status: "QUEUED #1"
status: "PHASE 6 CONTROLLED WORKFLOW MECHANISM PASS / BOUNDED PROPOSAL VIEW INTEGRATED / P3 RUN003 OBSERVED PASS / SCN-012+027 HUMAN SEMANTIC ACCEPTED / CANONICAL EFFECT PREPARED NOT APPLIED / GOAL DONE NO / NO MATURITY CLAIM"
reconstructed_at: "2026-07-27"
updated_at: "2026-08-21"
state_owner: "PROJECT_STATE.md"
---

# PROJECT_STATE — Narzędzie pisarskie / ScriptOps

## 1. Aktualny rezultat

Najmniejsza pętla ScriptOps oparta na istniejącym v2 została technicznie udowodniona jako kontrolowany mechanizm:

```text
task
→ context bundle
→ candidate import
→ validation
→ impact report
→ human decision with why
→ accepted identity
→ decision log
→ Git commit
```

To jest `CONTROLLED WORKFLOW MECHANISM PASS`, nie maturity claim i nie pełny ScriptOps v5 RC1.

PR #7 został zweryfikowany i scalony. Jego merge `daa6e5dc210e09171a530eeffe5601e0e74ae041` pozostaje historycznym checkpointem przyjętego Phase-6 proof, a nie wiecznym wskaźnikiem bieżącego `main`.

Późniejszy bounded security/correctness maintenance PR #10 został osobno technicznie zweryfikowany, Human-accepted i Human-authorized do merge. Wszedł do `main` jako `dae2eb084e9dea51d576a55334cc3dc1dc21bc02`, zamykając błąd leksykograficznego wyboru staged candidate (`v10` vs `v9`) oraz odrzucając symlink candidates. Nie zmienia to maturity claim ani celu projektu.

Po realnych workloadach P3 ujawniono konkretny blocker: downstream context dla SCN-027 czytał stary canonical SCN-012 zamiast jawnie wybranego staged proposal. Human zaakceptował kierunek minimalnego `bounded proposal view`, bez atomic approval. PR #14 został technicznie zweryfikowany, Human-accepted i Human-authorized do merge; integracyjny checkpoint to `817c57a313cbf195cf9ed60e88b36a2f09fa4fab`.

Real Workload 003 wykorzystał ten mechanizm end-to-end dla SCN-012 → SCN-027 i ustanowił:

```text
BOUNDED_UPSTREAM_CONTEXT: PASS
DOWNSTREAM_CANDIDATE: STAGED
CROSS_SCENE_PROPOSAL_COHERENCE: OBSERVED PASS
CANONICAL_EFFECT: NOT APPLIED
HUMAN_APPROVAL: NOT REQUESTED
GOAL_DONE: NO
```

Human zaakceptował evidence Run 003, a następnie osobno autoryzował merge PR #16. Integracyjny checkpoint Run 003 to `43ab980d4e0af33bc9a628f3d8b70617a14fb9db`.

2026-08-21 Human następnie jawnie ustalił, że `SCN-012 → SCN-027` wyczerpuje zamierzony zakres tej decyzji, przeprowadził semantic review i zaakceptował proposal state obu scen. `NO-CARRIER GOAL` dla tego ograniczonego zakresu jest `SEMANTICALLY SATISFIED`; zaakceptowana została zamiana fizycznej kontroli nośnika na kontrolę dostępu do zaszyfrowanego źródła, a utrata fizycznego beatu pendrive/szuflada nie jest blockerem. Human autoryzował wyłącznie przygotowanie canonical effect; jego wykonanie wymaga osobnego Human gate. Szczegóły: `DEC-SO-011` oraz `evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`.

Bieżący live `main` należy rozwiązać z GitHub przy odczycie, jeśli jest potrzebny do consequential work; zapisane tutaj SHA są historycznymi lub last-observed integration checkpoints, nie remote lockiem ani wiecznym twierdzeniem `CURRENT LIVE`.

## 2. Definicja projektu

ScriptOps jest lokalnym systemem kontroli prawdy, decyzji i zmian dla projektów narracyjnych oraz innych projektów intensywnie wykorzystujących idee i AI.

AI tworzy kandydatów. ScriptOps przygotowuje kontekst, kontroluje strukturę i raportuje wpływ. Człowiek zatwierdza albo odrzuca zmianę. Dopiero zmiana zwalidowana, zatwierdzona z uzasadnieniem i utrwalona w Git staje się prawdą projektu.

## 3. Historia projektu

1. Workflow B3 → B2 → RR prowadził rzeczywistą produkcję „Przygód Liścionka”.
2. Mądry Warsztat / S2 Studio uporządkował role, stan, recenzję i przekazywanie artefaktów.
3. ScriptOps v2 przeniósł część mechanizmów do lokalnego CLI.
4. ScriptOps WebAI v5 rozszerzył specyfikację do systemu kontroli prawdy.
5. Final Master Package zamknął zakres MVP RC1.
6. GitHub-side access check nie znalazł późniejszego RC1 builda; analiza v2 wskazała B1–B5.
7. 2026-08-10 człowiek wybrał v2 jako bazę Saddle Phase 6: reuse + hardening + proof, bez rewrite i nowych capability w zamrożonym scope Phase 6.
8. PR #7 udowodnił bounded workflow smoke oraz repository continuity verification i został scalony do `main`.
9. Późniejsza zaakceptowana historia Saddle zamknęła historyczny gate `SADDLE LIVE MODEL EVIDENCE NEXT`; nie zmienia to lokalnego maturity claim ScriptOps.
10. Real pilot ujawnił błąd wyboru staged candidate po nazwie; PR #10 dodał numeric-version selection, symlink rejection i dedykowane regresje.
11. PR #11 uporządkował semantics lokalnych SHA: checkpoint/provenance zamiast perpetual live pointer.
12. P3 Run 001 i Run 002 udowodniły odpowiednio brak downstream coverage oraz konkretny blocker `DOWNSTREAM_CONTEXT_SOURCE=OLD_CANONICAL / CROSS_SCENE_CANDIDATE_COHERENCE=BLOCKED`.
13. W trakcie pracy nad rozwiązaniem wykryto P0 collision path w review task identity; PR #15 zamknął go przed wznowieniem feature work.
14. Human zaakceptował minimalny bounded proposal view bez atomic approval; PR #14 został scalony, a P3 Run 003 następnie ustanowił `CROSS_SCENE_PROPOSAL_COHERENCE=OBSERVED_PASS` bez canonical effect.
15. Human ograniczył semantic-decision scope do `SCN-012 → SCN-027`, zaakceptował proposal state obu scen oraz autoryzował przygotowanie, ale nie wykonanie canonical effect (`DEC-SO-011`).

## 4. Aktualne decyzje użytkownika

Obowiązują `DEC-SO-001`…`DEC-SO-011`, w szczególności dla zamrożonego baseline Phase 6:

- człowiek pozostaje właścicielem kanonu i decyzji;
- AI tworzy kandydatów, nie zatwierdza kanonu;
- `legacy/scriptops-v2-single.py` jest bazą Phase 6;
- `REWRITE: NO` dla bazowej implementacji Phase 6;
- `NEW CAPABILITY: NO` dla zamrożonego bazowego scope Phase 6;
- Phase 6 = `reuse + hardening + proof`;
- `MATURITY CLAIM: NONE`.

Późniejsza jawna Human decision z 2026-08-19 autoryzowała dokładnie jeden wąski kierunek ponad ten historyczny baseline:

```text
MINIMALNY BOUNDED PROPOSAL VIEW DLA CROSS-SCENE COHERENCE
BEZ ATOMIC APPROVAL
```

Ta decyzja została zmaterializowana w Human-accepted i Human-authorized PR #14. Nie jest ogólną zgodą na nowe capability. Nie autoryzuje atomic multi-scene approval, globalnego `staging wins`, automatycznego wyboru kandydatów, model/API integration, GUI, agent framework ani dalszego rozszerzania produktu.

DEC-SO-011 z 2026-08-21 ustanawia Human semantic acceptance proposal state `SCN-012 + SCN-027` i autoryzuje wyłącznie przygotowanie exact canonical effect. Canonical write, `approve --why` i jakikolwiek consequential effect pozostają nieautoryzowane do osobnego Human gate.

Późniejsze `FUNCTIONAL_SADDLE_ACCEPTED` jest zaakceptowanym faktem repo Saddle, nie lokalną decyzją ScriptOps i nie promocją ScriptOps do wyższego maturity.

## 5. Zamknięty zakres B1–B5

1. **B1 lifecycle / dirty tree:** task jest trwałym Git checkpointem przed preflight.
2. **B2 artefakty przed approval:** preflight/context/candidate input/impact są jawnie checkpointowane; unrelated dirty state blokuje.
3. **B3 accepted hash:** accepted scene hash jest liczony po zmianie statusu.
4. **B4 human why:** `approve --why` jest obowiązkowe i trafia do decision logu.
5. **B5 impact + smoke:** `impact-report.json` istnieje przed human decision; pełna ścieżka jest testowana w świeżym tymczasowym repo Git.

Evidence: `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`.

## 6. Model odpowiedzialności w tym slice

```text
candidate artifact = proposal, not canon
impact report = review evidence, not authority
bounded proposal binding = task-local proposal context, not canon
human approve --why = semantic decision
canonical scene write = consequence after human decision
decision log + Git = durable evidence
```

ScriptOps nie dostaje własnej interpretacji intencji, własnej effect authority ani autonomicznego planowania celu.

## 7. Implementacja Phase 6 i bounded proposal view

Historyczny `legacy/scriptops-v2-single.py` pozostaje niezmienionym źródłem bazowym i dowodem v2.

`phase6/scriptops-v2-hardening.py` ładuje go jako execution substrate i dodaje audytowalne checkpointy B1–B5 oraz późniejsze bounded correctness/security maintenance.

PR #10 zmienia istniejącą funkcję wyboru staged candidate: wersja jest parsowana numerycznie, najwyższy integer wygrywa, a symlink/malformed candidate nie jest kwalifikowany.

PR #15 hardenuje review task identity tak, aby dwa natychmiastowe review nie mogły współdzielić katalogu task evidence ani nadpisać istniejącego tasku.

`phase6/bounded-proposal-view.py` dodany przez PR #14 jest jawnie opt-in i task-bounded:

- `bind` wiąże dokładny staged candidate przez repository-relative path + SHA-256;
- kandydat musi mieć matching `REVIEW_REQUIRED` impact report;
- binding musi dotyczyć graph-adjacent sceny;
- bounded context używa tylko jawnie przypiętych proposal artifacts;
- unbound scenes zachowują canonical-first resolution;
- context pack oznacza view jako `BOUNDED_NONCANONICAL / PROPOSAL_NOT_CANON`;
- drift candidate identity blokuje operację;
- mechanizm nie dodaje atomic approval ani canonical write.

Proof/evidence:
- `tests/test_phase6_scriptops_smoke.py`;
- `tests/test_phase6_candidate_selection.py`;
- `tests/test_phase6_review_task_identity.py`;
- `tests/test_phase6_bounded_proposal_view.py`;
- `tests/test_phase6_p3_real_workload_001.py`;
- `tests/test_phase6_p3_real_workload_002.py`;
- `tests/test_phase6_p3_real_workload_003.py`;
- `tests/test_phase6_p3_evidence_record_003.py`;
- `.github/workflows/phase6-scriptops-smoke.yml`;
- `scripts/verify_repository.py`;
- `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`;
- `evidence/P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md`.

## 8. Zweryfikowane i scalone checkpointy

### Phase-6 proof — PR #7

- accepted implementation head: `acbfca79f96407dbd46f9806bf821caf6e02e1af`;
- merge/historyczny Phase-6 checkpoint: `daa6e5dc210e09171a530eeffe5601e0e74ae041`.

### Candidate-selection maintenance — PR #10

- Human-accepted exact head: `410b2d7b9b75988eb3343e2f4a99dade0f2608d2`;
- merge checkpoint: `dae2eb084e9dea51d576a55334cc3dc1dc21bc02`;
- old pilot PR #8: `CLOSED / UNMERGED / SUPERSEDED / SUPPORTING PROVENANCE`.

### Snapshot semantics — PR #11

- accepted/merged;
- zapisane SHA są checkpointami provenance, a live `main` ma być resolve'owany przy consequential use.

### P3 Real Workload 001 — PR #12

- `MECHANISM_CONTROL: PASS`;
- `LOCAL REWRITE CANDIDATE: OBSERVED PASS`;
- `DOWNSTREAM DEPENDENCY COVERAGE: INSUFFICIENT EVIDENCE`;
- `CANONICAL EFFECT: NOT APPLIED`;
- `GOAL DONE: NO`.

### P3 Real Workload 002 — PR #13

- `DEPENDENCY_PRESENT: YES`;
- `UPSTREAM_CANDIDATE: STAGED`;
- `DOWNSTREAM_CONTEXT_SOURCE: OLD_CANONICAL`;
- `CROSS_SCENE_CANDIDATE_COHERENCE: BLOCKED`;
- `CANONICAL EFFECT: NOT APPLIED`;
- `GOAL DONE: NO`.

### Review task identity P0 — PR #15

- exact accepted head: `ee018d18f70450200508a430a1769be3c858c77a`;
- merge checkpoint: `06a2ffa3f0ce436e10eee4448a586fbfbaba9ac8`;
- two immediate reviews receive distinct task directories;
- existing task evidence overwrite is prevented.

### Bounded proposal view — PR #14

- exact accepted head: `248f51f0e9a914295262b0e97395d9971ddcebee`;
- merge checkpoint: `817c57a313cbf195cf9ed60e88b36a2f09fa4fab`;
- explicit binding PASS;
- downstream context can consume the exact bound staged upstream proposal;
- unbound global precedence remains `NO`;
- canonical effect remains `NOT APPLIED`;
- atomic approval remains `NOT ADDED`.

### P3 Real Workload 003 — PR #16

- exact accepted evidence head: `1bd3c6d0406d1d23aa2b9c4d401f3e5d6ca15a82`;
- merge/integration checkpoint: `43ab980d4e0af33bc9a628f3d8b70617a14fb9db`;
- `BOUNDED_UPSTREAM_CONTEXT: PASS`;
- `DOWNSTREAM_CANDIDATE: STAGED`;
- `CROSS_SCENE_PROPOSAL_COHERENCE: OBSERVED PASS`;
- `CANONICAL_EFFECT: NOT APPLIED`;
- `HUMAN APPROVAL: NOT REQUESTED`;
- `GOAL DONE: NO`.

Human acceptance Run 003 dotyczy observed evidence. Późniejsza DEC-SO-011 ustanawia Human semantic acceptance rewrite'ów SCN-012/SCN-027, ale nadal nie stanowi canonical effect.

## 9. Czego nadal nie wolno twierdzić

- brak ScriptOps v5/RC1 maturity claim;
- brak niezależnego zewnętrznego user testu ScriptOps;
- brak produkcyjnego narrative-value claim;
- brak ScriptOps AI-model-quality claim;
- brak production identity/request-origin provider jako capability ScriptOps;
- whole-project dependency completeness poza dostarczonym łańcuchem SCN-012 → SCN-027 nie jest ustanowiona ani wymagana przez tę ograniczoną Human decision;
- Human semantic acceptance proposal state SCN-012/SCN-027 jest ustanowiona przez DEC-SO-011;
- brak canonical effect dla tych rewrite'ów;
- brak atomic multi-scene approval capability;
- `GOAL DONE` dla Human-owned no-carrier goal pozostaje `NO` do czasu realnego canonical effect.

Nie wolno przedstawiać PR #7, numeric candidate-selection P0, review-task-id P0, bounded proposal view implementation ani Run 003 cross-scene proposal blocker jako otwartych lokalnych blockerów — są zamkniętymi, zintegrowanymi checkpointami. Otwarty jest wyłącznie osobny Human gate dla przygotowanego canonical effect na prawdziwym target canon.

## 10. Zakaz rozbudowy pozostaje aktywny

Nie dodawać browser helpera, model/API automation, autonomous approval, atomic multi-scene approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph, multi-user ani innych capability bez nowej jawnej decyzji.

Zaakceptowany bounded proposal view jest wąskim wyjątkiem już zintegrowanym; nie otwiera ogólnego product roadmap ani kolejnych capability.

## 11. Jeden następny krok

Stan bieżący:

```text
CANONICAL_EFFECT_PREPARED / WAITING_FOR_SEPARATE_HUMAN_EFFECT_GATE
```

Human semantic decision dla `SCN-012 + SCN-027` jest zamknięta. Nie szukać dalszego downstream material dla tej decyzji.

Prepared effect jest zapisany w:

`evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`.

Repo `JTJ07/scriptops` jest repo narzędzia; workload scen był materializowany w tymczasowym projekcie ewaluacyjnym. Przed realnym canonical effect trzeba wskazać dokładny target project/canon, potwierdzić accepted source identities i candidate identities oraz przedstawić exact `why`. Dopiero osobny Human gate może autoryzować `approve --why` / canonical write.

Bez tego gate'u ScriptOps nie wykonuje canonical effect i nie deklaruje `GOAL DONE`.

## 12. Źródła szczegółowe

- `sources/Decision_Summary_Current_State.md`;
- `sources/ScriptOps_Main_Theme_Summary.md`;
- `sources/RC1_SCOPE_LOCK.md`;
- `legacy/scriptops-v2-single.py`;
- `analysis/RC1_V2_GAP_2026-08-10.md`;
- `DECISION_LOG.md` — DEC-SO-011 i wcześniejsze baseline decisions;
- `phase6/scriptops-v2-hardening.py`;
- `phase6/bounded-proposal-view.py`;
- `tests/test_phase6_scriptops_smoke.py`;
- `tests/test_phase6_candidate_selection.py`;
- `tests/test_phase6_review_task_identity.py`;
- `tests/test_phase6_bounded_proposal_view.py`;
- `tests/test_phase6_p3_real_workload_001.py`;
- `tests/test_phase6_p3_real_workload_002.py`;
- `tests/test_phase6_p3_real_workload_003.py`;
- `tests/test_phase6_p3_evidence_record_003.py`;
- `evidence/PHASE6_CONTROLLED_WORKFLOW_PROOF_2026-08-10.md`;
- `evidence/P3_REAL_WORKLOAD_003_SCENE12_27_2026-08-19.md`;
- `evidence/P3_SCENE12_27_HUMAN_SEMANTIC_ACCEPTANCE_AND_CANONICAL_EFFECT_PREVIEW_2026-08-21.md`;
- PR #14 Human acceptance + merge history;
- PR #16 Human evidence acceptance + merge history;
- accepted downstream context in `JTJ07/Saddle` is supporting provenance, not local state authority.
