---
project: "Narzędzie pisarskie / ScriptOps"
canonical_name: "ScriptOps"
cos_status: "QUEUED #1"
status: "NOT ACTIVATED / SOURCE OF TRUTH ACTIVE / BASE SELECTION DECISION REQUIRED"
reconstructed_at: "2026-07-27"
updated_at: "2026-08-10"
state_owner: "PROJECT_STATE.md"
---

# PROJECT_STATE — Narzędzie pisarskie / ScriptOps

## 1. Aktualny rezultat

Przygotować i empirycznie sprawdzić najmniejszą wersję ScriptOps RC1,
która przeprowadza jedną rzeczywistą zmianę narracyjną przez pełną pętlę:

```text
task
→ context bundle
→ WebAI candidate import
→ validation
→ impact report
→ human decision
→ decision log
→ Git commit
```

Celem obecnego etapu nie jest budowa pełnej wizji ScriptOps v5.

## 2. Definicja projektu

ScriptOps jest lokalnym systemem kontroli prawdy, decyzji i zmian
dla projektów narracyjnych oraz innych projektów intensywnie
wykorzystujących idee i AI.

AI tworzy kandydatów. ScriptOps przygotowuje kontekst, kontroluje
strukturę i raportuje wpływ. Człowiek zatwierdza albo odrzuca zmianę.

Dopiero zmiana zwalidowana, zatwierdzona, zapisana z uzasadnieniem
i utrwalona w Git staje się prawdą projektu.

## 3. Historia projektu

1. Workflow B3 → B2 → RR prowadził rzeczywistą produkcję „Przygód Liścionka”.
2. Mądry Warsztat / S2 Studio uporządkował role, stan, recenzję i przekazywanie artefaktów.
3. ScriptOps v2 przeniósł część mechanizmów do lokalnego CLI.
4. ScriptOps WebAI v5 rozszerzył projekt do systemu kontroli prawdy.
5. Final Master Package zamknął zakres MVP RC1 i przygotował instrukcje implementacyjne dla Codex.

B3, B2, RR, S2 Studio, ScriptOps v2, v5 i RC1 są etapami, rolami
lub wersjami tego samego projektu.

## 4. Najnowsze decyzje użytkownika

1. Narzędzie pisarskie / ScriptOps jest projektem numer 1 w kolejce.
2. Projekt ma zostać odtworzony przed dalszą implementacją.
3. Użytkownik pozostaje właścicielem koncepcji, kanonu i decyzji.
4. AI nie może automatycznie zmieniać kanonu.
5. Szczegółowy stan projektu należy do tego repozytorium, nie do głównego pliku Creative OS.
6. Ten dokument jest zatwierdzonym lokalnym źródłem prawdy.

## 5. Zrekonstruowane decyzje produktowe

Final Master Package wskazuje jako aktualny kandydat decyzji:

1. ScriptOps jest lokalnym systemem kontroli prawdy, a nie głównie AI writerem, analizatorem scenariusza ani prompt managerem.
2. RC1 ma udowodnić najmniejszą lokalną pętlę kontroli.
3. RC1 obejmuje:
   - lokalny projekt i CLI;
   - zadania;
   - pakiet kontekstu;
   - ręczny import odpowiedzi WebAI;
   - walidację strukturalną;
   - prosty raport wpływu;
   - approve / reject / revision;
   - decision log z uzasadnieniem;
   - Git commit;
   - dirty-state detection;
   - smoke test.
4. RC1 nie obejmuje:
   - browser helpera;
   - integracji API;
   - autonomicznego agenta;
   - AI Guard;
   - automatycznego grafu semantycznego;
   - pełnego IdeaOps;
   - dashboardu;
   - eksportu;
   - multi-user.
5. Wartościowe pomysły post-MVP mają być zachowywane, ale nie implementowane przed dowodem potrzeby.

## 6. Potwierdzone rezultaty

### OBSERVED WORKING RESULT

- Workflow B3 → B2 → RR doprowadził do kompletnego pakietu pierwszego sezonu „Przygód Liścionka”.
- S2 Studio doprowadziło do zaakceptowanego working draftu E01.
- E02 przeszedł review jako PASS WITH MINOR FIX bez potrzeby zmiany struktury lub kanonu.

### EXECUTABLE MECHANISM — CZĘŚCIOWY

- `legacy/scriptops-v2-single.py` uruchamia się.
- Potwierdzono inicjalizację projektu, kontrolę stanu, utworzenie sceny, zmianę statusu sceny i automatyczne commity Git.
- Prototyp v2 nie jest implementacją v5 RC1.

### EXISTING ARTIFACT

- `ScriptOps_FINAL_MASTER_PACKAGE` zawiera definicję produktu, podsumowanie decyzji, blokadę zakresu RC1, instrukcje dla Codex, kontrakty i testy na poziomie specyfikacji oraz materiały post-MVP.

### ACCESS CHECK — GITHUB SIDE COMPLETE

- w dostępnym zestawie repozytoriów GitHub wyszukiwanie `scriptops` wskazuje tylko `litrgratis-pixel/scriptops`;
- wyszukiwanie repozytorium `RC1` nie zwraca późniejszej implementacji;
- brak późniejszego RC1/Codex builda w dostępnym pakiecie GitHub;
- lokalne/off-GitHub artefakty pozostają nieznane.

