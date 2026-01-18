from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal

router = APIRouter(prefix="/books")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@router.get("/{book_id}", response_model=schemas.Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.post("/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    obj = models.Book(
        title=book.title,
        author=book.author,
        description=book.description,
        year=book.year,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = book.title
    db_book.author = book.author
    db_book.description = book.description
    db_book.year = book.year

    db.commit()
    db.refresh(db_book)
    return db_book

@router.post("/{book_id}/edit", response_model=schemas.Book)
def update_book_via_form(
    book_id: int, 
    book: schemas.BookCreate, 
    db: Session = Depends(get_db)):
    return update_book(book_id, book, db)



@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted"}

@router.post("/{book_id}/delete")
def delete_book_via_form(book_id: int, db: Session = Depends(get_db)):
    return delete_book(book_id, db)

