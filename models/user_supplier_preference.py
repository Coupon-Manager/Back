from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field


class UserSupplierPreference(SQLModel, table=True):
    __tablename__ = "user_supplier_preferences"

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id", primary_key=True)
    color: Optional[str] = None
