from decimal import Decimal
from sqlalchemy.orm import Session
import argparse

from app.database import BaseSQL, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.offer import Offer
from app.models.booking import Booking, BookingStatus
from app.services.auth import hash_password

def upsert_user(db: Session, email: str, first: str, last: str, role: UserRole) -> User:
    u = db.query(User).filter(User.email == email).first()
    if u:
        return u
    u = User(email=email, first_name=first, last_name=last, role=role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def upsert_offer(db: Session, tutor_id: str, subject: str, price: Decimal, desc: str | None = None) -> Offer:
    o = db.query(Offer).filter(Offer.tutor_id == tutor_id, Offer.subject == subject).first()
    if o:
        return o
    o = Offer(tutor_id=tutor_id, subject=subject, description=desc, price_hour=price)
    db.add(o)
    db.commit()
    db.refresh(o)
    return o

def upsert_booking(db: Session, offer_id: str, student_id: str, status: BookingStatus = BookingStatus.PENDING) -> Booking:
    b = (db.query(Booking).filter(Booking.offer_id == offer_id, Booking.student_id == student_id).first())
    if b:
        # tu peux mettre à jour le statut si tu veux forcer un état :
        # b.status = status; db.commit(); db.refresh(b)
        return b
    b = Booking(offer_id=offer_id, student_id=student_id, status=status)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

def reset_data(db: Session, keep_users: bool = False):
    """
    Nettoyage simple pour reseed.
    - Si keep_users=True: on supprime seulement bookings + offers
    - Sinon: on supprime bookings + offers + users
    """
    # ordre important à cause des FK
    db.query(Booking).delete()
    db.query(Offer).delete()
    if not keep_users:
        db.query(User).delete()
    db.commit()

def run(keep_users: bool = False, do_reset: bool = False):
    # Assure que les tables existent (utile si tu lances le seed en dehors du cycle FastAPI)
    BaseSQL.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if do_reset:
            reset_data(db, keep_users=keep_users)

        tutor = upsert_user(db, "alice.tutor@example.com", "Alice", "Tutor", UserRole.tutor)
        student = upsert_user(db, "bob.student@example.com", "Bob", "Student", UserRole.student)

        if not tutor.hashed_password:
            tutor.hashed_password = hash_password("pass")
        if not student.hashed_password:
            student.hashed_password = hash_password("pass")
        db.commit()

        off1 = upsert_offer(db, tutor_id=tutor.id, subject="Maths",  price=Decimal("25.00"), desc="Analyse L1 / L2")
        off2 = upsert_offer(db, tutor_id=tutor.id, subject="Python", price=Decimal("30.00"), desc="Bases → Avancé")

        bk1 = upsert_booking(db, offer_id=off1.id, student_id=student.id, status=BookingStatus.PENDING)

        print("Seed OK ✅")
        print(f"Tutor:   {tutor.id}  {tutor.email}")
        print(f"Student: {student.id}  {student.email}")
        print(f"Offer 1: {off1.id}  {off1.subject}")
        print(f"Offer 2: {off2.id}  {off2.subject}")
        print(f"Booking: {bk1.id}  offer={bk1.offer_id} student={bk1.student_id} status={bk1.status}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Supprimer les données avant de reseeder")
    parser.add_argument("--keep-users", action="store_true", help="Conserver les users lors du reset (ne supprime que offers + bookings)")
    args = parser.parse_args()

    run(keep_users=args.keep_users, do_reset=args.reset)