Szczegóły i porównanie v2 z RC1: `analysis/RC1_V2_GAP_2026-08-10.md`.

## 7. Elementy niepotwierdzone

- Brak dowodu implementacji ScriptOps v5 RC1.
- Brak pełnego smoke testu RC1.
- Brak potwierdzonego późniejszego repozytorium zgodnego z Final Master Package w dostępnym GitHubie.
- Nie można wykluczyć lokalnego/off-GitHub wyniku Codex niedostępnego w podłączonym źródle.
- Brak testu pełnej pętli na rzeczywistej zmianie narracyjnej.
- Brak testu z niezależnym użytkownikiem.
- Brak VALIDATED RESULT.
- Browser helper, AI Guard, Rule Miner, Retcon Engine, pełny IdeaOps, dashboard i graf semantyczny pozostają post-MVP.

## 8. Aktualne rozjazdy

### Finalna specyfikacja a gotowy produkt

Dokumenty określają v5 jako finalną wersję specyfikacji lub pakietu,
ale zawierają instrukcje rozpoczęcia implementacji, nie gotowy build.

**Werdykt:** Final Master Package jest źródłem aktualnego zakresu, ale nie dowodem wykonania programu.

### Prototyp v2 a zakres v5 RC1

Porównanie z 2026-08-10 potwierdza, że v2 ma większość mechaniki potrzebnej do jednego happy-pathu: CLI, Git, task/context, walidację, staging, approve i decision log. Jednocześnie istnieją konkretne blokery wykonania:

1. tworzony task pozostawia dirty tree, a `check-pre` wymaga clean tree;
2. task/context/WebAI artifacts mogą pozostawić dirty tree przed `approve`;
3. `approve` zmienia `candidate` na `accepted` bez przeliczenia hasha sceny;
4. approve nie wymaga `why`;
5. brak impact reportu i pełnego smoke testu.

**Rekomendacja techniczna:** użyć `legacy/scriptops-v2-single.py` jako bazy najmniejszego jednego przypadku, zamiast przepisywać istniejące mechanizmy. To nadal rekomendacja, nie zatwierdzona decyzja o bazie.

### Redukcja pracy ręcznej

RC1 nadal zakłada ręczne przeniesienie odpowiedzi WebAI.

**Werdykt:** to świadome ograniczenie pierwszego testu. Automatyzacja przeglądarki pozostaje osobnym kierunkiem post-MVP. Tarcie ręcznego kroku należy zmierzyć w pierwszym realnym cyklu, a nie zakładać z góry.

## 9. Miejsce zatrzymania

`ACCESS CHECK` po stronie dostępnego GitHuba został zakończony wynikiem:

`NOT FOUND ON ACCESSIBLE GITHUB — V2 VS RC1 COMPARISON COMPLETE`.

Porównanie v2 z RC1 zostało zapisane w `analysis/RC1_V2_GAP_2026-08-10.md`.

Zgodnie z `DEC-SO-006` i `DEC-SO-007` następny krok jest decyzją o bazie implementacji. Nie należy rozpoczynać zmian runtime przed jej zatwierdzeniem.

## 10. Rzeczywista blokada

`BASE SELECTION DECISION REQUIRED`

Rekomendacja: wybrać `legacy/scriptops-v2-single.py` jako bazę najmniejszej naprawy jednego end-to-end happy-pathu i wdrożyć tylko blokery B1–B5 opisane w analizie.

## 11. Jeden następny krok

Człowiek zatwierdza albo odrzuca użycie `legacy/scriptops-v2-single.py` jako bazy dla jednego minimalnego end-to-end przypadku ScriptOps.

Po zatwierdzeniu implementacja powinna ograniczyć się do najmniejszego delta potrzebnego dla: task → context → candidate → validation → impact → human approve z `why` → poprawny hash → Git commit → smoke test.

## 12. Źródła szczegółowe

### Źródła zabezpieczone bezpośrednio w tym repo

- `sources/Decision_Summary_Current_State.md` — aktualne podsumowanie decyzji produktu;
- `sources/ScriptOps_Main_Theme_Summary.md` — definicja i główne prawo produktu;
- `sources/RC1_SCOPE_LOCK.md` — obowiązująca blokada zakresu RC1;
- `CODEX_START.md` — samowystarczalna instrukcja rozpoczęcia etapu planowania;
- `legacy/scriptops-v2-single.py` — pojedyncza kanoniczna kopia historycznego prototypu v2;
- `sources/prototype/RESTORE.md` — instrukcja awaryjnego odtworzenia prototypu;
- `scripts/restore_v2.py` — kontrola i odtworzenie kanonicznego pliku;
- `sources/prototype/scriptops-v2-single.py.part01` … `part07` — transportowy zapis pełnej treści prototypu v2;
- `RECONSTRUCTION_REPORT.md` i `SOURCE_AUDIT_SUMMARY.md` — historia, dowody i granice rekonstrukcji;
- `analysis/RC1_V2_GAP_2026-08-10.md` — aktualny access check i porównanie wykonawcze.
