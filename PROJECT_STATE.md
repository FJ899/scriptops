---
project: "Narzędzie pisarskie / ScriptOps"
canonical_name: "ScriptOps"
cos_status: "QUEUED #1"
status: "NOT ACTIVATED / SOURCE OF TRUTH ACTIVE / ACCESS CHECK REQUIRED"
reconstructed_at: "2026-07-27"
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

- `scriptops-v2-single.py` uruchamia się.
- Potwierdzono inicjalizację projektu, kontrolę stanu, utworzenie sceny, zmianę statusu sceny i automatyczne commity Git.
- Prototyp v2 nie jest implementacją v5 RC1.

### EXISTING ARTIFACT

- `ScriptOps_FINAL_MASTER_PACKAGE` zawiera definicję produktu, podsumowanie decyzji, blokadę zakresu RC1, instrukcje dla Codex, kontrakty i testy na poziomie specyfikacji oraz materiały post-MVP.

## 7. Elementy niepotwierdzone

- Brak dowodu implementacji ScriptOps v5 RC1.
- Brak pełnego smoke testu RC1.
- Brak potwierdzonego późniejszego repozytorium zgodnego z Final Master Package.
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

Istniejący prototyp realizuje część starszego procesu, lecz ma inny model danych i mniejszy zakres.

**Werdykt:** nie zakładać, że v2 jest bazą RC1 bez porównania kodu z `sources/RC1_SCOPE_LOCK.md`.

### Redukcja pracy ręcznej

RC1 nadal zakłada ręczne przeniesienie odpowiedzi WebAI.

**Werdykt:** to świadome ograniczenie pierwszego testu. Automatyzacja przeglądarki pozostaje osobnym kierunkiem post-MVP.

## 9. Miejsce zatrzymania

Zakres ScriptOps v5 RC1 został zamknięty.

Przygotowano materiały nakazujące Codexowi najpierw przedstawić:

- drzewo repozytorium;
- moduły;
- tabele SQLite;
- mapę CLI;
- plan testów;
- sprzeczności;
- listę wykluczonych funkcji.

Implementacja miała rozpocząć się po zatwierdzeniu planu. W dostępnych
materiałach nie ma dowodu, że nastąpiło zatwierdzenie planu albo implementacja.

## 10. Rzeczywista blokada

`ACCESS CHECK REQUIRED`

Należy ustalić, czy istnieje późniejsze repozytorium, kod albo wynik
pracy Codex nieobecny w przekazanym pakiecie.

## 11. Jeden następny krok

Sprawdzić notatki, lokalne foldery i dostępne repozytoria pod kątem
późniejszej implementacji ScriptOps RC1 lub odpowiedzi Codex powstałej
po Final Master Package.

Jeżeli nic takiego nie istnieje, następnym krokiem będzie porównanie
odtworzonego `scriptops-v2-single.py` z `sources/RC1_SCOPE_LOCK.md`
przed decyzją o bazie implementacji.

## 12. Źródła szczegółowe

### Źródła zabezpieczone bezpośrednio w tym repo

- `sources/Decision_Summary_Current_State.md` — aktualne podsumowanie decyzji produktu;
- `sources/ScriptOps_Main_Theme_Summary.md` — definicja i główne prawo produktu;
- `sources/RC1_SCOPE_LOCK.md` — obowiązująca blokada zakresu RC1;
- `CODEX_START.md` — samowystarczalna instrukcja rozpoczęcia etapu planowania;
- `sources/prototype/RESTORE.md` — instrukcja odtworzenia prototypu;
- `scripts/restore_v2.py` — automatyczne odtworzenie i kontrola integralności prototypu;
- `sources/prototype/scriptops-v2-single.py.part01` … `part07` — pełna treść prototypu v2;
- `RECONSTRUCTION_REPORT.md` i `SOURCE_AUDIT_SUMMARY.md` — historia, dowody i granice rekonstrukcji.

### Historyczne ścieżki pochodzenia

Poniższe nazwy opisują lokalizację w pierwotnym pakiecie źródłowym. Nie są ścieżkami aktywnego repo:

- `ScriptOps_FINAL_MASTER_PACKAGE/01_PRODUCT_TRUTH/Decision_Summary_Current_State.md`;
- `ScriptOps_FINAL_MASTER_PACKAGE/01_PRODUCT_TRUTH/ScriptOps_Main_Theme_Summary.md`;
- `ScriptOps_FINAL_MASTER_PACKAGE/03_CODEX_RC1_BUILD/RC1_SCOPE_LOCK.md`;
- `ScriptOps_FINAL_MASTER_PACKAGE/03_CODEX_RC1_BUILD/CODEX_MASTER_RC1_BUILD_INSTRUCTION.md`.

Treści potrzebne do zwykłego wznowienia zostały znormalizowane do plików wymienionych w poprzedniej sekcji. Oryginalny pełny pakiet pozostaje materiałem dowodowym poza aktywnym repo.

### Historyczne źródła S2 Studio / Mądrego Warsztatu

- `RR_S2_decyzja_start_architektury_v1.txt`;
- `DECYZJA_WDROZENIOWA_PO_AUDYTACH_MADRY_WARSZTAT_v1.md`;
- `00_PANEL_STANU_CURRENT.md`;
- `05_FILE_REGISTRY.md`;
- `03_S2_DECISION_LOG.md`.

Ich ustalenia wymagane do wznowienia zostały zachowane w `RECONSTRUCTION_REPORT.md` i `SOURCE_AUDIT_SUMMARY.md`. Oryginały nie są wymagane do zwykłego rozpoczęcia kolejnej sesji.

### Historyczne decyzje i reguły użytkownika

- `B4.txt`;
- `B5.txt`;
- `B5 - Aneks.txt`.

Ich aktualne konsekwencje są zapisane w sekcjach 4–5 tego dokumentu oraz w `DECISION_LOG.md`.
