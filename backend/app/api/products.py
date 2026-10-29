from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.rate_limit import limit_products_read, limit_products_write
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut
from app.services import product_service

router = APIRouter()


@router.get("", response_model=List[ProductOut], include_in_schema=False, dependencies=[Depends(limit_products_read)])
@router.get("/", response_model=List[ProductOut], dependencies=[Depends(limit_products_read)])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    q: Optional[str] = Query(None, description="Search by product name (case-insensitive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return product_service.list_products(db, current_user.id, q=q, skip=skip, limit=limit)


@router.post("", response_model=ProductOut, include_in_schema=False, dependencies=[Depends(limit_products_write)])
@router.post("/", response_model=ProductOut, dependencies=[Depends(limit_products_write)])
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_service.create_product(db, current_user.id, payload)


@router.get("/{product_id}", response_model=ProductOut, dependencies=[Depends(limit_products_read)])
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return product_service.get_product(db, current_user.id, product_id)
