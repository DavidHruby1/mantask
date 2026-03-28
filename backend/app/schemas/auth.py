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
    success: bool
    redirect_to: str