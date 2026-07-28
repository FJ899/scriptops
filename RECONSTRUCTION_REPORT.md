# Rekonstrukcja projektu „Narzędzie pisarskie / ScriptOps”

## Werdykt główny

Materiały opisują jeden historycznie rozwijany kierunek narzędziowy, który wyrósł z rzeczywistej produkcji serialu „Przygody Liścionka”:

1. ręczny workflow `B3 → B2 → RR`;
2. Mądry Warsztat / S2 Studio;
3. generalizacja do lokalnego narzędzia ScriptOps;
4. ScriptOps WebAI v5 / MVP RC1 jako ostatnia udokumentowana wersja docelowa.

Najlepiej potwierdzona nazwa projektu to **Narzędzie pisarskie / ScriptOps**. Nie znaleziono podstaw, aby `Narrative Engine`, `Narrative Engine v5` albo `SPEC-v5` uznać za utrwalone nazwy kanoniczne. `Narrative Change Impact Engine` jest zdolnością ScriptOps, nie osobnym projektem.

## Model działania

ScriptOps ma umożliwiać prowadzenie złożonego projektu narracyjnego z pomocą AI bez oddawania AI kontroli nad kanonem, decyzjami i stanem projektu.

```text
pomysł / zadanie / żądanie zmiany
→ wybór kanonu i kontekstu
→ kandydat AI
→ walidacja strukturalna i kontrola ciągłości
→ raport wpływu
→ decyzja człowieka
→ zapis uzasadnienia
→ commit albo odrzucenie
→ stan umożliwiający wznowienie
```

Najważniejsza reguła produktu:

> Odpowiedź AI jest kandydatem. Prawdą staje się dopiero zmiana zwalidowana, zatwierdzona przez człowieka, zapisana z uzasadnieniem i utrwalona w repozytorium.

## Historia

### Workflow Liścionka

Ręczny system B3 → B2 → RR doprowadził do rzeczywistych rezultatów produkcyjnych: kompletnego pakietu pierwszego sezonu, locku sezonu i materiałów dla dziesięciu odcinków.

Poziom dowodu: `OBSERVED WORKING RESULT`.

### Mądry Warsztat / S2 Studio

Proces został uporządkowany przez jedno centrum decyzji, manifesty, karty kanoniczne, kontrolę review i jawne przekazywanie artefaktów. E01 uzyskał zaakceptowany working draft. E02 przeszedł review jako `PASS WITH MINOR FIX`.

Poziom dowodu: `OBSERVED WORKING RESULT — częściowy`.

### ScriptOps v2

Powstał samodzielny prototyp CLI z Git, strukturą projektu, stanami scen, kontrolą i commitami. Potwierdzono inicjalizację projektu, kontrolę stanu, utworzenie sceny, zmianę statusu oraz commity Git.

Poziom dowodu: `EXECUTABLE MECHANISM — częściowy`.

Prototyp nie odpowiada pełnemu zakresowi v5 RC1.

### ScriptOps WebAI v5 / Final Master Package

Pakiet zawiera definicję produktu, podsumowanie decyzji, blokadę zakresu RC1, instrukcje budowy dla Codex, protokoły pracy i materiały post-MVP.

Poziom dowodu: `EXISTING ARTIFACT`.

Nie odnaleziono implementacji v5 RC1 ani logów jej testów.

## Co rzeczywiście działa

| Element | Poziom dowodu |
|---|---|
| workflow B3 → B2 → RR | `OBSERVED WORKING RESULT` |
| produkcyjny system Liścionka | `OBSERVED WORKING RESULT` |
| Mądry Warsztat / S2 Studio | `OBSERVED WORKING RESULT — częściowy` |
| `scriptops-v2-single.py` | `EXECUTABLE MECHANISM — częściowy` |
| ScriptOps v5 RC1 | `EXISTING ARTIFACT / planowana implementacja` |
| pełny produkt używany powtarzalnie | brak dowodu |
| `VALIDATED RESULT` | brak |

## Najważniejsze rozjazdy

1. „Finalna wersja” oznacza finalny pakiet specyfikacyjny, nie gotowy produkt.
2. Pakiet dla Codex jest materiałem do rozpoczęcia budowy; nie jest buildem.
3. Kod v2 nie implementuje docelowego modelu v5 RC1.
4. Redukcja pracy ręcznej nie została jeszcze osiągnięta.
5. Architektura post-MVP rosła szybciej niż dowód potrzeby, dlatego później została wyłączona z RC1.
6. W historii występowało kilka lokalnych źródeł prawdy; obecnie ich właścicielem jest `PROJECT_STATE.md` w tym repo.

## Miejsce zatrzymania

Zakres ScriptOps v5 RC1 został zamknięty i przygotowano pakiet budowy dla Codex. Instrukcja wymagała, aby Codex najpierw przedstawił drzewo repo, moduły, tabele SQLite, mapę CLI, plan testów, sprzeczności i listę wykluczeń.

Nie odnaleziono dowodu, że plan został zatwierdzony ani że implementacja ruszyła.

## Braki do wznowienia

1. Ustalenie, czy istnieje późniejsza implementacja lub odpowiedź Codex.
2. Jeżeli nie istnieje: porównanie prototypu v2 z `RC1_SCOPE_LOCK.md`.
3. Decyzja, czy v2 jest bazą, materiałem do odzyskania, czy tylko dowodem historycznym.
4. Jeden test end-to-end na prawdziwej zmianie narracyjnej.
5. Kryteria zakończenia RC1.

## Jeden następny krok

Przeprowadzić `ACCESS CHECK` opisany w `HANDOFF.md`.

## Klasyfikacja projektu

- istniejący projekt historyczny i narzędziowy;
- wpisany w Creative OS jako `QUEUED #1`;
- lokalne źródło prawdy aktywne;
- projekt nadal `NOT ACTIVATED` do implementacji.
