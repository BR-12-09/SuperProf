from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import BaseSQL

class Review(BaseSQL):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    tutor_id = Column(String, ForeignKey("users.id"), nullable=False)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)

    rating = Column(Integer, nullable=False)  # 1..5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tutor = relationship("User", foreign_keys=[tutor_id])
    student = relationship("User", foreign_keys=[student_id])
