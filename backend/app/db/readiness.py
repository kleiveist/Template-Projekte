from __future__ import annotations

from sqlalchemy import text

from app.db.engine import get_database_engine


def database_ready() -> bool:
    """Probe the configured database and fail closed without leaking driver details."""
    try:
        with get_database_engine().connect() as connection:
            return connection.scalar(text("SELECT 1")) == 1
    except Exception:  # Infrastructure health checks intentionally collapse driver-specific failures.
        return False
