from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
import uuid, enum

from app.database import BaseSQL

class UserRole(str, enum.Enum):
    student = "student"
    tutor = "tutor"

class User(BaseSQL):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.student)
    city = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)

    postal_code = Column(String, nullable=True)
    department = Column(String, nullable=True)


    # Relation tuteur -> ses offres
    offers = relationship("Offer", back_populates="tutor", cascade="all,delete", lazy="selectin")
    tutor_profile = relationship("TutorProfile", uselist=False, back_populates="user")