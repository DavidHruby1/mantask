from fastapi import (
    APIRouter,
    Depends
)
from sqlalchemy.orm import (
    Session,
    select,
)

from backend.app.models.app_config import AppConfig
from backend.app.schemas.bootstrap import (
    BootstrapSetupInput, 
    BootstrapSetupResult, 
    BootstrapStatus
)
from backend.app.core.db import get_db


router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])


@router.get("/status", response_model=BootstrapStatus)
def get_bootstrap_status(db: Session = Depends(get_db)) -> BootstrapStatus:
    """
    Check if the application has been bootstrapped (if config singleton exists).
    """
    is_app_bootstrapped = db.scalar(select(AppConfig.id).limit(1)) is not None
    return BootstrapStatus(is_bootstrapped=is_app_bootstrapped)


@router.post("/setup", response_model=BootstrapSetupResult)
def bootstrap_setup(input: BootstrapSetupInput):
    """
    Perform the bootstrap setup by creating the initial user, organization and team.
    This endpoint should only be accessible if the application is not yet bootstrapped.
    """
    return BootstrapSetupResult()