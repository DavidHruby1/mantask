import re
from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    field_validator
)


NAME_REGEX = re.compile(r"^[a-zA-Z0-9\-_: ]+$")


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        if name.strip() == "":
            raise ValueError("Team name cannot be empty or whitespace")
        if not NAME_REGEX.fullmatch(name):
            raise ValueError("Team name can only contain letters, numbers, spaces and -_:")
        return name.strip()


class TeamUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str| None:
        if name is None:
            return None
        if name.strip() == "":
            raise ValueError("Team name cannot be empty or whitespace")
        if not NAME_REGEX.fullmatch(name):
            raise ValueError("Team name can only contain letters, numbers, spaces and -_:")
        return name.strip()


class TeamRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool