from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlmodel import Session
from database import get_session
from models import Coupon, User
from api.deps import get_current_user
from workers.email_importer import import_emails
from pydantic import BaseModel

router = APIRouter(prefix="/import", tags=["import"])


class ImportResult(BaseModel):
    imported: int
    skipped: int
    coupons: list[Coupon]


@router.post("/email", response_model=ImportResult)
def run_email_import(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return import_emails(session, added_by_id=current_user.id)
