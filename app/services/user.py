from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User as ModelsUser
from app.serializers.user import User as SerializersUser
from app.exceptions.user import UserNotFound, UserAlreadyExists

def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> list[ModelsUser]:
    records = db.query(ModelsUser).offset(skip).limit(limit).all()
    for record in records:
        record.id = str(record.id)
    return records


def get_user_by_id(user_id: str, db: Session) -> ModelsUser:
    record = db.query(ModelsUser).filter(ModelsUser.id == user_id).first()
    if not record:
        raise UserNotFound
    record.id = str(record.id)
    return record


""" def get_users_by_title(title: str, db: Session) -> list[models.User]:
    records = db.query(models.User).filter(models.User.title == title).all()
    for record in records:
        record.id = str(record.id)
    return records """


def update_user(user_id: str, db: Session, user: SerializersUser) -> ModelsUser:
    db_user = get_user_by_id(user_id=user_id, db=db)
    payload = user.model_dump(exclude_unset=True)
    for field, value in payload.items():
        if value is not None:
            setattr(db_user, field, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(user_id: str, db: Session) -> ModelsUser:
    db_user = get_user_by_id(user_id=user_id, db=db)
    db.delete(db_user)
    db.commit()
    return db_user


def create_user(db: Session, user: SerializersUser) -> ModelsUser:
    db_user = ModelsUser(**user.model_dump())
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UserAlreadyExists
    db.refresh(db_user)
    db_user.id = str(db_user.id)
    return db_user
