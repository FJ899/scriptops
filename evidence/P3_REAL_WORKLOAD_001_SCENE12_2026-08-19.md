# P3 REAL WORKLOAD 001 — SCENA 12 / usunięcie fizycznego nośnika

Date: 2026-08-19
Status: `OBSERVED WORKING RESULT / LOCAL CONTROL PASS / STRUCTURAL COVERAGE INSUFFICIENT / NO CANONICAL APPROVAL`
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

Przed jakimkolwiek approval test rozdziela co najmniej te zależności:

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

Pierwszy run #13 poprawnie zatrzymał się na błędzie samego test harnessu: case-sensitive assertion oczekiwał małej litery w frazie, mimo że kandydat zawierał wymagane dane. Ten błąd nie był przypisany ScriptOps i został poprawiony wyłącznie w teście.

Fresh corrected run:

- `Phase 6 ScriptOps smoke` #14 / run `32223864081`: PASS;
- `Verify repository state` #32 / run `32223864065`: PASS.

Log run #14 emituje:

```text
P3_REAL_WORKLOAD_001: MECHANISM_CONTROL=PASS; CANDIDATE_REWRITE=PASS; CANONICAL_EFFECT=NOT_APPLIED; DOWNSTREAM_DEPENDENCY_COVERAGE=INSUFFICIENT_EVIDENCE; HUMAN_APPROVAL=NOT_REQUESTED
```

## 7. Observed result

### PASS — controlled candidate lifecycle

- Human goal został zmaterializowany w bounded `rewrite-scene` task-pack;
- preflight i context-build przeszły;
- kandydat usuwa `pendrive` i zachowuje `ARCHIWUM`, nagrania/umowy/zdjęcia, lokalną kopię oraz źródłowy pakiet bez fizycznego nośnika;
- `check-post` stagedował kandydata;
- `impact-report.json` ma `REVIEW_REQUIRED` i `requires_human_decision=true`;
- canonical `SCN-012` pozostał dokładnie niezmieniony;
- `.scriptops/decision-log.ndjson` nie powstał, bo nie było Human approval.

### INSUFFICIENT EVIDENCE — project-wide structural impact

Aktualny Phase-6 `impact-report.json` kontroluje proponowany lokalny efekt na `scenes/SCN-012.fountain`, ale nie ustanawia pól ani dowodu dla:

- `affected_scenes`;
- `dependency_analysis`;
- `downstream_dependencies`.

W tym workloadzie nie dostarczono też późniejszych scen projektu, więc nie istnieje niezależny materiał, z którego można uczciwie potwierdzić wszystkie odwołania do oryginału, kopii, sejfu, czerwonego nośnika albo kontroli danych przez Adama.

Wynik dla Human goal:

`LOCAL REWRITE CANDIDATE: OBSERVED PASS`

`ALL DOWNSTREAM DEPENDENCIES PRESERVED: NOT ESTABLISHED / INSUFFICIENT EVIDENCE`

`GOAL DONE: NO`

To jest realne rozróżnienie między kontrolowaną edycją sceny a operacją na strukturze całego projektu.

## 8. Must not be inferred

Ten run nie może być promowany do:

- ScriptOps maturity claim;
- proof of project-wide Narrative Change Impact Engine;
- proof that later scenes are safe;
- Human approval of the candidate rewrite;
- authorization to write canonical `SCN-012`;
- authorization for new product capability, model/API integration, release, deploy or roadmap expansion.

## 9. Next evidence requirement

Aby rozstrzygnąć, czy problem wynika tylko z braku danych wejściowych, czy także z braku mechanizmu project-wide impact analysis, kolejny test powinien dostać **rzeczywisty późniejszy materiał projektu** zawierający co najmniej jedno zależne odwołanie do tej sceny (np. do oryginału/kopii/sejfu/posiadania danych przez Adama).

Do tego czasu nie należy ani zatwierdzać kandydata jako canonical change, ani deklarować, że Human goal został osiągnięty.
