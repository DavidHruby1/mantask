from fastapi import APIRouter, Response, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from backend.app.api.dependencies import (
    SessionTokenDep,
    DbSessionDep,
    CurrentSessionDep,
)
from backend.app.core.config import settings
from backend.app.schemas.auth import LoginInput, LoginResult
from backend.app.services.auth import (
    LoginService,
    SessionAuthService,
    ensure_active_team_id,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResult)
def login(
    db: DbSessionDep, 
    input_data: LoginInput, 
    response: Response
) -> LoginResult:
    login_service = LoginService(db)
    user = login_service.authenticate_user(input_data.email, input_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")

    try:
        session_token = login_service.create_session(user_id=user.id)
        active_team_id = ensure_active_team_id(db, user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the request right now. Please try again.",
        )

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.SESSION_EXPIRE_DAYS,
        path="/",
    )

    return LoginResult(
        authenticated=True,
        active_team_id=active_team_id,
        session_token=session_token,
    )


@router.get("/me", response_model=LoginResult)
def auth_user(
    db: DbSessionDep, session: CurrentSessionDep
) -> LoginResult:
    try:
        active_team_id = ensure_active_team_id(db, session.user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the request right now. Please try again.",
        )

    return LoginResult(authenticated=True, active_team_id=active_team_id)


@router.post("/logout", response_model=LoginResult)
def logout(
    db: DbSessionDep, 
    session_token: SessionTokenDep, 
    response: Response
) -> LoginResult:
    if not session_token:
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
        return LoginResult(authenticated=False)

    session_auth_service = SessionAuthService(db)
    revoked = session_auth_service.revoke_session_by_token(session_token)
    if not revoked:
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
        return LoginResult(authenticated=False)

    try:
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
