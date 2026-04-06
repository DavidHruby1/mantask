from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

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
def bootstrap_setup(
    input_data: BootstrapSetupInput,
    db: Session = Depends(get_db),
) -> BootstrapSetupResult:
    """
    Perform the bootstrap setup by creating the initial user, organization and team.
    This endpoint should only be accessible if the application is not yet bootstrapped.
    """
    return BootstrapSetupResult(authenticated=True)



"""
BOOTSTRAP FLOW
1. GET /bootstrap/status
2. If is_bootstrapped == true:
   - frontend should go to normal auth/app flow
   - if user already has session, GET /dashboard
   - if not, go to login
3. If is_bootstrapped == false:
   - show bootstrap form
   - submit POST /bootstrap/setup
POST /bootstrap/setup:
1. Validate payload via BootstrapSetupInput
2. Backend checks app is still not bootstrapped
3. Call services/bootstrap.py
4. In service:
   - wrap transaction in try/except
   - create AppConfig
   - create User
   - create Team
   - create TeamMember
   - create Session
   - commit
5. If another request won the race first:
   - DB constraint fails
   - catch IntegrityError
   - rollback
   - return 409 already bootstrapped
6. If success:
   - endpoint sets auth cookie from created session token
   - return authenticated=True
"""
