"""Password hashing, token generation, and session management."""

import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_session_token() -> str:
    """Generate a cryptographically secure session token."""
    return secrets.token_urlsafe(48)


def session_expiry(days: int = 30) -> datetime:
    """Return offset-naive UTC datetime for session expiry."""
    return (datetime.now(timezone.utc) + timedelta(days=days)).replace(tzinfo=None)