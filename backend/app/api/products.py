"""
Product management endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.inventory import Product, Inventory
from app.api.schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all products for the user's brand."""
    products = db.query(Product).filter(
        Product.brand_id == current_user.brand_id,
        Product.is_active == True
    ).all()
    
    # Add inventory info
    result = []
    for product in products:
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        product_dict = {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "unit_cost": product.unit_cost,
            "selling_price": product.selling_price,
            "lead_time_days": product.lead_time_days,
            "current_inventory": inventory.current_quantity if inventory else 0.0,
            # Footwear fields
            "style_id": product.style_id,
            "size": product.size,
            "color": product.color,
            "width": product.width,
        }
        result.append(product_dict)
    
    return result


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new product."""
    # Check if SKU already exists for this brand
    existing = db.query(Product).filter(
        Product.brand_id == current_user.brand_id,
        Product.sku == product_data.sku
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists for this brand"
        )
    
    # Create product
    product = Product(
        brand_id=current_user.brand_id,
        **product_data.dict()
    )
    
    db.add(product)
    db.flush()
    
    # Create inventory record
    inventory = Inventory(
        product_id=product.id,
        current_quantity=0.0
    )
    db.add(inventory)
    
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "unit_cost": product.unit_cost,
        "selling_price": product.selling_price,
        "lead_time_days": product.lead_time_days,
        "current_inventory": 0.0
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == current_user.brand_id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    
    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "unit_cost": product.unit_cost,
        "selling_price": product.selling_price,
        "lead_time_days": product.lead_time_days,
        "current_inventory": inventory.current_quantity if inventory else 0.0
    }

