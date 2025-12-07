import pandas as pd
from sqlalchemy.orm import Session
from app.models.tutor_profile import TutorProfile
from app.models.user import User

# --- Fonctions utilitaires (internes) ---

def _extract_department(postal_code: str) -> str | None:
    """
    Fonction simple pour extraire le département (ex: '75001' -> '75')
    """
    if not postal_code or len(str(postal_code)) < 2:
        return None
        
    dep_str = str(postal_code).strip()
    
    # Gestion Corse (20100 -> 2A, etc.)
    if dep_str.startswith('20'):
        return '2A' if int(dep_str) < 20200 else '2B'
        
    return dep_str[:2]

def postal_code_to_department(postal_code: str | None) -> str | None:
    """
    Fonction publique utilisée pour calculer automatiquement
    le département d’un user à partir de son code postal.
    """
    return _extract_department(postal_code)


# --- Fonction principale (Service) ---

def get_tutors_by_department(db: Session, postal_code: str) -> list[dict]:
    """
    Récupère les profs et filtre ceux du même département via Pandas.
    """
    target_dept = _extract_department(postal_code)
    if not target_dept:
        return []

    # 1. Récupération des données brutes depuis la BDD
    # On fait une jointure pour avoir les infos du profil ET du user (nom, email...)
    results = db.query(TutorProfile, User)\
                .join(User, TutorProfile.user_id == User.id)\
                .all()
    
    if not results:
        return []

    # 2. Préparation pour Pandas (Aplatir les résultats)
    data_list = []
    for profile, user in results:
        data_list.append({
            "id": profile.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "bio": profile.bio,
            "city": profile.city,
            "postal_code": profile.postal_code, # Le champ qu'on vient d'ajouter
            "photo_url": profile.photo_url,
            "subject_highlight": "Maths / Python" # Exemple statique ou à récupérer des offres
        })

    # 3. Création du DataFrame Pandas (Data Engineering)
    df = pd.DataFrame(data_list)
    
    if df.empty or 'postal_code' not in df.columns:
        return []

    # 4. Application du filtre "Data"
    # On crée une colonne temporaire 'dept' pour filtrer
    df['postal_code'] = df['postal_code'].fillna('').astype(str)
    df['dept'] = df['postal_code'].apply(_extract_department)
    
    filtered_df = df[df['dept'] == target_dept]

    # 5. Retour en format liste de dictionnaires
    return filtered_df.to_dict(orient='records')