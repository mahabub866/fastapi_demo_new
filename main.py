from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()

# Replace 'mysql://user:password@host/db_name' with your MySQL connection string.
DATABASE_URL = "mysql+mysqlconnector://root:password@db:3306/demo"


# Create the SQLAlchemy engine and sessionmaker
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define the Base class for declarative models
Base = declarative_base()

# Define the MySQL database model for books
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    author = Column(String(255), index=True)
    genre = Column(String(100), index=True)
    description = Column(Text)

# Create the tables in the database (if they don't exist)
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for the book response
class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    description: str

# Create a new book
@app.post("/books/", response_model=BookResponse)
def create_book(book: BookResponse, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Get a book by its ID
@app.get("/books/{book_id}", response_model=BookResponse)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookResponse(**book.__dict__)

# Update a book by its ID
@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updated_book: BookResponse, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for field, value in updated_book.dict().items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return BookResponse(**book.__dict__)

# Delete a book by its ID
@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}

# Run the FastAPI application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)