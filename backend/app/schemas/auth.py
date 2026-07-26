import re
from typing import Self
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


PASSWORD_REGEX = re.compile(r'^[A-Za-z0-9\-_:!@#$%^&*()\[\]{};<>?/\\|~\."+\',`=]+$')


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    

class LoginResult(BaseModel):
    authenticated: bool
    active_team_id: int | None = None
    session_token: str | None = None


class RegisterInput(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    password_confirmation: str = Field(..., min_length=8, max_length=128)

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

    @model_validator(mode="after")
    def validate_passwords_match(self) -> Self:
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self


class RegisterResult(BaseModel):
    registered: bool


class ChangePasswordResult(BaseModel):
    changed: bool


class ResetPasswordResult(BaseModel):
    reset: bool
