from sqlalchemy import (
    Engine,
    create_engine,
    text
)

from sqlalchemy_utils import (
    create_database,
    database_exists
)

def _execute(engine: Engine, sql: str, raise_error: bool = True):

    with engine.connect() as conn:
        try:
            conn.execute(text(sql))
            conn.commit()
        except Exception as e:
            if 'psycopg2.errors.DuplicateColumn' in str(e):
                return

            if raise_error:
                raise e

def connect_to_postgres(
    host: str,
    port: int,
    db_name: str = "test_db",
    user: str = "root",
    password: str = "root") -> Engine:

    engine = create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{db_name}",
        pool_size=10
    )

    if not database_exists(engine.url):
        create_database(engine.url)

    _execute(engine=engine, sql=f"ALTER DATABASE \"{db_name}\" SET timezone TO 'Asia/Taipei';")

    return engine