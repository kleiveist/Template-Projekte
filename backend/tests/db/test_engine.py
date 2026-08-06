from sqlalchemy import text

from app.db.engine import create_database_engine


def test_create_database_engine_is_lazy_and_usable() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT 1")) == 1
    finally:
        engine.dispose()
