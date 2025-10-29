# app/models/booking.py
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid, enum

from app.database import BaseSQL

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class Booking(BaseSQL):
    __tablename__ = "bookings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    offer_id = Column(String, ForeignKey("offers.id"), nullable=False)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)

    offer = relationship("Offer")
    # Tu peux ajouter: student = relationship("User") plus tard si besoin
