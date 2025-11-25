from pydantic import BaseModel, ConfigDict
from enum import Enum

class BookingCreate(BaseModel):
    offer_id: str

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