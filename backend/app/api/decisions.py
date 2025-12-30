"""
Reorder decision endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.inventory import (
    Product, Inventory, SalesHistory, ReorderDecision,
    DecisionLog, DecisionStatus, RiskCategory
)
from app.api.schemas import (
    ReorderRecommendation, DecisionAccept, DecisionResponse
)

router = APIRouter(prefix="/decisions", tags=["decisions"])

# Lazy load AI service to avoid import errors at startup
_ai_service = None

def get_ai_service():
    """Get or create AI service instance (lazy loading)."""
    global _ai_service
    if _ai_service is None:
        try:
            from app.services.ai_service import AIService
            _ai_service = AIService()
        except Exception as e:
            # If AI service can't be loaded (e.g., LightGBM issues), return None
            # The endpoint will handle this gracefully
            print(f"Warning: AI service not available: {e}")
            return None
    return _ai_service


@router.post("/generate", response_model=List[ReorderRecommendation])
def generate_recommendations(
    product_ids: Optional[List[int]] = None,
    available_cash: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI-driven reorder recommendations."""
    # Get products
    query = db.query(Product).filter(
        Product.brand_id == current_user.brand_id,
        Product.is_active == True
    )
    
    if product_ids:
        query = query.filter(Product.id.in_(product_ids))
    
    products = query.all()
    
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No products found"
        )
    
    # Get inventories and sales history
    inventories = {}
    sales_histories = {}
    
    for product in products:
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        if inventory:
            inventories[product.id] = inventory
        
        # Get sales history (last 365 days minimum)
        sales = db.query(SalesHistory).filter(
            SalesHistory.product_id == product.id
        ).order_by(SalesHistory.date.desc()).limit(365).all()
        
        if sales:
            sales_histories[product.id] = list(reversed(sales))  # Oldest first
    
    # Filter products with sales history
    products_with_data = [
        p for p in products
        if p.id in inventories and p.id in sales_histories
    ]
    
    if not products_with_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No products with sufficient sales history"
        )
    
    # Generate recommendations
    recommendations = []
    
    for product in products_with_data:
        try:
            ai_service = get_ai_service()
            if ai_service is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service is not available. Please ensure LightGBM is properly installed."
                )
            
            rec = ai_service.generate_recommendation(
                product=product,
                current_inventory=inventories[product.id],
                sales_history=sales_histories[product.id],
                available_cash=None  # Individual product, no allocation
            )
            
            # Create decision record
            decision = ReorderDecision(
                brand_id=current_user.brand_id,
                product_id=product.id,
                recommended_quantity=rec['recommended_quantity'],
                current_inventory=rec['current_inventory'],
                stockout_probability_before=rec['stockout_probability_before'],
                stockout_probability_after=rec['stockout_probability_after'],
                risk_category_before=rec['risk_category_before'],
                risk_category_after=rec['risk_category_after'],
                expected_overstock_cost=rec['expected_overstock_cost'],
                expected_understock_cost=rec['expected_understock_cost'],
                total_expected_loss=rec['total_expected_loss'],
                cash_locked=rec['cash_locked'],
                cash_freed=rec['cash_freed'],
                status=DecisionStatus.PENDING,
                created_by_user_id=current_user.id
            )
            
            db.add(decision)
            db.flush()
            
            # Create log entry
            log = DecisionLog(
                decision_id=decision.id,
                action="CREATED",
                user_id=current_user.id
            )
            db.add(log)
            
            recommendations.append({
                "product_id": product.id,
                "product_name": product.name,
                "recommended_quantity": rec['recommended_quantity'],
                "current_inventory": rec['current_inventory'],
                "stockout_probability_before": rec['stockout_probability_before'],
                "stockout_probability_after": rec['stockout_probability_after'],
                "risk_category_before": rec['risk_category_before'],
                "risk_category_after": rec['risk_category_after'],
                "expected_overstock_cost": rec['expected_overstock_cost'],
                "expected_understock_cost": rec['expected_understock_cost'],
                "total_expected_loss": rec['total_expected_loss'],
                "cash_locked": rec['cash_locked'],
                "cash_freed": rec['cash_freed'],
                "explanation": rec['explanation']
            })
            
        except Exception as e:
            # Log error but continue
            print(f"Error generating recommendation for product {product.id}: {e}")
            continue
    
    db.commit()
    
    return recommendations


