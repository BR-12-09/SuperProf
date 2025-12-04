from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid

from app.database import BaseSQL

class TutorProfile(BaseSQL):
    __tablename__ = "tutor_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)

    bio = Column(String, nullable=True)
    city = Column(String, nullable=True)
    languages = Column(String, nullable=True)  # CSV simple: "FR,EN,ES"
    years_experience = Column(Integer, nullable=True)
    photo_url = Column(String, nullable=True)

    user = relationship("User", back_populates="tutor_profile")

    __table_args__ = (
        UniqueConstraint('user_id', name='uniq_tutor_profile_user'),
    )
