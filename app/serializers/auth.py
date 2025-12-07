from enum import Enum
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class RegisterRole(str, Enum):
    student = "student"
    tutor = "tutor"

def _not_blank(v: str, field_name: str) -> str:
    if v is None:
        raise ValueError(f"{field_name} est requis")
    v2 = v.strip()
    if not v2:
        raise ValueError(f"{field_name} ne peut pas être vide")
    return v2

class Login(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def _pwd_required(cls, v: str) -> str:
        v2 = _not_blank(v, "password")
        if len(v2) < 4:
            raise ValueError("password doit contenir au moins 4 caractères")
        return v2

class Register(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: RegisterRole

    # Nettoyage/validation stricte
    @field_validator("password")
    @classmethod
    def _pwd_valid(cls, v: str) -> str:
        v2 = _not_blank(v, "password")
        if len(v2) < 4:
            raise ValueError("password doit contenir au moins 4 caractères")
        return v2

    @field_validator("first_name")
    @classmethod
    def _first_not_blank(cls, v: str) -> str:
        return _not_blank(v, "first_name")

    @field_validator("last_name")
    @classmethod
    def _last_not_blank(cls, v: str) -> str:
        return _not_blank(v, "last_name")

class AuthToken(BaseModel):
    access_token: str

class Me(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: RegisterRole
