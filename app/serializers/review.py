from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

    class Config:
        from_attributes = True

class ReviewOut(ReviewIn):
    id: str
    tutor_id: str
    student_id: str
    created_at: datetime
