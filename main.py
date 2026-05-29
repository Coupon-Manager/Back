import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from database import create_db_and_tables, get_session
import models  # noqa: F401
from api.auth import router as auth_router
from api.suppliers import router as suppliers_router
from api.coupons import router as coupons_router
from api.import_email import router as import_router
from workers.email_importer import import_emails

SYSTEM_USER_ID = int(os.getenv("SYSTEM_USER_ID", "1"))


def scheduled_email_import():
    with next(get_session()) as session:
        import_emails(session, added_by_id=SYSTEM_USER_ID)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_email_import, "cron", hour=6)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Barcode Coupon Manager", lifespan=lifespan)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(suppliers_router)
app.include_router(coupons_router)
app.include_router(import_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
