from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# On importe la connexion DB
from app.database import get_db

# On importe ton service "Data Engineering"
from app.services.geo_service import get_tutors_by_department

# On définit le routeur
router = APIRouter(
    prefix="/search",
    tags=["Search & Data"]
)

@router.get("/tutors", response_model=Dict[str, Any])
def search_tutors_by_location(
    zip_code: str, 
    db: Session = Depends(get_db)
):
    """
    Endpoint de recherche intelligente.
    Prend un code postal complet (ex: 75011), 
    utilise Pandas pour extraire le département, 
    et renvoie les profs de ce département.
    """
    
    # Appel du service (logique métier)
    tutors = get_tutors_by_department(db=db, zip_code=zip_code)
    
    # Construction de la réponse
    return {
        "count": len(tutors),
        "search_zip": zip_code,
        "data": tutors
    }