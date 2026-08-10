---
project: "ScriptOps"
portfolio_status: "QUEUED #1"
activation: "BOUNDED PHASE 6 PROOF ONLY"
state_owner: "PROJECT_STATE.md"
blocker: "PHASE 6 PROOF MUST PASS ALL CHECKS"
next_step: "finish_phase6_smoke_and_continuity_evidence"
resume_contract: "REUSE V2 / NO REWRITE / NO NEW CAPABILITY"
---

# HANDOFF — ScriptOps

## Stan wejściowy

- Projekt: `Narzędzie pisarskie / ScriptOps`
- Ogólna aktywacja produktu: `NO`
- Dozwolona aktywność: `BOUNDED PHASE 6 PROOF ONLY`
- Baza: `legacy/scriptops-v2-single.py`
- Rewrite: `NO`
- New capability: `NO`
- Maturity claim: `NONE`
- Lokalne źródło prawdy: `PROJECT_STATE.md`

Nagłówek YAML jest maszynowym skrótem tego samego handoffu. W przypadku sprzeczności obowiązuje `PROJECT_STATE.md` i najnowsza jawna decyzja człowieka.

## Decyzja, która odblokowała pracę

`DEC-SO-010`: człowiek wybrał `legacy/scriptops-v2-single.py` jako bazę Saddle Phase 6.

Phase 6 ma tylko zamknąć B1–B5:

1. clean-tree lifecycle taska;
2. clean-tree lifecycle generated evidence/candidate input;
3. świeży accepted hash;
4. obowiązkowe `approve --why`;
5. impact report + smoke proof.

## Co jest implementowane

- historyczny plik v2 pozostaje niezmieniony;
- `phase6/scriptops-v2-hardening.py` ładuje v2 jako execution substrate;
- kandydat jest proposal artifact, nie kanonem;
- impact report powstaje przed decyzją człowieka;
- canonical scene write następuje dopiero po `approve --why`;
- accepted scene hash jest liczony po przejściu do `accepted`;
- task/preflight/context/candidate-input/impact są utrwalane jako jawne Git checkpoints;
- deterministyczny test tworzy tymczasowy Git project i przechodzi pełną ścieżkę.

## Zakaz dryfu

Nie dodawać browser helpera, model/API automation, autonomous approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph, multi-user ani innych funkcji post-MVP.

ScriptOps nie może przejąć roli Saddle ani Executora: nie interpretuje celu, nie tworzy własnej authority i nie zatwierdza sam kanonu.

## Aktualny dowód

PR Phase 6 uruchamia:

- `Phase 6 ScriptOps smoke`;
- istniejący `Verify repository state`.

Pierwszy smoke na początkowym head PR #7 przeszedł. Stary continuity verifier ujawnił własny drift statusów z czasu sprzed zakończenia access checka; jest aktualizowany tak, aby testował obecny kanoniczny stan zamiast historycznej blokady.

Nie ogłaszać Phase 6 DONE, dopóki finalny head nie ma zielonych obu checków.

## Jeden następny krok

Doprowadzić finalny head PR Phase 6 do dwóch zielonych checków, zapisać evidence, scalić bounded hardening i przekazać wynik do Saddle.

## Pliki do otwarcia przez nową sesję

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md` — DEC-SO-010
5. `analysis/RC1_V2_GAP_2026-08-10.md`
6. `legacy/scriptops-v2-single.py`
7. `phase6/scriptops-v2-hardening.py`
8. `tests/test_phase6_scriptops_smoke.py`
9. `scripts/verify_repository.py`
