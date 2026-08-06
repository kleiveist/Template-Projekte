from sqlalchemy import text

from app.db.engine import create_database_engine
from app.db.session import create_session_factory


def test_session_factory_creates_working_sessions() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            assert session.scalar(text("SELECT 1")) == 1
    finally:
        engine.dispose()
