from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app import serializers
from app.database import get_db
from app.exceptions.user import UserNotFound, UserAlreadyExists
from app.services import user as user_service
from app.serializers.user import UserOutput  # pour les réponses (optionnel)

user_router = APIRouter(prefix="/users")

@user_router.post("/", tags=["users"], response_model=UserOutput)
async def create_user(user: serializers.User, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(user=user, db=db)
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="User already exists")

@user_router.get("/", tags=["users"], response_model=list[UserOutput])
async def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db=db)

@user_router.delete("/{user_id}", tags=["users"])
async def delete_user_by_id(user_id: str, db: Session = Depends(get_db)):
    try:
        return user_service.delete_user(user_id=user_id, db=db)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
