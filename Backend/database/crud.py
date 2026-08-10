"""
crud.py

Database access functions ("Create, Read, Update, Delete") for the User
model. API routes (Step 6) call into these functions rather than touching
the database.models.User / SQLAlchemy session directly — keeps route
handlers thin and testable.
"""

from typing import Optional

from sqlalchemy.orm import Session

from database.models import User
from database.schemas import UserCreate
from database.auth import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Returns the User if email+password are correct, else None."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user