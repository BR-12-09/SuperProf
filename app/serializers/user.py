from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    tutor = "tutor"

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole = UserRole.student
    postal_code: str | None = None

class UserOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    postal_code: str | None = None
    department: str | None = None

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    first_name: str
    last_name: str
    email: str
    role: str
    department: str | None = None