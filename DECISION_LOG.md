# DECISION_LOG

## DEC-SO-001 — człowiek pozostaje właścicielem kanonu

Status: `ACTIVE`

AI tworzy kandydatów i analizy. Nie zatwierdza, nie commituję i nie zmienia samodzielnie kanonu.

## DEC-SO-002 — lokalne źródło prawdy

Status: `ACTIVE`

Szczegółowy stan ScriptOps należy do prywatnego repo `litrgratis-pixel/scriptops`. `PROJECT_STATE.md` jest kanonicznym stanem operacyjnym.

## DEC-SO-003 — zakres RC1

Status: `ACTIVE`

RC1 ma udowodnić tylko pętlę:

`task → context → candidate import → validation → impact → human decision → decision log → Git commit`.

## DEC-SO-004 — wyłączenia z RC1

Status: `ACTIVE`

Poza RC1 pozostają: browser helper, API, autonomiczny agent, AI Guard, automatyczny graf semantyczny, pełny IdeaOps, dashboard, eksport i multi-user.

## DEC-SO-005 — specyfikacja nie jest produktem

Status: `ACTIVE`

`ScriptOps_FINAL_MASTER_PACKAGE` i v5 są źródłami zakresu i architektury, ale nie dowodem wykonania RC1.

## DEC-SO-006 — prototyp v2 nie jest automatycznie bazą RC1

Status: `ACTIVE`

Decyzja o bazie implementacji wymaga porównania `scriptops-v2-single.py` z `RC1_SCOPE_LOCK.md`.

## DEC-SO-007 — kolejność pracy

Status: `ACTIVE`

1. zabezpieczenie stanu i źródeł;
2. `ACCESS CHECK`;
3. porównanie v2 z RC1, jeżeli nie ma późniejszego kodu;
4. decyzja o bazie implementacji;
5. dopiero potem test end-to-end.

## DEC-SO-008 — projekt nie jest jeszcze aktywowany

Status: `ACTIVE`

ScriptOps pozostaje `QUEUED #1 / NOT ACTIVATED`. Rekonstrukcja i zabezpieczenie repo nie oznaczają rozpoczęcia implementacji.
