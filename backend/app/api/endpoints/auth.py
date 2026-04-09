from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.db import get_db
from backend.app.schemas.auth import (
    LoginInput,
    LoginResult,
)
from backend.app.core.config import settings
from backend.app.services.auth import (
    authenticate_user,
    create_user_session,
    get_user_session_by_token,
    is_user_session_valid,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResult)
def login(
    input_data: LoginInput, response: Response, db: Session = Depends(get_db)
) -> LoginResult:
    user = authenticate_user(db, input_data.email, input_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")

    try:
        raw_token = create_user_session(db, user_id=user.id)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the request right now. Please try again.",
        )

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.SESSION_EXPIRE_DAYS,
        path="/",
    )

    return LoginResult(authenticated=True)


@router.get("/me", response_model=LoginResult)
def auth_user(
    request: Request, db: Session = Depends(get_db)
) -> LoginResult | JSONResponse:
    cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = get_user_session_by_token(db, cookie)
    if not session or not session.user.is_active or not is_user_session_valid(session):
        unauthorized = JSONResponse(
            status_code=401,
            content={"detail": "Not authenticated"},
        )
        unauthorized.delete_cookie(settings.SESSION_COOKIE_NAME)
        return unauthorized

    return LoginResult(authenticated=True)


@router.post("/logout", response_model=LoginResult)
def logout(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> LoginResult:
    cookie = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not cookie:
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
        return LoginResult(authenticated=False)

    session = get_user_session_by_token(db, cookie)
    if not session or not is_user_session_valid(session):
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
        return LoginResult(authenticated=False)

    now = datetime.now(timezone.utc)
    try:
        session.revoked_at = now
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to log out")

    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    return LoginResult(authenticated=False)


# Not in MVP scope for now
"""
@router.post("/register", response_model=RegisterResult)
def register():
    pass

@router.post("/change-password", response_model=ChangePasswordResult)
def change_password():
    pass


@router.post("/reset-password", response_model=ResetPasswordResult)
def reset_password():
    pass
"""
