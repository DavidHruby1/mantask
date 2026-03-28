import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
)


PASSWORD_REGEX = re.compile(r'^[A-Za-z0-9\-_:!@#$%^&*()\[\]{};<>?/\\|~\."+\',`]+$')
NAME_REGEX = re.compile(r"^[a-zA-Z0-9\-_: ]+$")


class BootstrapStatus(BaseModel):
    is_bootstrapped: bool


class BootstrapSetupInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50) # normalized_username will be on the backend
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    organization_name: str = Field(..., min_length=1, max_length=100)
    team_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        username = username.strip()
        if username == "":
            raise ValueError("Username cannot be empty or whitespace")
        if any(char.isspace() for char in username):
            raise ValueError("There can be no whitespace in username")
        return username

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return str(email).strip().lower()

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
        if name.strip() == "":
            raise ValueError("Organization and team names cannot be empty or whitespace")
        if not NAME_REGEX.fullmatch(name):
            raise ValueError("Organization and team names can only contain letters, numbers, spaces and -_:")
        return name.strip()


class BootstrapSetupResult(BaseModel):
    redirect_to: str