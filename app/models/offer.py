from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
import uuid

from app.database import BaseSQL

class Offer(BaseSQL):
    __tablename__ = "offers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tutor_id = Column(String, ForeignKey("users.id"), nullable=False)
    subject = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price_hour = Column(Numeric(precision=10, scale=2), nullable=False)

    tutor = relationship("User", back_populates="offers")
