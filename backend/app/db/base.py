from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative root for models added by a derived project."""
