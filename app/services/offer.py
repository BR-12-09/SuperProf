from sqlalchemy.orm import Session
from app.models.offer import Offer
from app.models.user import User, UserRole

def get_offers_by_department(db: Session, department: str, limit: int = 3) -> list[Offer]:
    """
    Récupère les offres de tuteurs d'un département donné
    """
    if not department:
        return []
    
    # Récupérer les offres où le tuteur a le même département
    offers = db.query(Offer)\
               .join(User, Offer.tutor_id == User.id)\
               .filter(User.role == UserRole.tutor)\
               .filter(User.department == department)\
               .limit(limit)\
               .all()
    
    return offers