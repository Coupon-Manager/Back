from typing import Optional
from sqlmodel import SQLModel, Field


class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    color: Optional[str] = None
    logo_url: Optional[str] = None
