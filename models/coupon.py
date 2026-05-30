from __future__ import annotations
from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from database import UTCDateTimeField


class Coupon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id")
    value: int
    code: Optional[str] = Field(default=None, unique=True)
    used: bool = False
    created_at: datetime = UTCDateTimeField(default_factory=lambda: datetime.now(timezone.utc))
    used_at: Optional[datetime] = UTCDateTimeField(default=None)
    added_by_id: int = Field(foreign_key="user.id")
