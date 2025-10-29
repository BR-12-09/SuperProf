# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import time
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.routers.health import health_router
from app.routers.user import user_router
from app.routers.offer import offer_router, booking_router
from app.database import BaseSQL, engine

def wait_for_db(max_retries: int = 60, delay_sec: float = 1.0):
    # Attend que Postgres soit prêt (jusqu'à ~60s)
    for _ in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            time.sleep(delay_sec)
    raise RuntimeError("Database not ready after waiting")

@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()  # <-- important
    BaseSQL.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="SuperProf-like API",
    description="Minimal MVP: Users, Offers, Bookings",
    version="0.0.1",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(offer_router)
app.include_router(booking_router)
