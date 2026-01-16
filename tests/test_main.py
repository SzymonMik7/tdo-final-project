from fastapi.testclient import TestClient
from app.main import app
import uuid

# Tworzymy klienta testowego, który "udaje" przeglądarkę
client = TestClient(app)

# 1. Test Twojego nowego endpointu /health
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# 2. Test Metryk (Osoba 2) - sprawdzamy czy endpoint istnieje
def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    # Sprawdzamy czy w treści jest cokolwiek od Prometheusa
    # (nie sprawdzamy dokładnych wartości, bo są zmienne)
    assert "python_info" in response.text or "# HELP" in response.text

# 3. Test CRUD Książek (Osoba 1) - Scenariusz: Dodaj i Sprawdź
def test_create_and_read_book():
    # Generujemy unikalny tytuł, żeby testy się nie myliły
    unique_title = f"Test Book {uuid.uuid4()}"
    
    payload = {
        "title": unique_title,
        "author": "Test Author",
        "year": 2024,
        "description": "Integration test description"
    }
    
    # KROK A: Wyślij POST (Dodaj książkę)
    response_create = client.post("/books/", json=payload)
    assert response_create.status_code == 200, f"Błąd tworzenia: {response_create.text}"
    data = response_create.json()
    assert data["title"] == unique_title
    assert "id" in data
    
    # KROK B: Wyślij GET (Pobierz listę)
    response_list = client.get("/books/")
    assert response_list.status_code == 200
    books = response_list.json()
    
    # KROK C: Sprawdź czy nasza książka jest na liście
    found = any(b["title"] == unique_title for b in books)
    assert found is True, "Utworzona książka nie pojawiła się na liście /books"
