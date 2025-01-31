import structlog

from sqlalchemy import (
    event,
    Engine,
    select,
    and_
)

from sqlalchemy.orm import (
    sessionmaker,
    Session
)

from sqlalchemy.dialects.postgresql import insert

from shcemas import (
    _BOOK_REPO_BASE,
    Book,
    Chapter,
    Page,
    Author,
    BookDetails,
    BooksAuthor
)

class BookRepo:
    
    def __init__(self, 
                 logger: structlog.stdlib.BoundLogger,
                 engine: Engine):
        
        # register log handler
        self.logger = logger

        # register session maker
        self.session_maker = sessionmaker(autocommit=False,
                                          autoflush=False,
                                          bind=engine)
        
        # register event listener
        # self.register_event_listener()

    # def register_event_listener(self):

    #     event.listen(target=self.session_maker,
    #                  identifier="before_commit",
    #                  fn=self.before_commit_callback)
    
    # def before_commit_callback(self, session: Session):

    #     if not session.new:
    #         return

    def insert_book(self, book: Book):

        with self.session_maker() as session:
            
            try:
                insert_stmt = (
                    insert(Book).
                    values(title=book.title,
                           isbn=book.isbn,
                           pages=book.pages,
                           price=book.price,
                           description=book.description,
                           publisher=book.publisher
                    )
                )

                upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[Book.isbn]
                )

                session.execute(upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[BookRepo][insert_book] Failed to insert book: {}".format(err))
                session.rollback()

    def insert_chapter(self, chapter: Chapter):

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(Chapter).
                    values(id=chapter.id,
                           number=chapter.number,
                           title=chapter.title,
                           book_isbn=chapter.book_isbn)
                )

                upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[Chapter.id]
                )

                session.execute(upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[BookRepo][insert_chapter] Failed to insert chapter: {}".format(err))
                session.rollback()

    def insert_page(self, page: Page):

        with self.session_maker() as session:
            
            try:
                insert_stmt = (
                    insert(Page).
                    values(id=page.id,
                           chapter_id=page.chapter_id,
                           content=page.content,
                           header=page.header,
                           footer=page.footer)
                )

                upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[Page.id]
                )

                session.execute(upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[BookRepo][insert_page] Failed to insert page: {}".format(err))
                session.rollback()

    def insert_author(self, author: Author):

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(Author).
                    values(name=author.name,
                           bio=author.bio,
                           email=author.email)
                )

                upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[Author.email]
                )

                session.execute(upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[BookRepo][insert_chapter] Failed to insert chapter: {}".format(err))
                session.rollback()

    def insert_books_authors(self, books_authors: BooksAuthor):
        
        with self.session_maker() as session:

            try:
                
                insert_stmt = (
                    insert(BooksAuthor).
                    values(book_isbn=books_authors.book_isbn,
                           author_email=books_authors.author_email)
                )

                upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[BooksAuthor.book_isbn, BooksAuthor.author_email]
                )

                session.execute(upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[BookRepo][insert_books_authors] Failed to insert books authors: {}".format(err))
                session.rollback()

    def insert_book_details(self, detail: BookDetails):

        with self.session_maker() as session:

            try:
                insert_stmt = (
                    insert(BookDetails).
                    values(id=detail.id,
                           book_isbn=detail.book_isbn,
                           rating=detail.rating,
                           language=detail.language,
                           keywords=detail.keywords,
                           date_publish=detail.date_publish)
                )

                upsert_stmt = insert_stmt.on_conflict_do_nothing(
                    index_elements=[BookDetails.id]
                )

                session.execute(upsert_stmt)
                session.commit()

            except Exception as err:
                self.logger.error("[BookRepo][insert_book_details] Failed to insert book details: {}".format(err))
                session.rollback()

    def fetch_books(self):

        with self.session_maker() as session:

            try:
                books = session.query(Book).all()
                for book in books:
                    self.logger.info(book)
            except Exception as err:
                self.logger.error("[BookRepo][fetch_books] Failed to fetch books: {}".format(err))
                session.rollback()

    def fetch_book_with_title(self, title: str):

        with self.session_maker() as session:

            try:
                book = session.query(Book).where(Book.title == title).all()
                self.logger.info(book)
            except Exception as err:
                self.logger.error("[BookRepo][fetch_books] Failed to fetch books with title: {}".format(err))
                session.rollback()
            
    def fetch_book_with_isbn(self, isbn: str):

        with self.session_maker() as session:

            try:
                book = session.query(Book).where(Book.isbn == isbn).all()
                self.logger.info(book)
            except Exception as err:
                self.logger.error("[BookRepo][fetch_books] Failed to fetch books with isbn: {}".format(err))
                session.rollback()
    
    def fetch_book_primary_key(self):

        return [key.name for key in Book.__table__.primary_key]
    
    def fetch_books_detail(self):

        with self.session_maker() as session:

            try:
                stmt = (
                    select(Book.title, 
                           Book.price,
                           BookDetails.language,
                           BookDetails.rating)
                    .join(BookDetails, Book.isbn == BookDetails.book_isbn)
                    .cte('books_details')
                )

                books_detail = session.query(stmt).all()
                self.logger.info(books_detail)

            except Exception as err:
                self.logger.error("[BookRepo][fetch_books_detail] Failed to fetch books detail: {}".format(err))
                session.rollback()

    def fetch_books(self):

        with self.session_maker() as session:

            try:
                stmt = (
                    select(Book.title, 
                           Chapter.title,
                           Page.content)
                    .join(Chapter, Book.isbn == Chapter.book_isbn)
                    .join(Page, Chapter.id == Page.chapter_id)
                    .cte('books')
                )

                books = session.query(stmt).all()
                self.logger.info(books)

            except Exception as err:
                self.logger.error("[BookRepo][fetch_books_info] Failed to fetch books: {}".format(err))
                session.rollback()

    def fetch_books_author(self):

        with self.session_maker() as sesion:

            try:
                stmt = (
                    select(Book.title,
                           Author.email,
                           Book.description)
                    .where(and_(Book.isbn == BooksAuthor.book_isbn,
                                Author.email == BooksAuthor.author_email))
                    .cte('books_author')
                )

                result = sesion.query(stmt).all()

                self.logger.info(result)

            except Exception as err:
                self.logger.error("[BookRepo][fetch_books_info] Failed to fetch books_author: {}".format(err))
                sesion.rollback()

    def fetch_authors_book(self):

        with self.session_maker() as sesion:

            try:
                stmt = (
                    select(Author.name,
                           Author.email,
                           Book.title)
                    .where(and_(Book.isbn == BooksAuthor.book_isbn,
                                Author.email == BooksAuthor.author_email))
                    .cte('authors_book')
                )

                result = sesion.query(stmt).all()

                self.logger.info(result)

            except Exception as err:
                self.logger.error("[BookRepo][fetch_authors_book] Failed to fetch books_author: {}".format(err))
                sesion.rollback()


def setup_book_repo(logger: structlog.stdlib.BoundLogger, engine: Engine) -> BookRepo:

    _BOOK_REPO_BASE.metadata.create_all(engine)

    book_repo = BookRepo(logger=logger, engine=engine)

    return book_repo

if __name__ == "__main__":

    from settings.settings import learning_postgres_settings
    from database.postgres import connect_to_postgres

    pg_engine = connect_to_postgres(
        host=learning_postgres_settings.host,
        port=learning_postgres_settings.port,
        db_name=learning_postgres_settings.db_name,
        user=learning_postgres_settings.user,
        password=learning_postgres_settings.password
    )

    logger = structlog.get_logger()

    book_repo = setup_book_repo(logger=logger,
                                engine=pg_engine)
    
    book_repo.insert_book(Book(title="Postgres Made Easy",
                               isbn="0-5980-6249-1",
                               pages=30,
                               price=9.99,
                               description="A great book for beginners to learn how to manage PostgreSQL",
                               publisher="Codecademy Press"))

    book_repo.insert_book(Book(title="Postgres for Beginners",
                               isbn="0-5980-6249-1",
                               pages=25,
                               price=4.99,
                               description="Learn Postgres the Easy Way",
                               publisher="Codecademy Publishing"))
    
    # fetch with title we obtain one book
    book_repo.fetch_book_with_title(title="Postgres for Beginners")
    
    # fetch with isbn we obtain two books
    book_repo.fetch_book_with_isbn(isbn="0-5980-6249-1")

    # book_repo.insert_chapter(Chapter(id=1,
    #                                  number=1,
    #                                  title="Introduction",
    #                                  content="<h1>Introduction</h1> <p>Welcome! In this lesson, you will learn what a database schema is and how to create one with PostgreSQL. PostgreSQL is a popular database management system that stores information on a dedicated database server instead of on a local file system. The benefits of using a database system include better organization of related information, more efficient storage and faster retrieval.</p>"))

    # book_repo.insert_chapter(Chapter(id=1,
    #                                  number=2,
    #                                  title="Database Schema",
    #                                  content="<h1>What is Database Schema?</h1> <p>Like an architectural blueprint, a database schema is documentation that helps its audience such as a database designer, administrator and other users interact with a database. It gives an overview of the purpose of the database along with the data that makes up the database, how the data is organized into tables, how the tables are internally structured and how they are externally related to one another.</p>"))
    
    book_repo.insert_author(Author(name="Kim Index",
                                   bio="Kim has been a professional database designer for 20 years",
                                   email="ki@cp.com"))
    
    book_repo.insert_book(Book(title="Learn PostgreSQL",
                               isbn="123457890",
                               pages=100,
                               price=2.99,
                               description="Great course",
                               publisher="Codecademy"))

    book_repo.insert_book_details(BookDetails(id=1,
                                              book_isbn="123457890",
                                              rating=3.95,
                                              language="French",
                                              keywords="{sql, postgresql, database}",
                                              date_publish="2020-05-20"))
    
    book_repo.fetch_books_detail()


    # inser books/chapter/pages
    book_repo.insert_book(Book(title="Learn PostgreSQL",
                               isbn="0-9673-4537-5",
                               pages=100,
                               price=2.99,
                               description="Dive into Postgres for Beginners",
                               publisher="Codecademy Publishing"))
    
    book_repo.insert_book(Book(title="Postgres Made Easy",
                               isbn="0-3414-4116-3",
                               pages=255,
                               price=5.99,
                               description="Learn Postgres the Easy Way",
                               publisher="Codecademy Press"))
    
    book_repo.insert_chapter(Chapter(id=1,
                                     number=1,
                                     title="Chapter 1",
                                     book_isbn="0-9673-4537-5"))

    book_repo.insert_chapter(Chapter(id=2,
                                     number=1,
                                     title="Chapter 1",
                                     book_isbn="0-3414-4116-3"))

    book_repo.insert_page(Page(id=1,
                               chapter_id=1,
                               content="Chapter 1 Page 1",
                               header="Page 1 Header",
                               footer="Page 1 Footer"))
    
    book_repo.insert_page(Page(id=2,
                               chapter_id=1,
                               content="Chapter 1 Page 2",
                               header="Page 2 Header",
                               footer="Page 2 Footer")) 
      
    book_repo.insert_page(Page(id=3,
                               chapter_id=1,
                               content="Chapter 1 Page 3",
                               header="Page 3 Header",
                               footer="Page 3 Footer"))   

    book_repo.insert_page(Page(id=4,
                               chapter_id=1,
                               content="Chapter 1 Page 4",
                               header="Page 4 Header",
                               footer="Page 4 Footer"))   

    book_repo.fetch_books()

    book_repo.insert_book(Book(title="Learn PostgreSQL Volume 2",
                               isbn="987654321",
                               pages=200,
                               price=3.99,
                               description="Manage database part two",
                               publisher="Codecademy"))


    book_repo.insert_author(Author(name="James Key",
                                   bio="Guru in database management with PostgreSQL",
                                   email="jkey@db.com"))

    book_repo.insert_author(Author(name="Clara Index",
                                   bio="Guru in database management with PostgreSQL",
                                   email="cindex@db.com"))
    
    book_repo.insert_books_authors(BooksAuthor(book_isbn="123457890",
                                               author_email="jkey@db.com"))

    book_repo.insert_books_authors(BooksAuthor(book_isbn="123457890",
                                               author_email="cindex@db.com"))
    
    book_repo.insert_books_authors(BooksAuthor(book_isbn="987654321",
                                               author_email="cindex@db.com"))
    
    
    book_repo.fetch_books_author()
    book_repo.fetch_authors_book()