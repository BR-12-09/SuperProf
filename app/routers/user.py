from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions.user import UserNotFound, UserAlreadyExists
from app.services import user as user_service
from app.serializers.user import User as SerializersUser, UserOutput, UserPublic # pour les réponses (optionnel)

user_router = APIRouter(prefix="/users")

@user_router.post("/", tags=["users"], response_model=UserOutput)
async def create_user(user: SerializersUser, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(user=user, db=db)
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="User already exists")

@user_router.get("/", tags=["users"], response_model=list[UserOutput])
async def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db=db)
    
@user_router.get("/{user_id}", tags=["users"], response_model=UserPublic)
async def get_user_public_by_id(user_id: str, db: Session = Depends(get_db)):
    try:
        u = user_service.get_user_by_id(user_id=user_id, db=db)
        # Pydantic filtrera aux champs de UserPublic (first_name, last_name, email, role)
        return u
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")

@user_router.delete("/{user_id}", tags=["users"])
async def delete_user_by_id(user_id: str, db: Session = Depends(get_db)):
    try:
        return user_service.delete_user(user_id=user_id, db=db)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
