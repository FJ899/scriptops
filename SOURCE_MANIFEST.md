# SOURCE_MANIFEST

Repo zawiera minimalny pakiet potrzebny do odtworzenia rekonstrukcji i kontynuacji pracy bez dostępu do wcześniejszego czatu.

## Aktywne źródła interpretacyjne

- `PROJECT_STATE.md` — kanoniczny stan operacyjny;
- `DECISION_LOG.md` — jawne decyzje;
- `HANDOFF.md` — punkt wznowienia;
- `IDEA_ARCHIVE.md` — pomysły poza RC1;
- `sources/CURRENT_PRODUCT_TRUTH.md` — aktualna definicja produktu, Scope Lock i instrukcja budowy RC1;
- `sources/ScriptOps_WebAI_v5_FINAL_SINGLE_USER.md` — szeroka specyfikacja v5;
- `sources/scriptops-v2-single.py` — częściowo wykonywalny prototyp;
- `sources/USER_DECISIONS_RAW.md` — surowe decyzje B4, B5 i Aneks;
- `sources/S2_PREDECESSOR_RAW.md` — stan i reguły bezpośredniego poprzednika;
- `sources/TRANSITION_AUDITS_RAW.md` — audyty przejścia do ScriptOps;
- `sources/POST_MVP_IDEAS.md` — patche, badanie alternatyw i roadmapa post-MVP.

## Integralność plików źródłowych

| Plik | SHA-256 | Rozmiar |
|---|---|---:|
| `sources/CURRENT_PRODUCT_TRUTH.md` | `f0e85ce24b62e92af420fdc26ef125cab7be432fe518f77486ba5e15b919ff14` | 27672 B |
| `sources/POST_MVP_IDEAS.md` | `817b53cef3da52fbbaaee15f10e1579849113ab97dedcfcc51a0e5566825570d` | 39152 B |
| `sources/S2_PREDECESSOR_RAW.md` | `809e144cb753f64f89778b886d52e68091ec4ae3b14314f3af0fee5b83bcddc5` | 37326 B |
| `sources/ScriptOps_WebAI_v5_FINAL_SINGLE_USER.md` | `6461b9de12f45475c1e65108d77c70d1a04e5c980e217ada31866d7157c84e21` | 14866 B |
| `sources/TRANSITION_AUDITS_RAW.md` | `70c8e584ed0f91056fc7bf0cd801c1cf7f5673a1fdfd96b32392f78026d4114f` | 39351 B |
| `sources/USER_DECISIONS_RAW.md` | `3aeef7e3aa4919f7ba482f978562b63bd4502e4e51919b53928f8aec3dfbcdf9` | 26886 B |
| `sources/scriptops-v2-single.py` | `881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596` | 51980 B |

## Pochodzenie

Pliki w `sources/` są wiernymi połączeniami lub kopiami materiałów z minimalnego pakietu READ_ONLY. Każda sekcja w plikach łączonych zaczyna się nagłówkiem `SOURCE:` wskazującym oryginalną ścieżkę.

## Granica kompletności

Pakiet zabezpiecza:

- najpóźniejszy udokumentowany stan produktu;
- szeroką wizję v5;
- zakres RC1;
- instrukcje implementacyjne;
- wcześniejszy kod;
- jawne decyzje użytkownika;
- działający poprzednik procesu;
- audyty przejścia;
- pomysły post-MVP i ich źródłowe uzasadnienia.

Nie zabezpiecza nieodnalezionej implementacji lub odpowiedzi Codex powstałej po Final Master Package. Ta luka pozostaje jawnie oznaczona jako `ACCESS CHECK REQUIRED`.
