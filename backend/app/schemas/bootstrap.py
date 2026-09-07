import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


PASSWORD_REGEX = re.compile(r'^[A-Za-z0-9\-_:!@#$%^&*()\[\]{};<>?/\\|~\."+\',`=]+$')
NAME_REGEX = re.compile(r"^[\w\-:,. ]+$")


class BootstrapSetup(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr # No need to normalize, EmailStr already strips and lowercases
    password: str = Field(..., min_length=8, max_length=128)
    organization_name: str = Field(..., min_length=1, max_length=100)
    team_name: str = Field(..., min_length=1, max_length=100)
    bootstrap_secret: str = Field(..., min_length=32, max_length=256)

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        username = username.strip()
        if username == "":
            raise ValueError("Username cannot be empty or whitespace")
        if any(char.isspace() for char in username):
            raise ValueError("There can be no whitespace in username")
        return username

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if any(char.isspace() for char in password):
            raise ValueError("There can be no whitespace in password")
        if not PASSWORD_REGEX.fullmatch(password):
            raise ValueError("Password contains invalid characters")
        return password

    @field_validator("organization_name", "team_name")
    @classmethod
    def validate_names(cls, name: str) -> str:
        name = name.strip()
        if name == "":
            raise ValueError("Organization and team names cannot be empty or whitespace")
        if not NAME_REGEX.fullmatch(name):
            raise ValueError("Organization and team names can only contain letters, numbers, spaces and -_:")
        return name


class BootstrapResult(BaseModel):
    bootstrapped: bool
    active_team_id: int | None = None


class BootstrapStatus(BaseModel):
    bootstrapped: bool
