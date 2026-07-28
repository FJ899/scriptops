# CODEX_START — ScriptOps RC1

## Tryb

`PLAN FIRST / NO IMPLEMENTATION WITHOUT APPROVAL`

## Pliki obowiązkowe przed pracą

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `sources/Decision_Summary_Current_State.md`
6. `sources/ScriptOps_Main_Theme_Summary.md`
7. `sources/RC1_SCOPE_LOCK.md`

## Pierwsza odpowiedź Codex

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

## Zakres implementacyjny

Buduj wyłącznie pętlę:

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

## Zakaz implementacji

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

Każdy taki element oznacz: `POST-MVP candidate, not RC1`.

## Kryterium ukończenia etapu planowania

Etap planowania kończy się dopiero, gdy przedstawiony plan umożliwia późniejsze sprawdzenie:

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
