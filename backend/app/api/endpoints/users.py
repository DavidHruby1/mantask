from fastapi import APIRouter

from backend.app.api.dependencies import CurrentSessionDep, DbSessionDep
from backend.app.error import NotAuthenticatedError
from backend.app.repositories.users import get_user_by_id
from backend.app.schemas.user import UserRead


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_current_user(
    db: DbSessionDep, session: CurrentSessionDep
) -> UserRead:
    user = get_user_by_id(db, session.user_id)
    if user is None:
        raise NotAuthenticatedError()
    return UserRead.model_validate(user)
