# SOURCE_MANIFEST

Repo zawiera minimalny pakiet potrzebny do wznowienia i kontynuacji pracy bez dostępu do wcześniejszego czatu.

## Kanoniczne źródła operacyjne

- `README.md` — kolejność uruchomienia nowej sesji;
- `PROJECT_STATE.md` — aktualny stan projektu;
- `HANDOFF.md` — punkt wznowienia i ACCESS CHECK;
- `DECISION_LOG.md` — jawne decyzje;
- `IDEA_ARCHIVE.md` — zachowane pomysły i warunki powrotu;
- `CODEX_START.md` — niezależny prompt etapu planowania RC1;
- `RECONSTRUCTION_REPORT.md` — zrekonstruowana historia, dowody i miejsce zatrzymania;
- `SOURCE_AUDIT_SUMMARY.md` — podsumowanie pełnej inwentaryzacji 2016 rekordów;
- `continuity/COLD_START_AUDIT-001.md` — niezależny test wznowienia bez pamięci rozmowy.

## Zachowane źródła produktowe

- `sources/Decision_Summary_Current_State.md` — aktualne podsumowanie decyzji produktu;
- `sources/ScriptOps_Main_Theme_Summary.md` — główna definicja i prawo produktu;
- `sources/RC1_SCOPE_LOCK.md` — obowiązująca blokada zakresu RC1;
- `sources/prototype/` — pełny prototyp `scriptops-v2-single.py` zapisany w siedmiu częściach wraz z instrukcją odtworzenia i sumą kontrolną.

Historyczne ścieżki z `ScriptOps_FINAL_MASTER_PACKAGE` są informacją o pochodzeniu. Aktywne, odczytywalne kopie wymagane do wznowienia znajdują się pod ścieżkami `sources/...` wymienionymi wyżej.

## Integralność prototypu

Oryginalny plik:

```text
scriptops-v2-single.py
SHA-256: 881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596
Rozmiar: 51980 B
```

Zalecana kontrola i odtworzenie:

```bash
python scripts/restore_v2.py --check-only
python scripts/restore_v2.py
```

Instrukcja alternatywna: `sources/prototype/RESTORE.md`.

## Pochodzenie

Rekonstrukcja została wykonana na podstawie minimalnego pakietu READ_ONLY obejmującego:

- ScriptOps Final Master Package;
- szeroką specyfikację v5;
- prototyp v2;
- materiały Mądrego Warsztatu / S2 Studio;
- decyzje B4, B5 i Aneks;
- dwa audyty przejścia;
- pełny indeks 2016 logicznych rekordów i 702 plików fizycznych.

Repo przechowuje wszystkie informacje wymagane do poprawnego wznowienia: stan, decyzje, zakres, dowody, pomysły, punkt zatrzymania, plan następnego kroku oraz kod prototypu.

## Granica kompletności

Zabezpieczono:

- tożsamość i historię projektu;
- najpóźniejszy udokumentowany zakres produktu;
- zakres i wykluczenia RC1;
- instrukcję rozpoczęcia pracy z Codex;
- wcześniejszy kod;
- kluczowe decyzje użytkownika;
- pomysły post-MVP z warunkami powrotu;
- dowody działania poprzednich procesów;
- główne sprzeczności i braki źródłowe;
- wynik niezależnego testu ciągłości.

Nie istnieje dostępny dowód późniejszej implementacji lub odpowiedzi Codex powstałej po Final Master Package. Ta niewiedza nie została ukryta; pozostaje aktywną blokadą `ACCESS CHECK REQUIRED`.
