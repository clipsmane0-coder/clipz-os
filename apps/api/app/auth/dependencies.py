"""Auth dependencies — FastAPI dependency injection for protected routes."""

from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import User, Session
from datetime import datetime, timezone


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract the authenticated user from the Authorization header.

    Expects: Authorization: Bearer <session_token>
    Returns: User
    Raises: 401 if missing, invalid, or expired.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Missing or invalid Authorization header. Use: Bearer <token>",
                    "details": {},
                    "retryable": False,
                },
                "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
            },
        )

    token = auth_header[len("Bearer "):]

    # Fetch session with eager-loaded user
    result = await db.execute(
        select(Session).where(Session.token == token, Session.is_active == True)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_SESSION",
                    "message": "Session not found or has been revoked.",
                    "details": {},
                    "retryable": False,
                },
                "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
            },
        )

    if session.expires_at and session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "SESSION_EXPIRED",
                    "message": "Session has expired. Please sign in again.",
                    "details": {},
                    "retryable": True,
                },
                "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
            },
        )

    user = await db.get(User, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "USER_DISABLED",
                    "message": "User account is disabled or not found.",
                    "details": {},
                    "retryable": False,
                },
                "meta": {"request_id": getattr(request.state, "request_id", "unknown")},
            },
        )

    return user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Like get_current_user but returns None instead of raising on missing auth."""
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None