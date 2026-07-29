# Odtworzenie prototypu ScriptOps v2

Pełny plik `scriptops-v2-single.py` został zapisany w siedmiu częściach tekstowych, aby zachować go w repo bez zależności od poprzedniego czatu.

## Zalecana metoda automatyczna

W katalogu głównym repo uruchom:

```bash
python scripts/restore_v2.py
```

Skrypt:

1. sprawdza obecność siedmiu części;
2. łączy je w `scriptops-v2-single.py`;
3. sprawdza SHA-256;
4. sprawdza poprawność UTF-8 i składni Python;
5. nie zastępuje istniejącego pliku o innej treści bez `--force`.

Sama kontrola bez zapisu pliku:

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
    > scriptops-v2-single.py
```

## Metoda ręczna — PowerShell

```powershell
$parts = 1..7 | ForEach-Object {
  "sources/prototype/scriptops-v2-single.py.part{0:D2}" -f $_
}
Get-Content $parts | Set-Content -Encoding utf8 scriptops-v2-single.py
```

## Kontrola integralności

Oryginalna suma SHA-256:

```text
881dade6c6c506b9a9d41ebfbf68afb18b66db7583d35f746fb29ed7b36ac596
```

Linux / macOS:

```bash
sha256sum scriptops-v2-single.py
```

PowerShell:

```powershell
Get-FileHash scriptops-v2-single.py -Algorithm SHA256
```

Plik jest materiałem historycznym i częściowo wykonywalnym prototypem. Nie należy uznawać go automatycznie za bazę RC1 przed porównaniem z `sources/RC1_SCOPE_LOCK.md`.
