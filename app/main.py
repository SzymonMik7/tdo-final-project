from fastapi import FastAPI, Request, Depends
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import books
from app.database import Base, engine, get_db
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app import models
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="LibraryLite")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(books.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    from app.init_db import init_db
    init_db()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ui/books", response_class=HTMLResponse)
def ui_books_list(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return templates.TemplateResponse(
        "books_list.html",
        {"request": request, "books": books},
    )


@app.get("/ui/books/{book_id}", response_class=HTMLResponse)
def ui_book_detail(
    request: Request,
    book_id: int,
    db: Session = Depends(get_db),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return templates.TemplateResponse(
            "books_list.html",
            {"request": request, "books": db.query(models.Book).all()},
            status_code=404,
        )
    return templates.TemplateResponse(
        "book_detail.html",
        {"request": request, "book": book},
    )


@app.get("/ui/books/{book_id}/edit", response_class=HTMLResponse)
def ui_book_edit(
    request: Request,
    book_id: int,
    db: Session = Depends(get_db),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return templates.TemplateResponse(
            "books_list.html",
            {"request": request, "books": db.query(models.Book).all()},
            status_code=404,
        )
    return templates.TemplateResponse(
        "book_edit.html",
        {"request": request, "book": book},
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
