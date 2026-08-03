"""Auth routes: register, login, logout, me."""

import uuid
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.models.models import User, Session
from app.auth.auth import hash_password, verify_password, generate_session_token, session_expiry
from app.auth.dependencies import get_current_user
from app.schemas.schemas import ApiMeta, ApiResponse, ApiError, ApiErrorResponse

router = APIRouter(prefix="/api/v1/auth")


def get_meta(request: Request) -> ApiMeta:
    return ApiMeta(request_id=getattr(request.state, "request_id", str(uuid.uuid4())))


# ============================================================
# SCHEMAS
# ============================================================
class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    user: AuthUserResponse


class MeResponse(BaseModel):
    user: AuthUserResponse


# ============================================================
# REGISTER
# ============================================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Validate email format
    if "@" not in body.email or "." not in body.email.split("@")[-1]:
        raise HTTPException(
            status_code=422,
            detail=ApiErrorResponse(
                error=ApiError(code="INVALID_EMAIL", message="Please provide a valid email address.", details={}, retryable=False),
                meta=get_meta(request),
            ).model_dump(),
        )

    # Validate password length
    if len(body.password) < 8:
        raise HTTPException(
            status_code=422,
            detail=ApiErrorResponse(
                error=ApiError(code="WEAK_PASSWORD", message="Password must be at least 8 characters.", details={}, retryable=False),
                meta=get_meta(request),
            ).model_dump(),
        )

    # Check for existing user
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ApiErrorResponse(
                error=ApiError(code="EMAIL_TAKEN", message="An account with this email already exists.", details={}, retryable=False),
                meta=get_meta(request),
            ).model_dump(),
        )

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        display_name=body.display_name,
        password_hash=hash_password(body.password),
        role="owner",
        is_active=True,
    )
    db.add(user)
    await db.flush()

    # Create session
    token = generate_session_token()
    session = Session(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=token,
        expires_at=session_expiry(),
        is_active=True,
    )
    db.add(session)
    await db.commit()

    return ApiResponse(
        data=LoginResponse(
            token=token,
            user=AuthUserResponse(
                id=user.id, email=user.email, display_name=user.display_name,
                role=user.role, is_active=user.is_active,
                created_at=user.created_at.isoformat(),
            ),
        ),
        meta=get_meta(request),
    )


# ============================================================
# LOGIN
# ============================================================
@router.post("/login")
async def login(request: Request, body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ApiErrorResponse(
                error=ApiError(code="INVALID_CREDENTIALS", message="Invalid email or password.", details={}, retryable=False),
                meta=get_meta(request),
            ).model_dump(),
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ApiErrorResponse(
                error=ApiError(code="USER_DISABLED", message="This account has been disabled.", details={}, retryable=False),
                meta=get_meta(request),
            ).model_dump(),
        )

    # Create session
    token = generate_session_token()
    session = Session(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token=token,
        expires_at=session_expiry(),
        is_active=True,
    )
    db.add(session)
    await db.commit()

    return ApiResponse(
        data=LoginResponse(
            token=token,
            user=AuthUserResponse(
                id=user.id, email=user.email, display_name=user.display_name,
                role=user.role, is_active=user.is_active,
                created_at=user.created_at.isoformat(),
            ),
        ),
        meta=get_meta(request),
    )


# ============================================================
# LOGOUT
# ============================================================
@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke the current session token."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[len("Bearer "):] if auth_header.startswith("Bearer ") else ""

    result = await db.execute(select(Session).where(Session.token == token, Session.user_id == current_user.id))
    session = result.scalar_one_or_none()
    if session:
        session.is_active = False
        await db.commit()

    return ApiResponse(data={"message": "Signed out successfully."}, meta=get_meta(request))


# ============================================================
# ME (current user)
# ============================================================
@router.get("/me")
async def me(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return ApiResponse(
        data=AuthUserResponse(
            id=current_user.id, email=current_user.email,
            display_name=current_user.display_name,
            role=current_user.role, is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
        ),
        meta=get_meta(request),
    )