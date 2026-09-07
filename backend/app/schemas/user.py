from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    profile_picture_path: str | None
    last_active_team_id: int | None
    created_at: datetime
    updated_at: datetime
