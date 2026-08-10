# ScriptOps

Repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Status

`PHASE 6 BOUNDED PROOF / V2 BASE SELECTED / NO MATURITY CLAIM`

Jawna decyzja użytkownika: `legacy/scriptops-v2-single.py` jest bazą pierwszego kontrolowanego workflow. `REWRITE: NO`. `NEW CAPABILITY: NO`.

## Uruchomienie nowej sesji

Nowe AI ma przeczytać w tej kolejności:

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `analysis/RC1_V2_GAP_2026-08-10.md`
6. `IDEA_ARCHIVE.md`
7. `SOURCE_MANIFEST.md`
8. `RECONSTRUCTION_REPORT.md`

## Zasady nadrzędne

- odpowiedź AI jest kandydatem, nie prawdą projektu;
- zmiana kanonu wymaga walidacji, decyzji człowieka, uzasadnienia i zapisu w Git;
- candidate artifact nie jest jeszcze kanonicznym efektem;
- kanoniczny zapis Phase 6 następuje dopiero po `approve --why`;
- obecny etap nie obejmuje budowy pełnej wizji ScriptOps v5;
- nie wolno uznać specyfikacji albo smoke testu za maturity claim;
- nie wolno rozszerzać zakresu o nowe capability;
- pełne rozmowy i dane prywatne pozostają poza aktywnym drzewem.

## Phase 6 — reuse + hardening + proof

Wybrana historyczna baza:

```text
legacy/scriptops-v2-single.py
```

Historyczny plik pozostaje niezmieniony jako źródło i dowód v2. Ograniczony hardening:

```text
phase6/scriptops-v2-hardening.py
```

zamyka wyłącznie B1–B5:

1. task clean-tree checkpoint;
2. generated evidence/candidate-input lifecycle;
3. accepted hash;
4. mandatory human `why`;
5. impact report + smoke proof.

Test:

```bash
python -m unittest discover -s tests -p 'test_phase6_*.py' -v
```

## Kontrola repozytorium

```bash
python scripts/verify_repository.py
```

Walidator sprawdza trwałe źródła, spójność aktualnego statusu/handoffu, scope lock, decyzje, odtwarzalność pełnego historycznego v2 oraz obecność bounded Phase-6 proof path.

Awaryjne odtworzenie historycznego v2:

```bash
python scripts/restore_v2.py --force
```

## Zakaz rozbudowy w Phase 6

Nie dodawać browser helpera, direct model/API automation, autonomous approval, agent framework, multi-agent, GUI/dashboard, vector DB, semantic graph ani multi-user.

## Audyt ciągłości

Pierwszy niezależny cold start bez pamięci wcześniejszej rozmowy zapisano w `continuity/COLD_START_AUDIT-001.md`.

## Aktualny następny krok

Doprowadzić PR Phase 6 do zielonego end-to-end smoke i repository continuity verification. Dopiero wtedy zapisać końcowe evidence B1–B5 i scalić bounded hardening.

`FUNCTIONAL_SADDLE_ACCEPTED`: **NOT YET**.
