from app.models import Book

def test_book_model_structure():
    """
    Sprawdza, czy model Book jest poprawnie zdefiniowany w SQLAlchemy.
    To testuje models.py bez potrzeby łączenia się z bazą danych.
    """
    # Sprawdź nazwę tabeli
    assert Book.__tablename__ == "books"

    # Sprawdź czy model ma wymagane pola (atrybuty klasy)
    assert hasattr(Book, "id")
    assert hasattr(Book, "title")
    assert hasattr(Book, "author")
    assert hasattr(Book, "year")
    assert hasattr(Book, "description")
