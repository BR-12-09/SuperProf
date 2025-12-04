from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database import BaseSQL

class Timeslot(BaseSQL):
    __tablename__ = "timeslots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    offer_id = Column(String, ForeignKey("offers.id"), nullable=False)

    start_utc = Column(DateTime, nullable=False)
    end_utc = Column(DateTime, nullable=False)

    is_booked = Column(Boolean, default=False, nullable=False)
    booking_id = Column(String, ForeignKey("bookings.id"), nullable=True)

    offer = relationship("Offer")
