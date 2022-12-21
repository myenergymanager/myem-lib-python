"""DbSettingsMixin."""
import os
from datetime import datetime
from typing import Any

from sqlalchemy import Column, create_engine, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


class Base:
    """Base model class for resources."""

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


DeclarativeBase = declarative_base(cls=Base)


engine_options = {
        "pool_pre_ping": True,
        "connect_args": {
            "connect_timeout": 31536000,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    }


class DbSettingsMixin:
    """Db settings mixin."""

    db_uri: str = (
        f"postgresql+psycopg2://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"
    )

    engine = create_engine(
        db_uri,
        connect_args={
            "connect_timeout": 31536000,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
        pool_pre_ping=True,
    )
    session_maker = sessionmaker(bind=engine)

    @classmethod
    def get_db(cls) -> Any:
        """Get database instance."""
        db = cls.session_maker()
        try:
            yield db
        finally:
            db.close()
