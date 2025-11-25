from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.offer import Offer
from app.models.user import User, UserRole
from app.serializers.offer import OfferCreate, OfferOut
from app.routers.utils import get_user_id
from app.routers.utils import verify_authorization_header


offer_router = APIRouter(prefix="/offers", tags=["offers"])

@offer_router.post("/", response_model=OfferOut, status_code=201)
def create_offer(payload: OfferCreate, db: Session = Depends(get_db), me_id: str = Depends(get_user_id)):
    tutor = db.query(User).filter(User.id == me_id).first()
    if not tutor or tutor.role != UserRole.tutor:
        raise HTTPException(403, "Only tutors can create offers")

    offer = Offer(
        tutor_id=me_id,
        subject=payload.subject,
        description=payload.description,
        price_hour=payload.price_hour,
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer

@offer_router.get("/", response_model=list[OfferOut])
def list_offers(q: str | None = Query(None, description="search by subject"),
                db: Session = Depends(get_db)):
    query = db.query(Offer)
    if q:
        query = query.filter(Offer.subject.ilike(f"%{q}%"))
    return query.all()

@offer_router.get("/by-tutor/{tutor_id}", response_model=list[OfferOut])
def list_offers_by_tutor(tutor_id: str, db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.tutor_id == tutor_id).all()

@offer_router.get("/mine", response_model=list[OfferOut])
def list_my_offers(auth=Depends(verify_authorization_header), db: Session = Depends(get_db)):
    return db.query(Offer).filter(Offer.tutor_id == auth["user_id"]).all()