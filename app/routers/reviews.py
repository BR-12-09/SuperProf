from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.routers.utils import get_user_id
from app.models.user import User, UserRole
from app.models.review import Review
from app.serializers.review import ReviewIn, ReviewOut

router = APIRouter(prefix="/reviews", tags=["reviews"])

def _get_user(db: Session, user_id: str) -> User:
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    return u

@router.post("/for/{tutor_id}", response_model=ReviewOut)
def create_review_for_tutor(tutor_id: str, payload: ReviewIn, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    me = _get_user(db, user_id)
    if me.role != UserRole.student:
        raise HTTPException(403, "Only students can create reviews")
    tutor = _get_user(db, tutor_id)
    if tutor.role != UserRole.tutor:
        raise HTTPException(400, "Target user is not a tutor")
    rev = Review(tutor_id=tutor.id, student_id=me.id, rating=payload.rating, comment=payload.comment)
    db.add(rev); db.commit(); db.refresh(rev)
    return rev

@router.get("/of-tutor/{tutor_id}", response_model=list[ReviewOut])
def list_reviews_of_tutor(tutor_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.tutor_id == tutor_id).order_by(Review.created_at.desc()).all()

@router.get("/of-tutor/{tutor_id}/summary")
def rating_summary(tutor_id: str, db: Session = Depends(get_db)):
    q = db.query(func.count(Review.id), func.avg(Review.rating)).filter(Review.tutor_id == tutor_id)
    count, avg = q.first()
    return {"tutor_id": tutor_id, "rating_count": int(count or 0), "rating_avg": float(avg) if avg is not None else None}
