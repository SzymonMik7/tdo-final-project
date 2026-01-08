def test_imports():
    """
    Smoke Test: Sprawdza, czy główne moduły aplikacji dają się zaimportować.
    Jeśli ten test pada, to znaczy, że brakuje bibliotek lub jest błąd składni w app/.
    """
    try:
        from app import database
        from app import models
        from app import schemas
        
        # Jeśli doszliśmy tutaj i nie było błędu, to sukces.
        assert True
    except ImportError as e:
        assert False, f"Błąd importu modułów aplikacji: {e}"