@router.get("", response_model=List[DecisionResponse])
def list_decisions(
    status_filter: Optional[DecisionStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all decisions for the brand."""
    query = db.query(ReorderDecision).filter(
        ReorderDecision.brand_id == current_user.brand_id
    )
    
    if status_filter:
        query = query.filter(ReorderDecision.status == status_filter)
    
    decisions = query.order_by(ReorderDecision.created_at.desc()).limit(50).all()
    
    result = []
    for decision in decisions:
        product = db.query(Product).filter(Product.id == decision.product_id).first()
        result.append({
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
    
    return result


@router.get("/recommendations", response_model=List[ReorderRecommendation])
def get_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get pending recommendations with full details."""
    decisions = db.query(ReorderDecision).filter(
        ReorderDecision.brand_id == current_user.brand_id,
        ReorderDecision.status == DecisionStatus.PENDING
    ).order_by(ReorderDecision.created_at.desc()).all()
    
    result = []
    for decision in decisions:
        product = db.query(Product).filter(Product.id == decision.product_id).first()
        if not product:
            continue
        
        result.append({
            "product_id": decision.product_id,
            "product_name": product.name,
            "recommended_quantity": decision.recommended_quantity,
            "current_inventory": decision.current_inventory,
            "stockout_probability_before": decision.stockout_probability_before,
            "stockout_probability_after": decision.stockout_probability_after,
            "risk_category_before": decision.risk_category_before,
            "risk_category_after": decision.risk_category_after,
            "expected_overstock_cost": decision.expected_overstock_cost,
            "expected_understock_cost": decision.expected_understock_cost,
            "total_expected_loss": decision.total_expected_loss,
            "cash_locked": decision.cash_locked,
            "cash_freed": decision.cash_freed,
            "explanation": f"Order {decision.recommended_quantity:.0f} units to reduce stockout risk from {(decision.stockout_probability_before*100):.1f}% to {(decision.stockout_probability_after*100):.1f}%. Cash locked: ₹{decision.cash_locked:,.0f}."
        })
    
    return result


@router.post("/{decision_id}/accept", response_model=DecisionResponse)
def accept_decision(
    decision_id: int,
    accept_data: DecisionAccept,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Accept a reorder decision and update inventory."""
    decision = db.query(ReorderDecision).filter(
        ReorderDecision.id == decision_id,
        ReorderDecision.brand_id == current_user.brand_id,
        ReorderDecision.status == DecisionStatus.PENDING
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found or already processed"
        )
    
    # Update inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == decision.product_id).first()
    if inventory:
        inventory.current_quantity += decision.recommended_quantity
        inventory.last_updated = datetime.utcnow()
    
    # Update decision status
    decision.status = DecisionStatus.ACCEPTED
    decision.accepted_at = datetime.utcnow()
    
    # Create log entry
    log = DecisionLog(
        decision_id=decision.id,
        action="ACCEPTED",
        user_id=current_user.id,
        notes=accept_data.notes
    )
    db.add(log)
    
    db.commit()
    db.refresh(decision)
    
    product = db.query(Product).filter(Product.id == decision.product_id).first()
    
    return {
        "id": decision.id,
        "product_id": decision.product_id,
        "product_name": product.name if product else "Unknown",
        "recommended_quantity": decision.recommended_quantity,
        "status": decision.status,
        "cash_locked": decision.cash_locked,
        "stockout_probability_after": decision.stockout_probability_after,
        "risk_category_after": decision.risk_category_after,
        "created_at": decision.created_at
    }


@router.post("/{decision_id}/reject")
def reject_decision(
    decision_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reject a reorder decision."""
    decision = db.query(ReorderDecision).filter(
        ReorderDecision.id == decision_id,
        ReorderDecision.brand_id == current_user.brand_id,
        ReorderDecision.status == DecisionStatus.PENDING
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found or already processed"
        )
    
    decision.status = DecisionStatus.REJECTED
    
    # Create log entry
    log = DecisionLog(
        decision_id=decision.id,
        action="REJECTED",
        user_id=current_user.id,
        notes=notes
    )
    db.add(log)
    
    db.commit()
    
    return {"message": "Decision rejected"}

