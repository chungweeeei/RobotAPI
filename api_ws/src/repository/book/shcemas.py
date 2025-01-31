from sqlalchemy.orm import registry

from sqlalchemy import (
    Integer,
    VARCHAR,
    Float,
    Column,
    DECIMAL,
    Text,
    Date,
    ForeignKey,
    PrimaryKeyConstraint
)

_BOOK_REPO_BASE = registry().generate_base()

class Book(_BOOK_REPO_BASE):
    __tablename__ = "book"
    title = Column(VARCHAR(100))
    isbn = Column(VARCHAR(50), primary_key=True)
    pages = Column(Integer)
    price = Column(Float)
    description = Column(VARCHAR(256))
    publisher = Column(VARCHAR(100))

    def __repr__(self) -> str:

        return f"Title: {self.title}, isbn: {self.isbn}, pages: {self.pages}, price: {self.price}, description: {self.description}, publisher: {self.publisher}"

class Chapter(_BOOK_REPO_BASE):
    __tablename__ = "chapter"
    
    # {TODO} how do define two primary keys
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    title = Column(VARCHAR(50))
    book_isbn = Column(VARCHAR(50), ForeignKey('book.isbn'))

class Page(_BOOK_REPO_BASE):
    __tablename__ = "page"

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey('chapter.id'))
    content = Column(Text)
    header = Column(VARCHAR(20))
    footer = Column(VARCHAR(20))

class Author(_BOOK_REPO_BASE):
    __tablename__ = "author"
    name = Column(VARCHAR(50))
    bio = Column(VARCHAR(100))
    email = Column(VARCHAR(20), primary_key=True)

"""
    When we take a look between books and author, a book can have many authors and an author can have many books.

    These two tables are so called many-to-many realtionship.

    Therefore we need a third table, join table, to manage these two tables.
"""

class BooksAuthor(_BOOK_REPO_BASE):
    __tablename__ = "books_authors"
    book_isbn = Column(VARCHAR(50), ForeignKey('book.isbn'), primary_key=True)
    author_email = Column(VARCHAR(20), ForeignKey('author.email'), primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('book_isbn', 'author_email'),
    )

class PopularBooks(_BOOK_REPO_BASE):
    __tablename__ = "popular_books"
    book_title = Column(VARCHAR(100), primary_key=True)
    author_name = Column(VARCHAR(50), primary_key=True)
    number_sold = Column(Integer)
    number_previewed = Column(Integer)

class BookDetails(_BOOK_REPO_BASE):
    __tablename__ = "book_details"
    id = Column(Integer, primary_key=True)
    book_isbn = Column(VARCHAR(50), ForeignKey('book.isbn'), unique=True)
    rating = Column(DECIMAL)
    language = Column(VARCHAR(10))
    keywords = Column(Text)
    date_publish = Column(Date)
