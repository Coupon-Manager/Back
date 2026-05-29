from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select, func
from database import get_session
from models import User, Supplier, Coupon
from api.deps import get_current_user

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


class CreateSupplierRequest(BaseModel):
    name: str
    logo_url: str | None = None


class SupplierBalance(BaseModel):
    id: int
    name: str
    logo_url: str | None
    available_balance: int


@router.post("", response_model=Supplier, status_code=status.HTTP_201_CREATED)
def create_supplier(
    body: CreateSupplierRequest,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    supplier = Supplier(name=body.name, logo_url=body.logo_url)
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@router.get("", response_model=list[SupplierBalance])
def list_suppliers(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    suppliers = session.exec(select(Supplier)).all()
    result = []
    for s in suppliers:
        balance = session.exec(
            select(func.coalesce(func.sum(Coupon.value), 0))
            .where(Coupon.supplier_id == s.id)
            .where(Coupon.used == False)
        ).one()
        result.append(SupplierBalance(
            id=s.id,
            name=s.name,
            color=s.color,
            logo_url=s.logo_url,
            available_balance=balance,
        ))
    return result


@router.get("/{supplier_id}/coupons", response_model=list[Coupon])
def list_supplier_coupons(
    supplier_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    supplier = session.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return session.exec(select(Coupon).where(Coupon.supplier_id == supplier_id)).all()
