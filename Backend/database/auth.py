"""
auth.py

Password hashing and JWT handling for the user-management layer.

Deliberately imports database.models directly (not database.crud) to avoid
a circular import: crud.py will import hash_password from this file, so
this file must not import crud.py back.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import User

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
try:
    from config import (
        JWT_SECRET_KEY as SECRET_KEY,
        JWT_ALGORITHM as ALGORITHM,
        ACCESS_TOKEN_EXPIRE_MINUTES,
    )
except ImportError:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "knowledge_graph_secret_key_change_this")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

# tokenUrl tells FastAPI's auto-docs (Swagger UI) which endpoint issues
# tokens — it must match the login route path we'll add in Step 6.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: decodes the bearer token and loads the matching
    User row. Use this to protect any future route, e.g.:

        @app.get("/some-protected-route")
        def route(current_user: User = Depends(get_current_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user