# app/serializers/offer.py
from pydantic import BaseModel, Field
from typing import Optional

class OfferCreate(BaseModel):
    subject: str = Field(min_length=1)
    description: Optional[str] = None
    price_hour: float
    tutor_id: str  # provisoire (en attendant l'auth)

class OfferOut(BaseModel):
    id: str
    tutor_id: str
    subject: str
    description: str | None
    price_hour: float
    class Config:
        from_attributes = True
