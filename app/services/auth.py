import base64
import hashlib
import hmac
import os
from typing import Optional

import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.exceptions.user import UserAlreadyExists, UserNotFound, IncorrectPassword

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "should-be-an-environment-variable")
JWT_SECRET_ALGORITHM = os.getenv("JWT_SECRET_ALGORITHM", "HS256")

# ---- Password hashing (PBKDF2-HMAC-SHA256) ----

def hash_password(password: str, iterations: int = 600_000) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"

def check_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_b64, hash_b64 = stored_hash.split("$")
        assert algorithm == "pbkdf2_sha256"
    except Exception:
        raise ValueError("Invalid hash format")
    iterations = int(iterations)
    salt = base64.b64decode(salt_b64)
    stored_dk = base64.b64decode(hash_b64)
    new_dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return hmac.compare_digest(stored_dk, new_dk)

# ---- JWT ----

def _encode_jwt(user_id: str) -> str:
    return jwt.encode({"user_id": user_id}, JWT_SECRET_KEY, algorithm=JWT_SECRET_ALGORITHM)

def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_SECRET_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as err:
        raise HTTPException(status_code=401, detail=f"Invalid token: '{err}'")

# def generate_access_token(db: Session, email: str, password: str) -> str:
#     user: Optional[User] = db.query(User).filter(User.email == email).first()
#     if not user or not user.hashed_password:
#         raise UserNotFound("User not found")
#     if not check_password(password, user.hashed_password):
#         raise IncorrectPassword("Incorrect password")
#     return _encode_jwt(user.id)

def create_user_with_password(
    db: Session,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str
) -> User:
    # normalisation
    email_norm = email.strip().lower()
    first_name = first_name.strip()
    last_name = last_name.strip()
    if not email_norm:
        raise HTTPException(status_code=422, detail="email est requis")
    if not first_name:
        raise HTTPException(status_code=422, detail="first_name est requis")
    if not last_name:
        raise HTTPException(status_code=422, detail="last_name est requis")

    pwd = (password or "").strip()
    if len(pwd) < 4:
        raise HTTPException(status_code=422, detail="password doit contenir au moins 4 caractères")

    existing = db.query(User).filter(User.email == email_norm).first()
    if existing:
        raise UserAlreadyExists("User already exists")

    u = User(
        email=email_norm,
        first_name=first_name,
        last_name=last_name,
        role=UserRole(role),
        hashed_password=hash_password(pwd),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def generate_access_token(db: Session, *, email: str, password: str) -> str:
    email_norm = (email or "").strip().lower()
    user = db.query(User).filter(User.email == email_norm).first()
    if not user:
        raise UserNotFound("User not found")
    pwd = (password or "").strip()
    if not user.hashed_password or not check_password(pwd, user.hashed_password):
        raise IncorrectPassword("Incorrect password")
    return _encode_jwt(user.id)