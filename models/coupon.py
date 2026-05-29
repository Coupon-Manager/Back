from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Coupon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id")
    value: int
    code: Optional[str] = None
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = None
    added_by_id: int = Field(foreign_key="user.id")
