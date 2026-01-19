# LibraryLite

LibraryLite to minimalna aplikacja **FastAPI + SQLAlchemy + Jinja2** do zarządzania katalogiem książek. Udostępnia:
- **REST API** do operacji CRUD na zasobie `Book` (`/books/...`),
- lekki interfejs **HTML (Jinja2)** do wygodnej obsługi (UI),
- integrację z monitoringiem (**Prometheus + Grafana**) oraz procesami **CI/CD** w GitHub Actions.

Projekt realizuje wymagania:
- uruchomienie w kontenerach, 
- trwała baza SQLite w Docker Volume, 
- lint i testy w CI

---

## Najważniejsze adresy (domyślne porty)

- Aplikacja (strona główna): `http://localhost:8000/`
- UI (książki): `http://localhost:8000/ui/books`
- API (książki): `http://localhost:8000/books/`
- Dokumentacja Swagger: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090/`
- Grafana: `http://localhost:3000/`

---

## Mapa projektu

- Routing i logika CRUD (Books): `app/routers/books.py`
- Modele SQLAlchemy: `app/models.py`
- Schematy Pydantic: `app/schemas.py`
- Konfiguracja DB (engine + sesje): `app/database.py`
- Podpięcie routerów i template’ów: `app/main.py`
- Szablony UI: `app/templates/`
- Konteneryzacja: `Dockerfile`, `.dockerignore`
- Stack usług: `docker-compose.yml`

---

## Uruchomienie lokalne (Docker Compose)

W katalogu repozytorium:


```bash
docker compose up --build
```

Zatrzymanie usług:

```bash
CTRL+C
docker compose down
```

Reset danych (usuwa również wolumen z SQLite):

```bash
docker compose down -v
```

---

## Konfiguracja

### Zmiana portu aplikacji

Port hosta jest sterowany zmienną `APP_PORT`:

W `docker-compose.yml`:

```yaml
ports:
  - "${APP_PORT:-8000}:8000"
```

Uruchomienie na innym porcie (przykład):

```bash
APP_PORT=8001 docker compose up --build
```

### Konfiguracja bazy (SQLite)

Aplikacja odczytuje połączenie z bazy z `DATABASE_URL`. W `docker-compose.yml` ustawione jest:

```yaml
environment:
  - DATABASE_URL=sqlite:////data/app.db
volumes:
  - db_data:/data
```

Dzięki temu plik SQLite jest zapisywany w `/data/app.db` w kontenerze i utrzymywany w wolumenie `db_data`.

Podgląd pliku bazy w kontenerze:

```bash
docker compose exec app ls -lah /data
```

## Obraz Dockera (Dockerfile)

Aplikacja jest pakowana jako obraz na bazie `python:3.12-slim`.

### Założenia i optymalizacje

- **Rozdzielenie zależności od kodu** (lepsze cache warstw):
  - `requirements.txt` jest kopiowany i instalowany przed skopiowaniem `app/`.
  - Dzięki temu przy zmianach w kodzie (bez zmian zależności) Docker może wykorzystać cache i build jest szybszy.

- **Cache pobierania paczek pip (BuildKit)**:
  - Włączone cachowanie pobranych paczek między buildami, co przyspiesza kolejne budowania obrazu.
  - Jednocześnie `--no-cache-dir` ogranicza rozmiar finalnego obrazu (cache nie jest trzymany w obrazie).

- **Wymuszenie czytelnego działania runtime**:
  - uruchamianie przez Uvicorn na `0.0.0.0:8000` (widoczne z hosta przez mapowanie portów).

## Budowanie i uruchomienie bez Compose (opcjonalnie)

```bash
docker build -t librarylite:test .
docker run --rm -p 8000:8000 librarylite:test
```

Uwaga: trwałość bazy SQLite jest zapewniana w standardowym scenariuszu przez Docker Compose (wolumen).

---

## Docker Compose (uruchomienie aplikacji z wolumenem)

W Compose aplikacja działa z:

- mapowaniem portu hosta przez `APP_PORT`,
- `DATABASE_URL=sqlite:////data/app.db`,
- wolumenem `db_data` pod `/data`.

---

## Monitoring i Obserwacje

System monitoringu oparty na stosie **Prometheus** i **Grafana**, skonfigurowany jako **Provisioning** (automatyczne wdrożenie konfiguracji przy starcie z plików .yaml i .json).

### Metryki i Dashboard
| Wykres | Metryka | Opis |
| :--- | :--- | :--- |
| **Suma książek** | `BOOKS_ADDED_TOTAL` | Licznik (**Counter**) pomyślnych zapisów w bazie danych. |
| **Zasoby** | `container_cpu/memory` | Zużycie CPU i RAM przez kontener aplikacji. |
| **Ruch HTTP** | `http_requests_total` | Natężenie ruchu. |

