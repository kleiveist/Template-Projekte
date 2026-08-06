"""Optional SQL database infrastructure for backend-enabled projects."""

from app.db.base import Base
from app.db.config import DatabaseConfigurationError, DatabaseSettings, load_database_settings
from app.db.engine import create_database_engine, dispose_database_engine, get_database_engine
from app.db.session import create_session_factory, get_db_session

__all__ = [
    "Base",
    "DatabaseConfigurationError",
    "DatabaseSettings",
    "create_database_engine",
    "create_session_factory",
    "dispose_database_engine",
    "get_database_engine",
    "get_db_session",
    "load_database_settings",
]
