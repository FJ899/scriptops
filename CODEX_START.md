---
document: "ScriptOps historical RC1 Codex bootstrap"
status: "HISTORICAL / SUPERSEDED RC1 PLANNING BOOTSTRAP / NOT CURRENT ROUTE"
reconciled_at: "2026-08-24"
current_recovery_entry: "README.md -> PROJECT_STATE.md -> HANDOFF.md"
---

# CODEX_START — ScriptOps RC1

## CURRENT RECOVERY NOTICE

This file preserves the historical RC1 planning bootstrap. It is **not** a current implementation instruction.

Current ScriptOps state is:

```text
CANONICAL_EFFECT_PREPARED / WAITING_FOR_SEPARATE_HUMAN_EFFECT_GATE
```

A zero-history session must recover current state from `README.md`, `PROJECT_STATE.md` and `HANDOFF.md`. No RC1 implementation, rewrite, new capability or new product phase is authorized by this file. The Human semantic decision for `SCN-012 + SCN-027` is already closed; this notice does not authorize the prepared canonical effect.

The historical body below remains provenance for the earlier RC1 planning model.

---

## Tryb — HISTORICAL

`PLAN FIRST / NO IMPLEMENTATION WITHOUT APPROVAL`

## Pliki obowiązkowe przed historyczną pracą RC1

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `sources/Decision_Summary_Current_State.md`
6. `sources/ScriptOps_Main_Theme_Summary.md`
7. `sources/RC1_SCOPE_LOCK.md`

## Pierwsza odpowiedź Codex — HISTORICAL

Nie implementuj jeszcze.

Przedstaw:

1. proponowane drzewo repozytorium;
2. planowane moduły Python;
3. tabele SQLite;
4. mapę komend CLI;
5. pliki czytane i zapisywane przez każdą komendę;
6. plan testów akceptacyjnych;
7. przepływ smoke testu;
8. sprzeczności i miejsca niedookreślone;
9. listę funkcji post-MVP, których nie zaimplementujesz.

## Kontrakt prawdy

- wypowiedź użytkownika może być hipotezą;
- wynik AI i Codex jest kandydatem;
- źródłem prawdy jest lokalny projekt;
- zmiana staje się prawdą dopiero po walidacji, analizie wpływu, jawnej decyzji człowieka, zapisie uzasadnienia i commicie Git;
- przy sprzeczności wybierz węższy zakres RC1 i zgłoś problem.

## Zakres implementacyjny — HISTORICAL / DO NOT EXECUTE AS CURRENT

Historyczny bootstrap instruował budowę wyłącznie pętli:

```text
project init
→ task
→ context bundle
→ WebAI candidate import
→ validation
→ impact report
→ human decision
→ decision log
→ Git commit
→ smoke test
```

Ta instrukcja nie jest current route po zintegrowanym Phase 6 / bounded proposal view / Real Workloads 001–003.

## Zakaz implementacji historycznego RC1

Nie dodawaj:

- browser helpera;
- wywołań API modeli;
- autonomicznego agenta;
- automatycznego approve;
- automatycznej zmiany kanonu;
- multi-user;
- dashboardu ani GUI/TUI;
- vector database;
- automatycznego grafu semantycznego;
- AI Guard;
- Rule Miner;
- Retcon Engine;
- eksportu;
- voice interface;
- cloud sync.

Każdy taki element był oznaczany: `POST-MVP candidate, not RC1`.

## Kryterium ukończenia etapu planowania — HISTORICAL

Historyczny etap planowania kończył się dopiero, gdy przedstawiony plan umożliwiał późniejsze sprawdzenie:

- `scriptops --help`;
- inicjalizacji projektu;
- tworzenia zadania;
- budowania kontekstu i HANDSHAKE v2;
- importu kandydata;
- walidacji strukturalnej;
- raportu wpływu;
- approve/reject/revision z obowiązkowym `why`;
- commita tylko po approve;
- wykrycia dirty state;
- testów pytest i pełnego smoke testu.
