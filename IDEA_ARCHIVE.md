# IDEA_ARCHIVE

Wpisy są zachowane, ale nie należą do zakresu RC1. Żaden wpis nie jest zgodą na implementację.

## IDEA-SO-001 — browser helper

Status: `PARKING`

Problem: ręczne przenoszenie odpowiedzi WebAI.

Dlaczego nie teraz: RC1 świadomie testuje ręczny import; automatyzacja interfejsu zwiększa kruchość i zakres.

Warunek powrotu: podstawowa pętla RC1 działa, a ręczny import jest zmierzonym, powtarzalnym wąskim gardłem.

## IDEA-SO-002 — integracje API

Status: `PARKING`

Problem: automatyczne wywołania modeli i narzędzi.

Dlaczego nie teraz: najpierw trzeba potwierdzić kontrakty kandydatów, walidacji i decyzji.

Warunek powrotu: działający RC1 i co najmniej dwa zadania, w których ręczny transfer powoduje mierzalny koszt lub błąd.

## IDEA-SO-003 — autonomiczny agent

Status: `PARKING`

Problem: redukcja ręcznej orkiestracji.

Dlaczego nie teraz: brak stabilnego rdzenia, testów regresji i bezpiecznego rollbacku.

Warunek powrotu: stabilny RC1, deterministyczne testy, sandbox, rollback i jawne granice operacji wymagających zatwierdzenia.

## IDEA-SO-004 — AI Guard

Status: `PARKING`

Problem: wykrywanie naruszeń reguł i ryzyk przed zmianą kanonu.

Dlaczego nie teraz: nie ustalono jeszcze minimalnego kontraktu walidacji RC1.

Warunek powrotu: co najmniej dwa konkretne przypadki, w których walidacja RC1 przepuściła szkodliwą zmianę.

## IDEA-SO-005 — automatyczny graf semantyczny

Status: `PARKING`

Problem: śledzenie zależności i wpływu zmian.

Dlaczego nie teraz: graf może wyprzedzić dowód, że prosty raport wpływu jest niewystarczający.

Warunek powrotu: dwa porównywalne błędy wpływu, których nie da się naprawić małą korektą modelu danych lub raportu.

## IDEA-SO-006 — pełny IdeaOps

Status: `PARKING`

Problem: zachowywanie wartościowych pomysłów bez aktywowania ich.

Dlaczego nie teraz: repo i ten plik zapewniają minimalny mechanizm.

Warunek powrotu: co najmniej dwa przypadki utraty pomysłu, aliasu albo warunku powrotu mimo używania obecnego archiwum.

## IDEA-SO-007 — dashboard

Status: `PARKING`

Problem: widoczność stanu projektu.

Dlaczego nie teraz: aktualny stan jest mały i czytelny w Markdown.

Warunek powrotu: nawigacja po stanie wymaga powtarzalnej pracy ręcznej lub prowadzi do błędnych decyzji.

## IDEA-SO-008 — eksport

Status: `PARKING`

Problem: przekazywanie stanu lub produktów pracy do innych formatów.

Dlaczego nie teraz: nie ma ustalonego, zwalidowanego formatu wyniku RC1.

Warunek powrotu: istnieje konkretny odbiorca i format, którego nie obsłuży prosty eksport plików.

## IDEA-SO-009 — multi-user

Status: `PARKING`

Problem: współpraca wielu osób.

Dlaczego nie teraz: projekt jest obecnie jednoosobowy, a model uprawnień zwiększyłby zakres przed walidacją rdzenia.

Warunek powrotu: rzeczywisty drugi użytkownik i konflikt uprawnień, którego nie rozwiązuje Git oraz jawna procedura review.

## IDEA-SO-010 — Narrative Change Impact Engine

Status: `PARKING / PARTIALLY REPRESENTED IN RC1`

Problem: ocena konsekwencji zmiany kanonu.

Zakres RC1: prosty raport wpływu.

Warunek powrotu pełnej wersji: prosty raport wpływu zawiedzie w co najmniej dwóch realnych zmianach narracyjnych.

## IDEA-SO-011 — Rule Miner / Retcon Engine

Status: `PARKING`

Problem: wykrywanie reguł i zarządzanie zmianami wstecznymi.

Dlaczego nie teraz: brak zwalidowanych danych i rzeczywistych przypadków retconu w RC1.

Warunek powrotu: powtarzalne ręczne wykrywanie ukrytych reguł albo retcon wymagający wieloetapowej korekty.

## IDEA-SO-012 — hybrydowa architektura API + WebAI

Status: `PARKING / CROSS-PROJECT`

Problem: połączyć zdolności planistyczne WebAI z kontrolą i tanim wykonaniem przez API.

Warunek powrotu: porównywalny test na rzeczywistym zadaniu po uzyskaniu działającego RC1. Nie jest częścią obecnego zakresu ScriptOps.
