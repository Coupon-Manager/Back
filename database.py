import os
from typing import Any
from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://coupon:coupon@localhost:5432/coupon")

engine = create_engine(DATABASE_URL)


def UTCDateTimeField(**kwargs: Any) -> Any:
    return Field(sa_column=Column(DateTime(timezone=True)), **kwargs)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
