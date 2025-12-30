"""
Dashboard endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.inventory import Product, Inventory, ReorderDecision, DecisionStatus, RiskCategory
from app.api.schemas import DashboardStats, DecisionResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard statistics."""
    brand_id = current_user.brand_id
    
    # Total products
    total_products = db.query(Product).filter(
        Product.brand_id == brand_id,
        Product.is_active == True
    ).count()
    
    # Total inventory value
    inventory_value = db.query(
        func.sum(Inventory.current_quantity * Product.unit_cost)
    ).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Product.brand_id == brand_id
    ).scalar() or 0.0
    
    # Total cash locked (from pending decisions)
    pending_decisions = db.query(ReorderDecision).filter(
        ReorderDecision.brand_id == brand_id,
        ReorderDecision.status == DecisionStatus.PENDING
    ).all()
    
    total_cash_locked = sum(d.cash_locked for d in pending_decisions)
    
    # High risk products (need to compute from recent decisions or inventory)
    # For now, count products with pending decisions that have high risk
    high_risk_products = db.query(ReorderDecision).filter(
        ReorderDecision.brand_id == brand_id,
        ReorderDecision.status == DecisionStatus.PENDING,
        ReorderDecision.risk_category_before == RiskCategory.HIGH
    ).distinct(ReorderDecision.product_id).count()
    
    # Pending decisions count
    pending_count = len(pending_decisions)
    
    # Recent decisions
    recent_decisions = db.query(ReorderDecision).filter(
        ReorderDecision.brand_id == brand_id
    ).order_by(ReorderDecision.created_at.desc()).limit(10).all()
    
    recent_decisions_list = []
    for decision in recent_decisions:
        product = db.query(Product).filter(Product.id == decision.product_id).first()
        recent_decisions_list.append({
            "id": decision.id,
            "product_id": decision.product_id,
            "product_name": product.name if product else "Unknown",
            "recommended_quantity": decision.recommended_quantity,
            "status": decision.status,
            "cash_locked": decision.cash_locked,
            "stockout_probability_after": decision.stockout_probability_after,
            "risk_category_after": decision.risk_category_after,
            "created_at": decision.created_at
        })
    
    return {
        "total_products": total_products,
        "total_inventory_value": inventory_value,
        "total_cash_locked": total_cash_locked,
        "high_risk_products": high_risk_products,
        "pending_decisions": pending_count,
        "recent_decisions": recent_decisions_list
    }

