---
project: "ScriptOps"
portfolio_status: "QUEUED #1"
activation: "NOT ACTIVATED"
state_owner: "PROJECT_STATE.md"
blocker: "BASE SELECTION DECISION REQUIRED"
next_step: "human_decide_v2_as_single_slice_base"
resume_contract: "REVIEW DECISION / NO RUNTIME IMPLEMENTATION BEFORE BASE SELECTION"
---

# HANDOFF — ScriptOps

## Stan wejściowy

- Projekt: `Narzędzie pisarskie / ScriptOps`
- Pozycja w Creative OS: `QUEUED #1`
- Aktywacja: `NOT ACTIVATED`
- Lokalne źródło prawdy: `PROJECT_STATE.md`
- Blokada: `BASE SELECTION DECISION REQUIRED`

Nagłówek YAML jest maszynowym skrótem tego samego handoffu, a nie osobnym źródłem prawdy. W przypadku sprzeczności obowiązuje treść `PROJECT_STATE.md` oraz najnowsza jawna decyzja użytkownika.

## Co zostało wykonane

1. Zrekonstruowano ciąg: workflow B3 → B2 → RR → Mądry Warsztat / S2 Studio → ScriptOps v2 → ScriptOps WebAI v5 / RC1.
2. Zabezpieczono stan, źródła, decyzje, archiwum pomysłów i kanoniczny prototyp v2.
3. Zakończono GitHub-side `ACCESS CHECK`: w dostępnym zestawie nie ma późniejszego repo/builda ScriptOps RC1; lokalne/off-GitHub artefakty pozostają nieznane.
4. Porównano `legacy/scriptops-v2-single.py` z `sources/RC1_SCOPE_LOCK.md` i wymaganiem jednego pełnego happy-pathu.
5. Zapisano wynik w `analysis/RC1_V2_GAP_2026-08-10.md`.
6. Zidentyfikowano pięć konkretnych blockerów istniejącej ścieżki: clean-tree lifecycle taska/evidence, clean-tree przed approve, stale accepted hash, brak obowiązkowego `why`, brak impact report/smoke proof.

## Czego nie wykonano

- nie wybrano kanonicznej bazy implementacji;
- nie zmieniono runtime v2;
- nie wykonano pełnego smoke testu;
- nie wykonano rzeczywistej zmiany narracyjnej;
- nie zatwierdzono żadnej zmiany kanonu;
- nie ogłoszono VALIDATED RESULT.

## Rekomendacja

Użyć `legacy/scriptops-v2-single.py` jako bazy pierwszego jednego end-to-end happy-pathu. Powód: większość wymaganej mechaniki już istnieje, a wykryte braki są lokalnymi, konkretnymi blockerami. Przepisywanie od zera zwiększyłoby zakres bez dowodu potrzeby.

Ta rekomendacja nie jest decyzją projektu.

## Jeden następny krok

Człowiek zatwierdza albo odrzuca użycie `legacy/scriptops-v2-single.py` jako bazy dla minimalnego jednego przypadku end-to-end.

Jeżeli zatwierdzi, implementować wyłącznie delta potrzebne do: task → context → candidate import → validation → impact report → human approve z `why` → poprawny accepted hash → Git commit → smoke test.

## Zakaz dryfu

Do czasu decyzji o bazie nie rozwijać browser helpera, API, autonomicznego agenta, AI Guard, grafu semantycznego, pełnego IdeaOps, dashboardu, eksportu, multi-user ani innych elementów post-MVP.

## Pliki do otwarcia przez nową sesję

1. `README.md`
2. `PROJECT_STATE.md`
3. `HANDOFF.md`
4. `DECISION_LOG.md`
5. `sources/RC1_SCOPE_LOCK.md`
6. `analysis/RC1_V2_GAP_2026-08-10.md`
7. `legacy/scriptops-v2-single.py`
