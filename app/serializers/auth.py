# from pydantic import BaseModel, EmailStr

# class Login(BaseModel):
#     email: EmailStr
#     password: str

# class AuthToken(BaseModel):
#     access_token: str

from pydantic import BaseModel, EmailStr, ConfigDict
from enum import Enum

class Login(BaseModel):
    email: EmailStr
    password: str

class RegisterRole(str, Enum):
    student = "student"
    tutor = "tutor"

class Register(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: RegisterRole

class AuthToken(BaseModel):
    access_token: str

class Me(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: RegisterRole

