# app/serializers/booking.py
from pydantic import BaseModel
from enum import Enum

class BookingCreate(BaseModel):
    offer_id: str
    student_id: str  # provisoire (en attendant l'auth)

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class BookingOut(BaseModel):
    id: str
    offer_id: str
    student_id: str
    status: BookingStatus
    class Config:
        from_attributes = True
