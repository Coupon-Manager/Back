from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
import models  # noqa: F401
from api.auth import router as auth_router
from api.suppliers import router as suppliers_router
from api.coupons import router as coupons_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Barcode Coupon Manager", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(suppliers_router)
app.include_router(coupons_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
