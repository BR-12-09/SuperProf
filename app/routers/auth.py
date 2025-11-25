from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.serializers.auth import Login, Register, AuthToken, Me
from app.services.auth import create_user_with_password, generate_access_token, decode_jwt
from app.models.user import User, UserRole
from app.exceptions.user import UserAlreadyExists, UserNotFound, IncorrectPassword
from app.routers.utils import verify_authorization_header

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# @auth_router.post("/token", response_model=AuthToken)
# def get_access_token(payload: Login, db: Session = Depends(get_db)) -> AuthToken:
#     try:
#         token = generate_access_token(db=db, email=payload.email, password=payload.password)
#         return AuthToken(access_token=token)
#     except UserNotFound as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except IncorrectPassword as e:
#         raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/register", response_model=AuthToken)
def register_user(payload: Register, db: Session = Depends(get_db)) -> AuthToken:
    try:
        user = create_user_with_password(
            db,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            role=payload.role,
        )
        token = generate_access_token(db, email=user.email, password=payload.password)
        return AuthToken(access_token=token)
    except UserAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))

@auth_router.post("/token", response_model=AuthToken)
def get_access_token(payload: Login, db: Session = Depends(get_db)) -> AuthToken:
    try:
        token = generate_access_token(db=db, email=payload.email, password=payload.password)
        return AuthToken(access_token=token)
    except UserNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IncorrectPassword as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.get("/me", response_model=Me)
def get_me(auth=Depends(verify_authorization_header), db: Session = Depends(get_db)) -> Me:
    # auth contains {"user_id": "..."}
    from app.models.user import User
    u = db.query(User).get(auth["user_id"])
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return u