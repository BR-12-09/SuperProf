from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    offer_id: str
    timeslot_id: Optional[str] = None

class BookingStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    offer_id: str
    student_id: str
    status: BookingStatus
    timeslot_id: str | None = None