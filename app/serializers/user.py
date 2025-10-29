# app/serializers/user.py
from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    student = "student"
    tutor = "tutor"

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole = UserRole.student  # <-- ajouté

    class Config:
        from_attributes = True


class UserOutput(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole  # <-- ajouté
    class Config:
        from_attributes = True
