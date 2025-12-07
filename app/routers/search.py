from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.services.geo_service import get_tutors_by_department

router = APIRouter(
    prefix="/search",
    tags=["Search & Data"]
)

@router.get("/tutors", response_model=Dict[str, Any])
def search_tutors_by_location(
    postal_code: str = Query(..., min_length=5, max_length=5, description="Code postal français (5 chiffres)"),
    db: Session = Depends(get_db)
):
    """
    Renvoie les profs d'un département précis
    """
    
    # Validation du format du code postal
    if not postal_code.isdigit():
        raise HTTPException(
            status_code=400, 
            detail="Le code postal doit contenir uniquement des chiffres"
        )
    
    try:
        # Appel du service (logique métier)
        tutors = get_tutors_by_department(db=db, postal_code=postal_code)
        
        # Vérification si des tuteurs ont été trouvés
        if tutors is None:
            raise HTTPException(
                status_code=400,
                detail="Code postal invalide ou département non reconnu"
            )
        
        # Construction de la réponse
        return {
            "count": len(tutors),
            "search_zip": postal_code,
            "data": tutors
        }
        
    except HTTPException:
        # Re-lever les HTTPException déjà gérées
        raise
        
    except Exception as e:
        # Logger l'erreur pour le débogage (optionnel)
        print(f"Erreur lors de la recherche de tuteurs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur interne lors de la recherche des tuteurs"
        )