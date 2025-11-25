from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class OfferCreate(BaseModel):
    subject: str = Field(min_length=1)
    description: Optional[str] = None
    price_hour: float

class OfferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tutor_id: str
    subject: str
    description: str | None
    price_hour: float