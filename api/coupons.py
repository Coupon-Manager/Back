from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from database import get_session
from models import User, Coupon
from api.deps import get_current_user

router = APIRouter(prefix="/coupons", tags=["coupons"])


class CreateCouponRequest(BaseModel):
    supplier_id: int
    value: int
    code: str | None = None


@router.post("", response_model=Coupon, status_code=status.HTTP_201_CREATED)
def create_coupon(
    body: CreateCouponRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    coupon = Coupon(
        supplier_id=body.supplier_id,
        value=body.value,
        code=body.code,
        added_by_id=current_user.id,
    )
    session.add(coupon)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Coupon code already exists")
    session.refresh(coupon)
    return coupon


@router.patch("/{coupon_id}/use", response_model=Coupon)
def use_coupon(
    coupon_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    coupon = session.get(Coupon, coupon_id)
    if not coupon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    if coupon.used:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Coupon already used")
    coupon.used = True
    coupon.used_at = datetime.utcnow()
    session.add(coupon)
    session.commit()
    session.refresh(coupon)
    return coupon
