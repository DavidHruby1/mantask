from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator
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


class ChangePasswordResult(BaseModel):
    changed: bool


class ResetPasswordResult(BaseModel):
    reset: bool
