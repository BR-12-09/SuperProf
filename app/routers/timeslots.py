from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.routers.utils import get_user_id
from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.timeslot import Timeslot
from app.serializers.timeslot import TimeslotIn, TimeslotOut

router = APIRouter(prefix="/timeslots", tags=["timeslots"])

def _get_me(db: Session, user_id: str) -> User:
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    return u

@router.post("/", response_model=TimeslotOut)
def create_timeslot(payload: TimeslotIn, db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    me = _get_me(db, user_id)
    if me.role != UserRole.tutor:
        raise HTTPException(403, "Only tutors can create timeslots")
    offer = db.query(Offer).filter(Offer.id == payload.offer_id).first()
    if not offer:
        raise HTTPException(404, "Offer not found")
    if offer.tutor_id != me.id:
        raise HTTPException(403, "You can only create timeslots for your offers")

    if payload.start_utc >= payload.end_utc:
        raise HTTPException(400, "start_utc must be before end_utc")

    t = Timeslot(
        offer_id=offer.id,
        start_utc=payload.start_utc,
        end_utc=payload.end_utc,
        is_booked=False
    )
    db.add(t); db.commit(); db.refresh(t)
    return t

@router.get("/of-offer/{offer_id}", response_model=list[TimeslotOut])
def list_timeslots_of_offer(offer_id: str, db: Session = Depends(get_db)):
    return db.query(Timeslot).filter(Timeslot.offer_id == offer_id).order_by(Timeslot.start_utc.asc()).all()

@router.get("/mine", response_model=list[TimeslotOut])
def list_my_timeslots(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    me = _get_me(db, user_id)
    if me.role != UserRole.tutor:
        raise HTTPException(403, "Only tutors can list their timeslots")
    # all timeslots across my offers
    return db.query(Timeslot).join(Offer, Timeslot.offer_id == Offer.id).filter(Offer.tutor_id == me.id).order_by(Timeslot.start_utc.asc()).all()