### Alerty (Alerting Rules)
* **App Down**: Powiadomienie o braku sygnału `up` z aplikacji (awaria kontenera).
* **High Load**: Alert przy obciążeniu > 30 req/min (obliczany z okna 30s).

### Test wydajnościowy (Stress Test)
Aby przetestować działanie alertu **High Load**, uruchom w terminalu hosta:
```bash
for i in {1..150}; do curl -s http://localhost:8000/ > /dev/null; sleep 0.05; done
```

### Informacje dostępowe

| Usługa | Adres URL | Autoryzacja |
| :--- | :--- | :--- |
| **Grafana** | [http://localhost:3000](http://localhost:3000) | `admin` / `admin` |
| **Prometheus** | [http://localhost:9090](http://localhost:9090) | Dostęp otwarty |

---

## 🏗 DevOps, CI/CD & Quality Assurance

Sekcja poświęcona procesom zapewnienia jakości (QA), automatyzacji wdrożeń oraz strategii wersjonowania, za które odpowiada zespół DevOps (Osoba 3).

### 1. Konfiguracja Środowiska Deweloperskiego

Aby zapewnić izolację zależności i powtarzalność testów, pracujemy w wirtualnym środowisku Python.

**Tworzenie i aktywacja środowiska:**

```bash
# 1. Utwórz wirtualne środowisko (venv)
python -m venv venv

# 2. Aktywuj środowisko:
# Windows (Git Bash):
source venv/Scripts/activate
# Windows (PowerShell):
# .\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

```

**Instalacja zależności:**
Gdy środowisko jest aktywne (widoczny prefiks `(venv)`), zainstaluj pakiety:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt

```

### 2. Weryfikacja kodu (QA)

Projekt wykorzystuje narzędzia do statycznej analizy oraz testów automatycznych w celu utrzymania wysokiej jakości kodu.

| Polecenie | Narzędzie | Opis |
| --- | --- | --- |
| `ruff check .` | **Ruff** | Linter kodu. Sprawdza zgodność ze standardami PEP8, importy i wykrywa błędy składniowe. |
| `python -m pytest` | **Pytest** | Uruchamia pełny zestaw testów automatycznych. |

**Zakres testów (`tests/`):**

* **Smoke Tests:** Szybka weryfikacja czy moduły aplikacji importują się poprawnie.
* **Integration Tests:**
* `GET /health` – sprawdzenie statusu aplikacji (Liveness Probe).
* `GET /metrics` – weryfikacja, czy endpoint metryk Prometheusa jest dostępny.
* `POST/GET /books/` – testy scenariuszowe CRUD weryfikujące zapis i odczyt danych z bazy.



### 3. Automatyzacja CI/CD (GitHub Actions)

W katalogu `.github/workflows/` zdefiniowano automatyczne potoki:

* **CI (Continuous Integration):** Uruchamiane przy każdym *Push* i *Pull Request*. Wykonuje linter oraz testy. Blokuje możliwość zmerge'owania kodu, który nie przechodzi weryfikacji.
* **CD (Continuous Delivery):** Uruchamiane **wyłącznie** po otagowaniu commita (np. `v1.0.0`). Buduje obraz Docker i publikuje go w rejestrze **GitHub Container Registry (GHCR)**.

### 4. Strategia Wersjonowania

W projekcie wdrożono rygorystyczną politykę **Immutable Tags** (niezmiennych tagów), aby zagwarantować stabilność środowisk produkcyjnych.

**Obrazy Aplikacji (GHCR):**

1. ❌ **Brak tagu `latest`:** Nie używamy tagu `latest` w rejestrze zdalnym, aby uniknąć niekontrolowanych aktualizacji.
2. ✅ **Semantic Versioning:** Obrazy otrzymują tag zgodny z tagiem w git (np. `v1.0.0`, `v1.1.0`).
3. ✅ **Commit SHA:** Każdy obraz posiada dodatkowy tag z hashem commita (np. `sha-4f2a1b`) dla pełnej śnialności (traceability).

**Infrastruktura (`docker-compose.yml`):**
Obrazy usług zewnętrznych są "przypięte" do konkretnych wersji:

* `prom/prometheus:v2.45.0` (zamiast latest)
* `grafana/grafana:10.2.0` (zamiast latest)

### 🚀 Release Guide: Jak wydać nową wersję?

Aby zbudować i opublikować nową wersję aplikacji w GHCR:

1. Upewnij się, że gałąź `main` jest aktualna i testy przechodzą lokalnie.
2. Utwórz tag wersji (zgodnie z SemVer):
```bash
git tag v1.0.0

```


3. Wyślij tag do repozytorium (automatycznie uruchomi to pipeline CD):
```bash
git push origin v1.0.0

```


4. Po zakończeniu procesu w zakładce *Actions*, gotowy obraz pojawi się w sekcji **Packages** repozytorium.
