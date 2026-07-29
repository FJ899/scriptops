# Odtworzenie prototypu ScriptOps v2

Pełny historyczny plik jest dostępny bezpośrednio jako:

```text
legacy/scriptops-v2-single.py
```

To jest pojedyncza kanoniczna kopia prototypu v2. Siedem plików w `sources/prototype/` pozostaje zapisem transportowym i awaryjnym dowodem odtwarzalności, a nie drugim plikiem roboczym.

## Zalecana kontrola

W katalogu głównym repo uruchom:

```bash
python scripts/verify_repository.py
```

Walidator:

1. sprawdza kanoniczny pełny plik;
2. kontroluje jego SHA-256, rozmiar, UTF-8 i składnię Python;
3. składa siedem części transportowych w pamięci;
4. potwierdza, że odtworzona treść jest identyczna z `legacy/scriptops-v2-single.py`.

## Awaryjne odtworzenie

Gdy kanoniczny plik zostanie uszkodzony albo utracony:

```bash
python scripts/restore_v2.py --force
```

Domyślnym plikiem wynikowym jest `legacy/scriptops-v2-single.py`.

Sama kontrola części bez zapisu:

```bash
python scripts/restore_v2.py --check-only
```

Odtworzenie do innej lokalizacji:

```bash
python scripts/restore_v2.py --output /tmp/scriptops-v2-single.py
```

## Metoda ręczna — Linux / macOS / Git Bash

```bash
cat sources/prototype/scriptops-v2-single.py.part01 \
    sources/prototype/scriptops-v2-single.py.part02 \
    sources/prototype/scriptops-v2-single.py.part03 \
    sources/prototype/scriptops-v2-single.py.part04 \
    sources/prototype/scriptops-v2-single.py.part05 \
    sources/prototype/scriptops-v2-single.py.part06 \
    sources/prototype/scriptops-v2-single.py.part07 \
    > legacy/scriptops-v2-single.py
```

## Kontrola integralności

```text
SHA-256: 881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596
Rozmiar: 51980 B
```

Plik jest materiałem historycznym i częściowo wykonywalnym prototypem. Nie należy uznawać go automatycznie za bazę RC1 przed porównaniem z `sources/RC1_SCOPE_LOCK.md`.
