from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TimeslotIn(BaseModel):
    offer_id: str
    start_utc: datetime
    end_utc: datetime

    class Config:
        from_attributes = True

class TimeslotOut(TimeslotIn):
    id: str
    is_booked: bool
    booking_id: Optional[str] = None
