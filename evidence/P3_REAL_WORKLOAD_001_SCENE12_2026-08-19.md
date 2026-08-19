# P3 REAL WORKLOAD 001 — SCENA 12 / usunięcie fizycznego nośnika

Date: 2026-08-19
Status: `EVALUATION CANDIDATE / CI PENDING / NO CANONICAL APPROVAL`
Authority: `USER-PROVIDED TEST MATERIAL + USER-PROVIDED CHANGE GOAL`
Semantic scope: `P3 WORKING EVALUATION / NOT MATURITY CLAIM / NOT PRODUCT ACTIVATION`

## 1. Wejście użytkownika — materiał testowy

`SCENA 12 — BIURO / DZIEŃ`

Adam wchodzi do niewielkiego biura. Anna siedzi przy biurku i przegląda dokumenty.

— Masz ten pendrive? — pyta bez podnoszenia wzroku.

Adam wyciąga z kieszeni czerwony pendrive i kładzie go na stole.

— Wszystko tam jest. Nagrania, umowy, zdjęcia.

Anna bierze pendrive i wkłada go do laptopa.

— Jeśli to trafi do prokuratury, Kowalski jest skończony.

Na ekranie pojawia się folder „ARCHIWUM”.

Anna kopiuje jego zawartość na komputer.

— Zrobię kopię. Oryginał schowamy w sejfie.

Adam bierze pendrive i wychodzi.

## 2. Human-owned goal

> Całkowicie usunąć pendrive z projektu i zastąpić go sposobem przekazania danych, który nie wymaga żadnego fizycznego nośnika, zachowując logikę sceny i wszystkie wynikające z niej późniejsze zależności.

Ten goal nie autoryzuje canonical write ani nie stwierdza, że downstream dependencies są znane.

## 3. Intelligence-proposed HOW — kandydat, nie decyzja

Najmniejszy kandydat zachowujący lokalną funkcję sceny:

- Adam przekazuje Annie jednorazowy dostęp do zaszyfrowanego pakietu danych;
- Anna uruchamia transfer na swoim laptopie;
- zawartość nadal pojawia się jako `ARCHIWUM`;
- Anna tworzy lokalną kopię roboczą;
- odpowiednikiem „oryginału” jest źródłowy pakiet pozostający w zaszyfrowanym magazynie, nie fizyczny nośnik;
- Adam wychodzi bez zabierania urządzenia z danymi.

Proponowana wersja dialogowo-akcyjna:

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

To jest `AI RECOMMENDATION / CANDIDATE`, nie Human decision i nie canon.

## 4. Wymagany structural-impact check

Przed jakimkolwiek approval test musi rozdzielić co najmniej te zależności:

1. `pendrive` jako fizyczny obiekt — ma zniknąć;
2. `oryginał` — musi dostać nową semantyczną tożsamość jako źródłowy pakiet;
3. `kopia` — pozostaje lokalną kopią roboczą Anny;
4. `sejf` — fizyczny sejf nie może być bezrefleksyjnie zachowany jako miejsce nośnika; potrzebny jest odpowiednik zabezpieczenia źródła;
5. `Adam bierze pendrive` — po zmianie nie istnieje ruch fizycznego nośnika; ewentualna późniejsza własność/kontrola dostępu musi być sprawdzona osobno;
6. późniejsze sceny mogą odwoływać się do koloru/nośnika, oryginału, kopii, sejfu, posiadania przez Adama albo sposobu dostępu.

## 5. Frozen evaluation question

Czy obecny ScriptOps Phase 6 potrafi jednocześnie:

- bezpiecznie stagedować rewrite jako candidate;
- pozostawić canon bez zmian przed Human approval;
- oraz **udowodnić**, że wszystkie downstream dependencies wymagane przez Human goal zostały odnalezione i zachowane?

Brak dowodu downstream coverage ma być `INSUFFICIENT EVIDENCE`, nie sukcesem.

## 6. Wykonanie

Dedykowana regresja/evaluation:

`tests/test_phase6_p3_real_workload_001.py`

Test używa aktualnego `legacy/scriptops-v2-single.py` i `phase6/scriptops-v2-hardening.py` w świeżym tymczasowym repo Git. Nie dodaje nowej capability do mechanizmu.

Ścieżka:

```text
user scene fixture
→ Human goal materialized into task-pack
→ check-pre
→ context-build (rewrite-scene)
→ AI candidate
→ check-post
→ staged candidate
→ impact-report.json
→ STOP before approve --why
```

## 7. Expected evidence boundary before CI

- `MECHANISM_CONTROL`: expected PASS
- `CANDIDATE_REWRITE`: expected PASS
- `CANONICAL_EFFECT`: expected NOT APPLIED
- `HUMAN_APPROVAL`: NOT REQUESTED
- `DOWNSTREAM_DEPENDENCY_COVERAGE`: expected `INSUFFICIENT EVIDENCE` unless the current impact artifact actually establishes affected-scene/dependency coverage

## 8. Must not be inferred

This run must not be promoted into:

- ScriptOps maturity claim;
- proof of project-wide Narrative Change Impact Engine;
- proof that later scenes are safe;
- Human approval of the candidate rewrite;
- authorization to write canonical `SCN-012`;
- authorization for new product capability, model/API integration, release, deploy or roadmap expansion.
