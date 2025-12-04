# scripts/seed.py (ou ton chemin actuel)
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import argparse

from app.database import BaseSQL, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.booking import Booking, BookingStatus
from app.models.tutor_profile import TutorProfile
from app.models.review import Review
from app.models.timeslot import Timeslot
from app.services.auth import hash_password


# -------------------------
# UPSERT HELPERS
# -------------------------
def upsert_user(db: Session, email: str, first: str, last: str, role: UserRole,
                city: str | None = None, photo_url: str | None = None) -> User:
    u = db.query(User).filter(User.email == email).first()
    if u:
        # Optionnel: rafraîchir quelques champs vitrine
        if city is not None:
            u.city = city
        if photo_url is not None:
            u.photo_url = photo_url
        db.commit()
        db.refresh(u)
        return u
    u = User(email=email, first_name=first, last_name=last, role=role,
             city=city, photo_url=photo_url)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def upsert_offer(db: Session, tutor_id: str, subject: str, price: Decimal,
                 desc: str | None = None) -> Offer:
    o = (db.query(Offer)
           .filter(Offer.tutor_id == tutor_id, Offer.subject == subject)
           .first())
    if o:
        # Optionnel: mettre à jour price/desc si changés
        o.price_hour = price
        o.description = desc
        db.commit()
        db.refresh(o)
        return o
    o = Offer(tutor_id=tutor_id, subject=subject, description=desc, price_hour=price)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def upsert_booking(db: Session, offer_id: str, student_id: str,
                   status: BookingStatus = BookingStatus.PENDING) -> Booking:
    b = (db.query(Booking)
           .filter(Booking.offer_id == offer_id, Booking.student_id == student_id)
           .first())
    if b:
        # tu peux forcer un état si tu veux
        # b.status = status; db.commit(); db.refresh(b)
        return b
    b = Booking(offer_id=offer_id, student_id=student_id, status=status)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def upsert_tutor_profile(db: Session, user_id: str,
                         bio: str | None = None,
                         city: str | None = None,
                         languages: str | None = None,       # CSV "FR,EN"
                         years_experience: int | None = None,
                         photo_url: str | None = None) -> TutorProfile:
    p = db.query(TutorProfile).filter(TutorProfile.user_id == user_id).first()
    if p:
        # Patch/update light
        if bio is not None: p.bio = bio
        if city is not None: p.city = city
        if languages is not None: p.languages = languages
        if years_experience is not None: p.years_experience = years_experience
        if photo_url is not None: p.photo_url = photo_url
        db.commit()
        db.refresh(p)
        return p
    p = TutorProfile(
        user_id=user_id, bio=bio, city=city, languages=languages,
        years_experience=years_experience, photo_url=photo_url
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def upsert_timeslot(db: Session, offer_id: str,
                    start_utc: datetime, end_utc: datetime) -> Timeslot:
    # Ici on considère (offer_id, start_utc, end_utc) comme unique “logiquement”
    t = (db.query(Timeslot)
           .filter(Timeslot.offer_id == offer_id,
                   Timeslot.start_utc == start_utc,
                   Timeslot.end_utc == end_utc)
           .first())
    if t:
        return t
    t = Timeslot(offer_id=offer_id, start_utc=start_utc, end_utc=end_utc, is_booked=False)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def upsert_review(db: Session, tutor_id: str, student_id: str,
                  rating: int, comment: str | None = None) -> Review:
    # Pour éviter les doublons exacts (même auteur/élève/commentaire/rating), on peut chercher le plus récent
    r = (db.query(Review)
           .filter(Review.tutor_id == tutor_id,
                   Review.student_id == student_id,
                   Review.rating == rating,
                   Review.comment == comment)
           .first())
    if r:
        return r
    r = Review(tutor_id=tutor_id, student_id=student_id, rating=rating, comment=comment)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


# -------------------------
# RESET
# -------------------------
def reset_data(db: Session, keep_users: bool = False):
    """
    Nettoyage simple pour reseed.
    - Si keep_users=True: supprime reviews + timeslots + bookings + offers
    - Sinon: supprime reviews + timeslots + bookings + offers + users
    Ordre important à cause des FK !
    """
    # FK: Timeslot.booking_id -> Booking.id
    # FK: Timeslot.offer_id -> Offer.id
    # FK: Booking.offer_id -> Offer.id
    # FK: TutorProfile.user_id -> User.id
    # FK: Review.tutor_id/student_id -> User.id
    db.query(Review).delete()
    db.query(Timeslot).delete()
    db.query(Booking).delete()
    db.query(Offer).delete()
    if not keep_users:
        db.query(TutorProfile).delete()
        db.query(User).delete()
    db.commit()


# -------------------------
# MAIN SEED
# -------------------------
def run(keep_users: bool = False, do_reset: bool = False):
    # S'assure que toutes les tables existent si on exécute le seed hors cycle FastAPI
    BaseSQL.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if do_reset:
            reset_data(db, keep_users=keep_users)

        # USERS
        tutor = upsert_user(
            db,
            email="alice.tutor@example.com",
            first="Alice",
            last="Tutor",
            role=UserRole.tutor,
            city="Paris",
            photo_url=None
        )
        student = upsert_user(
            db,
            email="bob.student@example.com",
            first="Bob",
            last="Student",
            role=UserRole.student,
            city="Lyon",
            photo_url=None
        )

        # ensure passwords
        changed = False
        if not tutor.hashed_password:
            tutor.hashed_password = hash_password("pass")
            changed = True
        if not student.hashed_password:
            student.hashed_password = hash_password("pass")
            changed = True
        if changed:
            db.commit()

        # TUTOR PROFILE
        upsert_tutor_profile(
            db,
            user_id=tutor.id,
            bio="Ingénieure passionnée, j'enseigne Python et SQL.",
            city="Paris",
            languages="FR,EN",
            years_experience=4,
            photo_url=None
        )

        # OFFERS
        off1 = upsert_offer(
            db, tutor_id=tutor.id, subject="Maths",
            price=Decimal("25.00"), desc="Analyse L1 / L2"
        )
        off2 = upsert_offer(
            db, tutor_id=tutor.id, subject="Python",
            price=Decimal("30.00"), desc="Bases → Avancé"
        )

        # TIMESLOTS sur off2 (ex: demain)
        now = datetime.utcnow()
        ts1 = upsert_timeslot(db, off2.id, start_utc=now + timedelta(days=1, hours=9),
                              end_utc=now + timedelta(days=1, hours=10))
        ts2 = upsert_timeslot(db, off2.id, start_utc=now + timedelta(days=1, hours=11),
                              end_utc=now + timedelta(days=1, hours=12))

        # BOOKING student -> off1 (sans timeslot)
        bk1 = upsert_booking(db, offer_id=off1.id, student_id=student.id, status=BookingStatus.PENDING)

        # BOOKING student -> off2 AVEC timeslot (on “verrouille” ts1)
        bk2 = upsert_booking(db, offer_id=off2.id, student_id=student.id, status=BookingStatus.PENDING)
        # verrouiller ts1 si pas déjà lock
        if not ts1.is_booked:
            ts1.is_booked = True
            ts1.booking_id = bk2.id
            db.add(ts1)
            db.commit()
            db.refresh(ts1)

        # REVIEWS student -> tutor
        r1 = upsert_review(db, tutor_id=tutor.id, student_id=student.id, rating=5, comment="Super pédagogue !")
        r2 = upsert_review(db, tutor_id=tutor.id, student_id=student.id, rating=4, comment="Très clair, je recommande.")

        print("Seed OK ✅")
        print(f"Tutor:   {tutor.id}  {tutor.email}")
        print(f"Student: {student.id}  {student.email}")
        print(f"Offer 1: {off1.id}  {off1.subject}")
        print(f"Offer 2: {off2.id}  {off2.subject}")
        print(f"Timeslot 1: {ts1.id} ({ts1.start_utc} → {ts1.end_utc}) booked={ts1.is_booked}")
        print(f"Timeslot 2: {ts2.id} ({ts2.start_utc} → {ts2.end_utc}) booked={ts2.is_booked}")
        print(f"Booking 1: {bk1.id}  offer={bk1.offer_id} student={bk1.student_id} status={bk1.status}")
        print(f"Booking 2: {bk2.id}  offer={bk2.offer_id} student={bk2.student_id} status={bk2.status}")
        print(f"Review 1:  {r1.id}  rating={r1.rating}")
        print(f"Review 2:  {r2.id}  rating={r2.rating}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Supprimer les données avant de reseeder")
    parser.add_argument("--keep-users", action="store_true", help="Conserver les users lors du reset (ne supprime que offers + bookings + timeslots + reviews)")
    args = parser.parse_args()

    run(keep_users=args.keep_users, do_reset=args.reset)
