"""
database.py

Configures the SQLite database connection for the user-management layer
of the Knowledge Graph Learning Assistant.

This module is intentionally isolated from graph/ and llm/ — it has no
knowledge of Neo4j or Ollama, and nothing in graph/ or llm/ imports from
here. It only exists to support user accounts (auth, profiles, etc.)
via SQLAlchemy + SQLite.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# ---------------------------------------------------------------------------
# Database location
# ---------------------------------------------------------------------------
# The .db file is created in the backend/ root directory (one level up from
# this database/ package), so it sits alongside app.py and config.py rather
# than inside the database/ folder itself.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'knowledge_graph.db')}"

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# check_same_thread=False is required for SQLite when used with FastAPI,
# since FastAPI can handle a request in a different thread than the one
# that created the connection.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
# autocommit=False and autoflush=False are the standard, explicit defaults
# recommended by SQLAlchemy for web applications — commits happen only when
# your CRUD code calls db.commit().
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------
# All ORM models created in the next step (models.py) will inherit from
# this Base so SQLAlchemy can track them for table creation/migrations.
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and guarantees it is
    closed after the request finishes, even if an error occurs.

    Usage in a route (from Step 3+ onward):

        from database.database import get_db
        from sqlalchemy.orm import Session
        from fastapi import Depends

        @app.get("/some-route")
        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()