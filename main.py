from fastapi import FastAPI
from database import create_db_and_tables
import models  # noqa: F401 — ensures all SQLModel tables are registered before create_all

app = FastAPI(title="Barcode Coupon Manager")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
