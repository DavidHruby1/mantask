from typing import Self
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator
)


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return str(email).strip().lower()
    

class LoginResult(BaseModel):
    authenticated: bool


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

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        return str(email).strip().lower()

    @model_validator(mode="after")
    def validate_password(self) -> Self:
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self


class RegisterResult(BaseModel):
    registered: bool


class ChangePasswordResult(BaseModel):
    changed: bool


class ResetPasswordResult(BaseModel):
    reset: bool
