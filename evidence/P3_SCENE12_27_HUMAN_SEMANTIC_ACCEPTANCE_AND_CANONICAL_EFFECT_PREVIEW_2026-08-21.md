# P3 SCN-012 → SCN-027 — HUMAN SEMANTIC ACCEPTANCE + CANONICAL EFFECT PREVIEW

Date: 2026-08-21
Status: `HUMAN SEMANTIC ACCEPTED / CANONICAL EFFECT PREPARED / NOT APPLIED`
Authority: `EXPLICIT HUMAN DECISION`
Scope: `SCN-012 → SCN-027 ONLY`

## 1. Human decision

Human explicitly decided:

```text
SCN-012 → SCN-027 WYCZERPUJE ZAMIERZONY ZAKRES TEJ DECYZJI.
PRZECHODZIMY DO HUMAN SEMANTIC REVIEW.
```

After semantic review Human explicitly accepted:

```text
AKCEPTUJĘ SEMANTYCZNIE PROPOSAL STATE
SCN-012 + SCN-027.

NO-CARRIER GOAL DLA USTALONEGO ZAKRESU:
SATISFIED.

AKCEPTUJĘ ZAMIANĘ:
FIZYCZNA KONTROLA NOŚNIKA
→
KONTROLA DOSTĘPU DO ZASZYFROWANEGO ŹRÓDŁA.

UTRATA FIZYCZNEGO BEATU Z PENDRIVEM / SZUFLADĄ
NIE JEST BLOCKEREM TEJ ZMIANY.

AUTORYZUJĘ PRZEJŚCIE DO PRZYGOTOWANIA
CANONICAL EFFECT,
ALE NIE DO JEGO WYKONANIA BEZ OSOBNEGO HUMAN GATE.
```

## 2. What is now established

For the explicitly bounded material `SCN-012 → SCN-027`:

- Human semantic acceptance of the proposal state: `YES`;
- no-carrier goal at the semantic/proposal level: `SATISFIED`;
- physical pendrive semantics may be replaced by encrypted-source/access-control semantics: `ACCEPTED`;
- loss of the physical pendrive/drawer beat: `NOT A BLOCKER`;
- further downstream material for this decision: `NOT REQUIRED BY HUMAN`;
- canonical effect: `NOT APPLIED`;
- `approve --why`: `NOT EXECUTED`;
- `GOAL DONE`: `NO` until the accepted effect is actually applied to a canonical target.

This does not create ScriptOps maturity, a new capability, atomic multi-scene approval, product activation, model/API integration or autonomous effect authority.

## 3. Exact accepted proposal content — SCN-012

Source provenance: `tests/test_phase6_p3_real_workload_002.py` and Run 003 bounded proposal evidence.

```text
INT. BIURO - DZIEŃ

Adam wchodzi do niewielkiego biura. Anna siedzi przy biurku i przegląda dokumenty.

ANNA
Masz dostęp?

ADAM
Wysłałem ci jednorazowy link. Wszystko tam jest. Nagrania, umowy, zdjęcia.

Anna otwiera wiadomość na laptopie. Uruchamia zaszyfrowany transfer.

ANNA
Jeśli to trafi do prokuratury, Kowalski jest skończony.

Na ekranie pojawia się folder „ARCHIWUM”.

Anna kopiuje jego zawartość na komputer.

ANNA
Zrobię kopię roboczą. Źródłowy pakiet zostaje w zaszyfrowanym magazynie. Tej wersji nie ruszamy.

Transfer kończy się. Adam wychodzi.
```

Semantic mapping accepted by Human:

```text
pendrive
→ one-time access link / encrypted transfer

Anna copy
→ local working copy

physical original
→ authoritative source package in encrypted remote storage
```

## 4. Exact accepted proposal content — SCN-027

Source provenance: `tests/test_phase6_p3_real_workload_003.py` and Run 003 bounded proposal evidence.

```text
INT. MIESZKANIE ADAMA - NOC

Adam zamyka drzwi na dwa zamki i podchodzi do biurka.

Telefon wibruje.

ANNA
Masz jeszcze dostęp do źródła?

ADAM
Mam.

ANNA
Kopia z mojego laptopa zniknęła. Ktoś ją usunął.

Adam nie loguje się do magazynu. Odkłada telefon ekranem w dół.

ADAM
Czyli został tylko źródłowy pakiet w zaszyfrowanym magazynie, do którego mam dostęp.

Po drugiej stronie zapada cisza.

ANNA
Nie otwieraj go z żadnego komputera. I nikomu nie udostępniaj dostępu.

Adam blokuje telefon.

ADAM
Bez mojego udziału nikt tych danych nie dostanie.

Rozłącza się.
```

Semantic invariants accepted as preserved:

- Anna's local copy is gone;
- one authoritative source remains;
- Adam still controls access to that source;
- physical possession/custody is replaced by access control;
- no physical data carrier remains;
- `Bez mojego udziału nikt tych danych nie dostanie` remains semantically true.

## 5. Canonical-effect preparation boundary

This repository is the ScriptOps tool repository. The SCN-012/SCN-027 workload was materialized by the deterministic P3 evaluation fixture in a temporary ScriptOps project. The tool repository `main` does not contain a live screenplay canon at `scenes/SCN-012.fountain` and `scenes/SCN-027.fountain` to which this Human decision can truthfully be applied as a real project effect.

Therefore this record prepares the exact accepted effect but does not pretend that changing ScriptOps tool files would be a screenplay canonical write.

A future canonical effect requires an exact target project instance containing the accepted source identity for SCN-012 and SCN-027, followed by a separate Human effect gate before any `approve --why` / canonical write.

## 6. Prepared effect

The prepared effect is exactly:

```text
SCN-012 accepted source
→ Human-accepted no-carrier SCN-012 proposal

SCN-027 accepted source
→ Human-accepted no-carrier SCN-027 proposal
```

No alternative wording, additional scene rewrite, downstream expansion or dramatic-beat repair is authorized by this decision.

## 7. Required next Human gate before effect

Before canonical application, the system must present:

1. exact target project / canonical scene identities;
2. exact source hashes or equivalent accepted identities for SCN-012 and SCN-027;
3. exact candidate identities matching the Human-accepted proposal content above;
4. the exact `why` / decision rationale to be recorded;
5. confirmation that no unrelated canonical files will change.

Only after a separate Human authorization may the canonical-effect command(s) be executed.

## 8. Current state

```text
SCN-012 + SCN-027 SEMANTIC ACCEPTANCE = YES
NO-CARRIER GOAL FOR BOUNDED SCOPE = SEMANTICALLY SATISFIED
CANONICAL EFFECT PREVIEW = PREPARED
CANONICAL EFFECT = NOT APPLIED
HUMAN EFFECT GATE = REQUIRED
GOAL DONE = NO
ATOMIC MULTI-SCENE APPROVAL = NOT AUTHORIZED / NOT IMPLEMENTED
NEW CAPABILITY = NO
MATURITY CLAIM = NONE
```
