# CODEX_DEMO_CyberSOC

> Gałąź ćwiczeniowa: funkcja do zaimplementowania celowo zwraca pusty wynik. Testy tej funkcji są czerwone. Pełne rozwiązanie znajdziesz na `main`.

![CI](https://github.com/lp830623/CODEX_DEMO_CyberSOC/actions/workflows/ci.yml/badge.svg)

Interaktywne centrum SOC: alerty, symulacje i korelacja zdarzeń.
Projekt do pokazów **Codex Ambassador**. Interfejs po polsku. Licencja MIT.

**Wyłącznie dane syntetyczne. Bez GCP, BigQuery, produkcyjnych nagrań i zewnętrznych API.**
Wyniki to jawne reguły demonstracyjne, nie odpowiedzi modelu AI. Nie potrzeba klucza API.

## Uruchomienie przez Docker

```sh
git clone https://github.com/lp830623/CODEX_DEMO_CyberSOC.git
cd CODEX_DEMO_CyberSOC
docker compose up --build --wait
```

Otwórz **http://localhost:8101**. API: http://localhost:8101/docs.
PostgreSQL ma własny wolumen i nie publikuje portu. Oba projekty mogą działać równolegle.
Obrazy i zależności należy pobrać przed pokazem; po przygotowaniu działanie dema nie wymaga internetu.

## Bez Dockera

Wymagania: Python 3.10+ oraz Node.js 22+. Pierwsze uruchomienie pobierze pakiety i zbuduje frontend.

```sh
python3 scripts/run_demo.py
```

Aplikacja działa na tym samym porcie, używając lokalnej SQLite. Ctrl+C zatrzymuje serwer.
Możesz podać `--port 8201`. Zmiana backendu: `DATABASE_URL` w środowisku, np. PostgreSQL.

## Co działa

- Dashboard z 500 logami i 12 incydentami, wykres aktywności i priorytety.
- Filtrowanie i wyszukiwanie incydentów, statusy, timeline, MITRE ATT&CK i playbooki.
- Cztery symulacje: brute force, phishing, ransomware i lateral movement.
- Korelacja: minimum 5 błędów w 10 minut, potem sukces w 2 minuty; izolacja kont i IP, deduplikacja.
- Dziennik działań, eksport JSON oraz druk / zapis PDF szczegółów.

Frontend jest statycznym eksportem Next.js, serwowanym przez FastAPI. Gdy otworzysz sam eksport
np. `python3 -m http.server 8301 --directory frontend/out`, interfejs przełączy się w tryb przeglądarkowy
z tymi samymi regułami i zapisem localStorage. To opcja zapasowa bez backendu; stan nie jest współdzielony.

## Reset i pokaz

Przycisk resetu w prawym górnym rogu przywraca tylko syntetyczny zestaw DEMO.
Z terminala (backend musi działać):

```sh
sh scripts/reset-demo.sh
```

- `main` — pełne działające rozwiązanie i wersja awaryjna.
- `demo/start` — celowo niezaimplementowana funkcja do wykonania przez Codexa; testy ćwiczenia pokazują brak funkcji.
- [Scenariusz prezentacji](docs/presenter-guide.md) — 20 minut, prompt i plan awaryjny.
- [Architektura i kontrakt API](docs/architecture.md).
- [Reguły pracy Codexa](AGENTS.md).

Po zmianie gałęzi użyj resetu i przebuduj aplikację, aby nie zachować wyników z wcześniejszej wersji.

## Testy

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python -m pytest backend/tests -q
cd frontend
npm ci
npm test
npm run typecheck
npm run build
```

Test E2E wymaga uruchomionego backendu z frontendem:

```sh
cd frontend
npx playwright install chromium
DEMO_BASE_URL=http://127.0.0.1:8101 npm run test:e2e
```

GitHub Actions wykonuje testy jednostkowe, buduje Docker Compose z PostgreSQL,
uruchamia aplikację i sprawdza pełny scenariusz Playwright. Zwykłe testy lokalne używają SQLite.

## Granice demonstracji

Aplikacja jest przygotowana do lokalnego pokazu. Nie zawiera logowania ani autoryzacji;
nie wystawiaj tego backendu bezpośrednio do internetu. Domyślne porty są przypięte do loopback.
To nie jest produkcyjny system SOC ani narzędzie do wykonywania ataków.
Nie wykonuje ruchu ofensywnego; symulator generuje jedynie rekordy wewnątrz aplikacji.
Ograniczone reguły są opisane i testowane; nie zastępują modeli ani weryfikacji człowieka.
