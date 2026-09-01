from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product, ProductListing
from app.schemas.product import ProductCreate


def create_product(db: Session, owner_id: UUID, payload: ProductCreate) -> Product:
    product = Product(owner_id=owner_id, name=payload.name, brand=payload.brand, category=payload.category)
    db.add(product)
    db.flush()  # get product.id before adding listings

    for listing in payload.listings:
        db.add(
            ProductListing(
                product_id=product.id,
                source=listing.source,
                url=listing.url,
                tracking_frequency_minutes=listing.tracking_frequency_minutes,
            )
        )

    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session, owner_id: UUID):
    return db.query(Product).filter(Product.owner_id == owner_id).all()


def get_product(db: Session, owner_id: UUID, product_id: UUID) -> Product:
    product = db.query(Product).filter(Product.id == product_id, Product.owner_id == owner_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
