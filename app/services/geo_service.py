import pandas as pd
from sqlalchemy.orm import Session
from app.models.tutor_profile import TutorProfile
from app.models.user import User, UserRole

def _extract_department(postal_code: str) -> str | None:
    """
    Extrait le département depuis un code postal
    """
    if not postal_code or len(str(postal_code)) < 2:
        return None
        
    dep_str = str(postal_code).strip()
    
    if not dep_str.isdigit():
        return None
    
    # Gestion Corse
    if dep_str.startswith('20'):
        try:
            return '2A' if int(dep_str) < 20200 else '2B'
        except ValueError:
            return None
        
    return dep_str[:2]


def postal_code_to_department(postal_code: str | None) -> str | None:
    """
    Fonction publique pour calculer le département
    """
    return _extract_department(postal_code)


def get_tutors_by_department(db: Session, postal_code: str) -> list[dict]:
    """
    Récupère les tuteurs d'un département via le code postal
    """
    try:
        target_dept = _extract_department(postal_code)
        if not target_dept:
            return []

        # Jointure User + TutorProfile
        # On filtre sur User.department 
        results = db.query(User, TutorProfile)\
                    .join(TutorProfile, User.id == TutorProfile.user_id)\
                    .filter(User.role == UserRole.tutor)\
                    .filter(User.department == target_dept)\
                    .all()
        
        if not results:
            return []

        # Formatage des résultats
        tutors = []
        for user, profile in results:
            tutors.append({
                "id": profile.id,
                "user_id": user.id,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
                "email": user.email,
                "department": user.department or "",
                "postal_code": user.postal_code or "",
                "bio": profile.bio or "",
                "photo_url": profile.photo_url or "",
                "subjects": profile.subjects or "",
                "hourly_rate": profile.hourly_rate,
                "years_experience": profile.years_experience
            })

        return tutors
        
    except Exception as e:
        print(f"Erreur dans get_tutors_by_department: {str(e)}")
        return []

