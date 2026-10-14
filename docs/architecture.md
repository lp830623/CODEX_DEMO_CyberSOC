# Architektura

## Przepływ

```mermaid
flowchart LR
    UI[Next.js + TypeScript] -->|same-origin JSON API| API[FastAPI]
    API --> STORE[SQLAlchemy snapshot v1]
    STORE --> DB[PostgreSQL w Dockerze / SQLite lokalnie]
    FIX[datasets/synthetic/seed.json] --> API
    UI -. bez API .-> LOCAL[localStorage + reguły TypeScript]
```

Next.js tworzy statyczny eksport. Jeden proces FastAPI obsługuje API i pliki frontendu,
więc nie potrzeba CORS, serwera Node ani dodatkowego reverse proxy. Style CSS i ikony są lokalne;
aplikacja nie ładuje fontów, analityki ani skryptów z zewnętrznych serwisów.

## Trwałość i schema v1

`demo_state_v1` zawiera jeden rekord `id=1`, `payload JSON`, `revision INTEGER`.
Inicjalizacja idempotentnie tworzy tę tabelę i wczytuje fixture. To wersjonowany schemat demonstracyjny,
nie system migracji dla bazy produkcyjnej. Przyszłe zmiany schematu wymagają jawnej migracji przed wydaniem.
Aktualizacje korzystają z compare-and-swap po `revision`. Dwa zapisy tej samej rewizji nie nadpiszą się;
drugi dostaje HTTP 409, a UI wczytuje aktualny stan. Reset również zwiększa rewizję.

Ta świadoma redukcja modelu ułatwia reset i przenoszenie scenariusza. Docelowy system produkcyjny
powinien rozbić encje na tabele, dodać migracje, autoryzację, monitoring i polityki danych.
Redis/worker pominięto: reguły są synchroniczne i małe, nie ma długich operacji API ani zadań audio.

## API

| Metoda | Ścieżka | Zachowanie |
|---|---|---|
| GET | `/api/health` | Sprawdza również połączenie z bazą, zwraca `mode=demo` |
| GET | `/api/state` | `{data, revision}` |
| POST | `/api/reset` | Przywraca fixture, opcjonalnie `expected_revision` |
| GET | `/api/export` | Pobieralny JSON stanu |
| POST | `/api/simulate` | `scenario`, idempotentny `run_id`, opcjonalna rewizja |
| PATCH | `/api/incidents/{id}` | `status` i/lub `step` (0–2), opcjonalna rewizja |

Każda mutacja zwraca `{data, revision}`. Pydantic odrzuca nieznane pola i błędne wartości.
Brak elementu: 404; niepoprawne dane: 422; konflikt: 409. UI pokazuje błąd zamiast udawać udany zapis.
W trybie przeglądarkowym dane są zapisywane wyłącznie w localStorage danej przeglądarki.

## Reguły domenowe

Detektor sortuje zdarzenia po czasie, usuwa duplikaty ID, grupuje po koncie i IP. Dla każdego sukcesu szuka wcześniejszych niepowodzeń: ostatnie nie dalej niż 2 minuty, co najmniej 5 w ciągu 10 minut do ostatniej porażki. Granice są inkluzywne, a sukces musi być ściśle późniejszy. Jedno znalezisko na sukces. Scenariusze mają stały zegar i izolowane konto na przebieg.

Backend Python i fallback TypeScript mają te same przypadki testowe. Testy pokrywają okna czasowe, duplikaty, kolejność oraz izolację.

## Dane

Zestaw jest w całości wygenerowany na potrzeby dema. IP używają zakresów dokumentacyjnych
192.0.2.0/24 oraz 198.51.100.0/24; to nie adresy infrastruktury użytkownika.
500 logów i 12 incydentów początkowych; cztery wewnętrzne scenariusze symulacji.
Brak połączeń z GCP, BigQuery, OpenAI API i danymi produkcyjnymi.
