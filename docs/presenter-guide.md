# Scenariusz Codex Ambassador — CyberSOC

## Przygotowanie

1. Pobierz repo, uruchom `docker compose up --build --wait` i otwórz localhost:8101.
2. Uruchom testy na main. To kompletna wersja awaryjna.
3. Zatrzymaj aplikację, przełącz `git switch demo/start`, przebuduj i zresetuj dane.
4. Zależności, obrazy i dostęp Codexa przygotuj przed pokazem. Aplikacja działa offline;
   sam Codex może wymagać internetu. W razie braku połączenia pokaż gotowy diff i main.
5. Zmiany wykonuj na roboczej gałęzi `git switch -c presentation/session`.

## 20 minut

| Czas | Działanie |
|---|---|
| 0–3 | Dashboard, lista incydentów, symulacja brute force |
| 3–6 | Pokaż błędy i późniejszy sukces; system bazowy nie koreluje zdarzeń |
| 6–12 | Codex: analiza repo, mała implementacja i testy |
| 12–16 | Uruchom testy, obejrzyj diff i sprawdź przypadki graniczne |
| 16–20 | Powtórz scenariusz w UI, pytania i wnioski |

## Prompt

```text
Przeanalizuj AGENTS.md i architekturę. Zaimplementuj detect_takeovers w Pythonie oraz detectTakeovers w TypeScript. Wykrywaj minimum 5 nieudanych logowań tego samego konta z tego samego IP w 10 minut, po których następuje sukces w kolejnych 2 minutach. Uwzględnij kolejność czasu, granice okien, duplikaty i izolację kont/IP. Uruchom istniejące testy i dodaj brakujące. Nie zmieniaj kontraktów API. W symulatorze ma pojawić się incydent krytyczny po brute force.
```

## Kryteria sukcesu

- Sześć błędów + sukces w symulatorze daje krytyczny incydent.
- Powtórzony ID nie podwaja zdarzeń ani nie zwiększa progu.
- Konta i IP pozostają odizolowane.
- Przypadki 10 minut i 2 minuty przechodzą, przekroczenie granic nie przechodzi.

## Plan awaryjny

Zachowaj zmiany na gałęzi roboczej, przełącz main, przebuduj i użyj resetu.
Przy problemie z backendem otwórz statyczny eksport `frontend/out` przez lokalny serwer HTTP.
Przy problemie z Codexem pokaż porównanie `demo/start...main` w GitHubie i omów testy.
Testy na demo/start celowo wskazują brak funkcji, więc nie przedstawiaj ich jako awarii środowiska.
