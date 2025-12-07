from pydantic import BaseModel, Field
from typing import Optional

class TutorProfileIn(BaseModel):
    bio: Optional[str] = None
    city: Optional[str] = None
    languages: Optional[str] = Field(default=None, description="CSV: 'FR,EN,ES'")
    years_experience: Optional[int] = None
    photo_url: Optional[str] = None


    class Config:
        from_attributes = True

class TutorProfileOut(TutorProfileIn):
    id: str
    user_id: str
