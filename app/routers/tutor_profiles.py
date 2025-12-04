from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.utils import get_user_id
from app.models.user import User, UserRole
from app.models.tutor_profile import TutorProfile
from app.serializers.tutor_profile import TutorProfileIn, TutorProfileOut

router = APIRouter(prefix="/tutors", tags=["tutors"])

def _get_me(db: Session, user_id: str) -> User:
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    return u

@router.get("/me/profile", response_model=TutorProfileOut)
def get_my_profile(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    me = _get_me(db, user_id)
    if me.role != UserRole.tutor:
        raise HTTPException(403, "Only tutors can access their profile")
    prof = db.query(TutorProfile).filter(TutorProfile.user_id == me.id).first()
    if not prof:
        # create empty profile on-the-fly
        prof = TutorProfile(user_id=me.id)
        db.add(prof); db.commit(); db.refresh(prof)
    return prof

@router.put("/me/profile", response_model=TutorProfileOut)
def upsert_my_profile(payload: TutorProfileIn, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    me = _get_me(db, user_id)
    if me.role != UserRole.tutor:
        raise HTTPException(403, "Only tutors can update their profile")

    prof = db.query(TutorProfile).filter(TutorProfile.user_id == me.id).first()
    if not prof:
        prof = TutorProfile(user_id=me.id)
        db.add(prof)
        db.commit()
        db.refresh(prof)

    data = payload.model_dump(exclude_unset=True)  # <<--- important en Pydantic v2

    # Normalisation côté serveur au cas où le front envoie "fr,en" en string
    if "languages" in data and isinstance(data["languages"], str):
        data["languages"] = [s.strip() for s in data["languages"].split(",") if s.strip()]

    for k, v in data.items():
        setattr(prof, k, v)

    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

@router.get("/{tutor_id}/profile", response_model=TutorProfileOut)
def get_public_profile(tutor_id: str, db: Session = Depends(get_db)):
    prof = db.query(TutorProfile).filter(TutorProfile.user_id == tutor_id).first()
    if not prof:
        raise HTTPException(404, "Tutor profile not found")
    return prof
