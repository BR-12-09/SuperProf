# SuperProf — Mini Plateforme (FastAPI + Postgres + Frontend statique)

Projet de démonstration inspiré de Superprof : gestion d’offres de cours (tuteurs), réservations (étudiants), créneaux horaires, profils tuteurs, avis & notes, et mini-frontend statique.

## Pile technique
- API : FastAPI, SQLAlchemy, Pydantic, JWT
- DB : PostgreSQL
- Frontend : `frontend/index.html` (HTML/CSS/JS vanilla)
- Conteneurs : Docker + docker-compose
- Tests : pytest

---

## Démarrage rapide

Pré-requis : Docker et docker-compose installés.

1) Arrêter et nettoyer l’environnement (volumes compris) → commande : `docker compose down -v`  
2) Rebuild des images → commande : `docker compose build --no-cache`  
3) Lancer les services → commande : `docker compose up -d`  
4) Seed (tables + données démo) → commande : `docker compose exec api python scripts/seed.py --reset`

Accès :  
- API : http://localhost:5001/  
- DB : Postgres (port 5432 *dans* le réseau Docker)  
- Frontend : http://localhost:8080/

---

## Comptes démo (seed)

- Tuteur : `alice.tutor@example.com` / `pass`  
- Étudiant : `bob.student@example.com` / `pass`

---

## Structure du projet

- `app/`
  - `main.py`, `database.py`
  - `models/` : `user.py`, `offer.py`, `booking.py`, `timeslot.py`, `tutor_profile.py`, `review.py`
  - `routers/` : `auth.py`, `offers.py`, `bookings.py`, `timeslots.py`, `tutors.py`, `reviews.py` , `users.py` 
  - `serializers/`, `services/`, etc.
- `scripts/seed.py`
- `frontend/index.html`
- `tests/`
    - `routers/` : `test_auth.py`, `test_offers_bookings.py`
    - `services/` : `test_auth_services.py`
    - `conftest.py`
- `docker-compose.yml`
- `README.md`

---

## Fonctionnalités

- Auth JWT (inscription + login e-mail/mot de passe, endpoint `/auth/me`)
- Tuteurs : créer/voir ses offres, publier des créneaux
- Étudiants : lister les offres, réserver un cours ou un créneau précis
- Réservations : PENDING / ACCEPTED / REJECTED, vues tuteur & étudiant
- Profils tuteurs : ville, années d’expérience, langues, bio (CRUD pour le tuteur connecté)
- Avis & notes : laisser un avis (après acceptation), résumé des notes d’un tuteur
- Mini-frontend

---

## Lancer les tests

- Commande : `docker compose exec api pytest -q`

---

## Endpoints principaux

Auth
- `POST /auth/register` → body : `{ first_name, last_name, email, password, role }`
- `POST /auth/token` → body : `{ email, password }` → renvoie `{ access_token }`
- `GET /auth/me` → infos utilisateur courant

Offres & Créneaux
- `GET /offers/` → liste (filtrage/tri gérés côté front dans cette démo)
- `GET /offers/mine` → offres du tuteur connecté
- `POST /offers/` → créer une offre (tuteur)
- `POST /timeslots/` → publier un créneau (tuteur)
- `GET /timeslots/of-offer/{offer_id}` → créneaux d’une offre

Bookings (réservations)
- `POST /bookings/` → body : `{ offer_id, [timeslot_id] }`
- `POST /bookings/slot/{timeslot_id}` → si la route dédiée est activée
- `GET /bookings/list/mine` → réservations de l’étudiant connecté
- `GET /bookings/list/on-my-offers` → réservations reçues par le tuteur
- `POST /bookings/{booking_id}/ACCEPT` et `POST /bookings/{booking_id}/REJECT` → décision du tuteur

Profils tuteurs
- `GET /tutors/me/profile` → récupère (créé à la volée si absent)
- `PUT /tutors/me/profile` → met à jour (ville, années, langues[], bio)
- `GET /tutors/{tutor_id}/profile` → public

Avis / Notes
- `POST /reviews/for/{tutor_id}` → body : `{ rating: 1..5, comment?: str }`
- `GET /reviews/of-tutor/{tutor_id}` → liste d’avis
- `GET /reviews/of-tutor/{tutor_id}/summary` → `{ rating_count, rating_avg }`

Utilisateurs
- `GET /users/{id}` → `{ first_name, last_name, email, role }`

---

## Frontend

Le fichier `frontend/index.html` fournit une UI de démonstration :
- Accueil : création/connexion Tuteur ou Étudiant (redirigé selon le rôle)
- Tuteur :
  - Mes offres (+ création)
  - Publication de créneaux
  - Réservations reçues (accepter/rejeter) avec affichage du créneau réservé
  - Mon profil (ville, années d’expérience, langues, bio)
  - Avis reçus (+ note moyenne)
- Étudiant :
  - Liste des offres (recherche, fourchette de prix, tri)
  - Réservation d’un cours ou d’un créneau précis
  - Mes réservations (+ dépôt d’avis si ACCEPTED)

---

## Dépannage

- 401 Unauthorized : token absent/expiré → reconnecte-toi.
- 404 Not Found : vérifie la route exacte. Si `POST /bookings/slot/{timeslot_id}` n’existe pas, utilise `POST /bookings` avec `timeslot_id`.
- 422 Unprocessable Entity :
  - Profils tuteurs : `languages` doit être un tableau de chaînes (le front convertit “fr, en” → `["fr","en"]`).
  - Créneaux : `start_utc < end_utc`, format ISO 8601 (UTC).
- CORS / ports : le front appelle l’API sur `http://localhost:5001`.