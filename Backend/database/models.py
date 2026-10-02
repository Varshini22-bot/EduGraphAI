"""
models.py

SQLAlchemy ORM models for the user-management layer of the Knowledge Graph
Learning Assistant.

This file only defines the database schema (tables). It does not create
tables on import — that happens explicitly via Base.metadata.create_all(),
which we will trigger in a later step (either in app.py's startup, or a
small init script) so this stays predictable and testable in isolation.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    """
    Represents a registered user of the Knowledge Graph Learning Assistant.

    Password storage: `hashed_password` stores a bcrypt hash only — the
    hashing itself will be implemented in auth.py (Step 5), not here.
    This model just defines the column.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class SharedConversation(Base):
    """
    Stores shared conversation snapshots so links are short (e.g., /share/s_a8f9c2d1)
    and full messages are preserved without URL truncation.
    """
    __tablename__ = "shared_conversations"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    messages_json = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<SharedConversation id={self.id} title={self.title}>"