from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.offer import Offer
from app.models.booking import Booking, BookingStatus
from app.models.user import User, UserRole
from app.serializers.booking import BookingCreate, BookingOut
from app.routers.utils import get_user_id
from app.models.timeslot import Timeslot

booking_router = APIRouter(prefix="/bookings", tags=["bookings"])

@booking_router.get("/", response_model=list[BookingOut])
def list_bookings(
    db: Session = Depends(get_db),
    status: BookingStatus | None = Query(None),
    skip: int = 0,
    limit: int = 50,
):
    q = db.query(Booking)
    if status:
        q = q.filter(Booking.status == status)
    return q.offset(skip).limit(limit).all()

@booking_router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    bk = db.query(Booking).filter(Booking.id == booking_id).first()
    if not bk:
        raise HTTPException(404, "Booking not found")
    return bk

@booking_router.get("/by-student/{student_id}", response_model=list[BookingOut])
def list_bookings_by_student(
    student_id: str, db: Session = Depends(get_db),
    status: BookingStatus | None = Query(None),
    skip: int = 0, limit: int = 50,
):
    q = db.query(Booking).filter(Booking.student_id == student_id)
    if status:
        q = q.filter(Booking.status == status)
    return q.offset(skip).limit(limit).all()

@booking_router.get("/by-offer/{offer_id}", response_model=list[BookingOut])
def list_bookings_by_offer(
    offer_id: str, db: Session = Depends(get_db),
    status: BookingStatus | None = Query(None),
    skip: int = 0, limit: int = 50,
):
    q = db.query(Booking).filter(Booking.offer_id == offer_id)
    if status:
        q = q.filter(Booking.status == status)
    return q.offset(skip).limit(limit).all()

@booking_router.get("/by-tutor/{tutor_id}", response_model=list[BookingOut])
def list_bookings_by_tutor(
    tutor_id: str, db: Session = Depends(get_db),
    status: BookingStatus | None = Query(None),
    skip: int = 0, limit: int = 50,
):
    # via join Offer -> Booking
    q = (
        db.query(Booking)
        .join(Offer, Offer.id == Booking.offer_id)
        .filter(Offer.tutor_id == tutor_id)
    )
    if status:
        q = q.filter(Booking.status == status)
    return q.offset(skip).limit(limit).all()

@booking_router.post("/", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db), me_id: str = Depends(get_user_id)):
    student = db.query(User).filter(User.id == me_id).first()
    if not student or student.role != UserRole.student:
        raise HTTPException(403, "Only students can create bookings")
    offer = db.query(Offer).filter(Offer.id == payload.offer_id).first()
    if not offer:
        raise HTTPException(404, "Offer not found")
    timeslot = None
    if payload.timeslot_id:
        timeslot = db.query(Timeslot).filter(Timeslot.id == payload.timeslot_id).first()
        if not timeslot:
            raise HTTPException(404, "Timeslot not found")
        if timeslot.offer_id != offer.id:
            raise HTTPException(400, "Timeslot does not belong to this offer")
        if timeslot.is_booked:
            raise HTTPException(409, "Timeslot already booked")

    booking = Booking(offer_id=offer.id, student_id=student.id, status=BookingStatus.PENDING)
    db.add(booking)
    db.commit()
    db.refresh(booking)

    if timeslot:
        timeslot.is_booked = True
        timeslot.booking_id = booking.id
        db.add(timeslot)
        db.commit()
        db.refresh(timeslot)

    return booking

@booking_router.post("/{booking_id}/{action}", response_model=BookingOut)
def decide_booking(booking_id: str, action: str, db: Session = Depends(get_db), me_id: str = Depends(get_user_id)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(404, "Booking not found")
    offer = db.query(Offer).filter(Offer.id == booking.offer_id).first()
    if not offer or offer.tutor_id != me_id:
        raise HTTPException(403, "Not your offer")
    if action.upper() not in ("ACCEPT", "REJECT"):
        raise HTTPException(400, "Action must be ACCEPT or REJECT")
    if action.upper() == "REJECT":
        # free any linked timeslot
        ts = db.query(Timeslot).filter(Timeslot.booking_id == booking.id).first()
        if ts:
            ts.is_booked = False
            ts.booking_id = None
            db.add(ts)
            db.commit()
    booking.status = BookingStatus.ACCEPTED if action.upper()=="ACCEPT" else BookingStatus.REJECTED
    db.commit()
    db.refresh(booking)
    return booking

@booking_router.get("/list/mine", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    return db.query(Booking).filter(Booking.student_id == user_id).all()

@booking_router.get("/list/on-my-offers", response_model=list[BookingOut])
def bookings_on_my_offers(db: Session = Depends(get_db), user_id: str = Depends(get_user_id)):
    return (
        db.query(Booking)
        .join(Offer, Booking.offer_id == Offer.id)
        .filter(Offer.tutor_id == user_id)
        .all()
    )