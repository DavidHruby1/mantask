import secrets

from fastapi import APIRouter, Depends, HTTPException, Response

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.db import get_db
from backend.app.models.app_config import AppConfig
from backend.app.schemas.bootstrap import BootstrapSetup, BootstrapResult
from backend.app.services.bootstrap import bootstrap_application
from backend.app.services.auth import create_user_session


router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])


@router.post("/setup", response_model=BootstrapResult)
def bootstrap_setup(
    input_data: BootstrapSetup, response: Response, db: Session = Depends(get_db)
) -> BootstrapResult:
    is_app_bootstrapped = db.scalar(select(AppConfig.id).limit(1)) is not None
    if is_app_bootstrapped:
        raise HTTPException(status_code=409, detail="App already bootstrapped")

    if not settings.BOOTSTRAP_SECRET:
        raise HTTPException(status_code=403, detail="Bootstrap is not configured")

    if not secrets.compare_digest(
        input_data.bootstrap_secret, settings.BOOTSTRAP_SECRET
    ):
        raise HTTPException(status_code=403, detail="Invalid bootstrap secret")

    try:
        user = bootstrap_application(db, input_data)
        raw_token = create_user_session(db, user_id=user.id)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Bootstrap data conflicts with existing records"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to complete the request right now. Please try again",
        )

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        expires=60 * 60 * 24 * settings.SESSION_EXPIRE_DAYS,
        path="/",
    )

    return BootstrapResult(bootstrapped=True)
