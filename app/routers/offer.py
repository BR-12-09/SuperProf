# app/routers/offer.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.offer import Offer
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.serializers.offer import OfferCreate, OfferOut
from app.serializers.booking import BookingCreate, BookingOut

offer_router = APIRouter(prefix="/offers", tags=["offers"])
booking_router = APIRouter(prefix="/bookings", tags=["bookings"])

# ---- OFFERS ----

@offer_router.post("/", response_model=OfferOut, status_code=201)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db)):
    tutor = db.query(User).filter(User.id == payload.tutor_id).first()
    if not tutor:
        raise HTTPException(404, "Tutor (user) not found")
    if tutor.role != UserRole.tutor:
        raise HTTPException(403, "Only users with role 'tutor' can create offers")

    offer = Offer(
        tutor_id=tutor.id,
        subject=payload.subject,
        description=payload.description,
        price_hour=payload.price_hour,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer

@offer_router.get("/", response_model=list[OfferOut])
def list_offers(q: str | None = Query(None, description="search by subject"),
                db: Session = Depends(get_db)):
    query = db.query(Offer)
    if q:
        query = query.filter(Offer.subject.ilike(f"%{q}%"))
    return query.all()

@offer_router.get("/by-tutor/{tutor_id}", response_model=list[OfferOut])
def list_offers_by_tutor(tutor_id: str, db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.tutor_id == tutor_id).all()

# ---- BOOKINGS ----

@booking_router.post("/", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == payload.offer_id).first()
    if not offer:
        raise HTTPException(404, "Offer not found")

    student = db.query(User).filter(User.id == payload.student_id).first()
    if not student:
        raise HTTPException(404, "Student (user) not found")
    if student.role != UserRole.student:
        raise HTTPException(403, "Only users with role 'student' can create bookings")

    booking = Booking(offer_id=offer.id, student_id=student.id, status=BookingStatus.PENDING)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@booking_router.post("/{booking_id}/{action}", response_model=BookingOut)
def decide_booking(booking_id: str, action: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")

    if action.upper() not in ("ACCEPT", "REJECT"):
        raise HTTPException(400, "Action must be ACCEPT or REJECT")

    booking.status = BookingStatus.ACCEPTED if action.upper() == "ACCEPT" else BookingStatus.REJECTED
    db.commit()
    db.refresh(booking)
    return booking
