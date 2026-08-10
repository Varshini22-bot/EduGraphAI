"""
schemas.py

Pydantic schemas — the request/response contracts for the user-management
API. These are separate from database/models.py (which defines the actual
SQL table) so the API shape can evolve independently of the DB schema.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Payload for POST /auth/register"""
    password: str


class UserResponse(UserBase):
    """What we return to the client — never includes the password/hash."""
    id: int
    is_active: bool
    created_at: datetime

    # Pydantic v2: allows building this schema directly from a SQLAlchemy
    # model instance (db_user), e.g. UserResponse.model_validate(db_user).
    # If your environment uses Pydantic v1 instead, replace this line with:
    #     class Config:
    #         orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Response for POST /auth/login"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Internal shape decoded out of a JWT — not exposed via any route."""
    email: Optional[str] = None