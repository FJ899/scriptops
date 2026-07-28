# ScriptOps

Prywatne repozytorium lokalnego stanu projektu **Narzędzie pisarskie / ScriptOps**.

## Status

`QUEUED #1 / NOT ACTIVATED / SOURCE OF TRUTH ACTIVE / ACCESS CHECK REQUIRED`

## Uruchomienie nowej sesji

Nowe AI ma przeczytać w tej kolejności:

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `IDEA_ARCHIVE.md`
6. `SOURCE_MANIFEST.md`
7. `RECONSTRUCTION_REPORT.md`

Do rozstrzygania sporów lub sprawdzania pochodzenia decyzji użyć `SOURCE_AUDIT_SUMMARY.md`, `SOURCE_MANIFEST.md` i materiałów w `sources/`.

## Zasady nadrzędne

- odpowiedź AI jest kandydatem, nie prawdą projektu;
- zmiana kanonu wymaga walidacji, decyzji człowieka, uzasadnienia i zapisu w Git;
- obecny etap nie obejmuje budowy pełnej wizji ScriptOps v5;
- nie wolno uznać specyfikacji za działający produkt bez dowodu wykonania;
- nie wolno automatycznie aktywować projektu ani rozszerzać zakresu RC1;
- pełne rozmowy i dane prywatne pozostają poza aktywnym drzewem; repo zawiera minimalny, odtwarzalny pakiet dowodowy.

## Aktualny następny krok

Sprawdzić, czy istnieje późniejsze repozytorium, kod albo wynik pracy Codex zgodny z `RC1_SCOPE_LOCK.md`.

Jeżeli nie istnieje, porównać zachowany prototyp `scriptops-v2-single.py` z zakresem RC1 przed decyzją, czy prototyp jest bazą implementacji.
