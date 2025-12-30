"""
FastAPI main application with all endpoints.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from backend.database import get_db, engine, Base
from backend.models import User, Brand, Product, Supplier, Inventory, SalesHistory, ReorderDecision
from backend.schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    BrandCreate, BrandResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    SupplierCreate, SupplierResponse,
    InventoryResponse, InventoryUpdate,
    SalesHistoryUpload, SalesHistoryResponse,
    ReorderDecisionResponse, DecisionAcceptRequest, DecisionRejectRequest,
    RunAIRequest, RunAIResponse, DashboardSummary
)
from backend.auth import (
    get_current_user, get_user_brand, get_password_hash, verify_password,
    create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.services import InventoryService
from datetime import timedelta

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockPilot API",
    description="AI-driven inventory management for D2C brands",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== AUTHENTICATION ====================

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create default brand for user
    brand = Brand(
        name=f"{user_data.full_name or user_data.email}'s Brand",
        owner_id=user.id
    )
    db.add(brand)
    db.commit()
    
    return user


@app.post("/api/auth/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user


# ==================== BRANDS ====================

@app.get("/api/brands", response_model=BrandResponse)
def get_brand(brand: Brand = Depends(get_user_brand)):
    """Get user's brand."""
    return brand


@app.put("/api/brands", response_model=BrandResponse)
def update_brand(
    brand_data: BrandCreate,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Update brand information."""
    brand.name = brand_data.name
    brand.currency = brand_data.currency
    brand.timezone = brand_data.timezone
    db.commit()
    db.refresh(brand)
    return brand


# ==================== PRODUCTS ====================

@app.post("/api/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Create a new product."""
    product = Product(
        brand_id=brand.id,
        **product_data.dict()
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Create inventory record
    inventory = Inventory(product_id=product.id, current_quantity=0.0)
    db.add(inventory)
    db.commit()
    
    return product


@app.get("/api/products", response_model=List[ProductResponse])
def list_products(
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """List all products for brand."""
    products = db.query(Product).filter(Product.brand_id == brand.id).all()
    return products


@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Get product details."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_data: ProductUpdate,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Update product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


# ==================== INVENTORY ====================

@app.get("/api/inventory", response_model=List[InventoryResponse])
def list_inventory(
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """List inventory for all products."""
    products = db.query(Product).filter(Product.brand_id == brand.id).all()
    product_ids = [p.id for p in products]
    inventory = db.query(Inventory).filter(Inventory.product_id.in_(product_ids)).all()
    return inventory


@app.get("/api/inventory/{product_id}", response_model=InventoryResponse)
def get_inventory(
    product_id: str,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Get inventory for a product."""
    # Verify product belongs to brand
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


@app.put("/api/inventory/{product_id}", response_model=InventoryResponse)
def update_inventory(
    product_id: str,
    inventory_data: InventoryUpdate,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually update inventory."""
    # Verify product belongs to brand
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory.current_quantity = inventory_data.current_quantity
    inventory.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(inventory)
    return inventory


# ==================== SALES HISTORY ====================

@app.post("/api/sales/upload", response_model=List[SalesHistoryResponse])
def upload_sales_history(
    sales_data: SalesHistoryUpload,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Upload sales history for a product."""
    # Verify product belongs to brand
    product = db.query(Product).filter(
        Product.id == sales_data.product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete existing sales history (optional - you might want to append instead)
    db.query(SalesHistory).filter(SalesHistory.product_id == sales_data.product_id).delete()
    
    # Create new records
    records = []
    for data_point in sales_data.sales_data:
        record = SalesHistory(
            product_id=sales_data.product_id,
            date=datetime.fromisoformat(data_point.date),
            demand=data_point.demand,
            revenue=data_point.revenue
        )
        records.append(record)
        db.add(record)
    
    db.commit()
    return records


@app.get("/api/sales/{product_id}", response_model=List[SalesHistoryResponse])
def get_sales_history(
    product_id: str,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Get sales history for a product."""
    # Verify product belongs to brand
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.brand_id == brand.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    sales = db.query(SalesHistory).filter(
        SalesHistory.product_id == product_id
    ).order_by(SalesHistory.date).all()
    return sales


# ==================== SUPPLIERS ====================

@app.post("/api/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier_data: SupplierCreate,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Create a supplier."""
    supplier = Supplier(
        brand_id=brand.id,
        **supplier_data.dict()
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@app.get("/api/suppliers", response_model=List[SupplierResponse])
def list_suppliers(
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """List all suppliers."""
    suppliers = db.query(Supplier).filter(Supplier.brand_id == brand.id).all()
    return suppliers


# ==================== AI DECISIONS ====================

@app.post("/api/ai/run", response_model=RunAIResponse)
def run_ai_analysis(
    request: RunAIRequest,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Run AI analysis and generate reorder decisions."""
    service = InventoryService(db)
    
    try:
        decisions = service.generate_decisions_for_brand(
            brand_id=brand.id,
            product_ids=request.product_ids,
            available_cash=request.available_cash,
            baseline_quantities=request.baseline_quantities or {}
        )
        
        total_cash = sum(d.cash_locked for d in decisions)
        product_ids = [d.product_id for d in decisions]
        
        return RunAIResponse(
            decisions_created=len(decisions),
            product_ids=product_ids,
            total_cash_required=total_cash,
            message=f"Generated {len(decisions)} reorder recommendations"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/decisions", response_model=List[ReorderDecisionResponse])
def list_decisions(
    status_filter: Optional[str] = None,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """List reorder decisions."""
    query = db.query(ReorderDecision).filter(ReorderDecision.brand_id == brand.id)
    
    if status_filter:
        query = query.filter(ReorderDecision.status == status_filter)
    
    decisions = query.order_by(ReorderDecision.created_at.desc()).limit(50).all()
    return decisions


@app.get("/api/decisions/{decision_id}", response_model=ReorderDecisionResponse)
def get_decision(
    decision_id: str,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Get decision details."""
    decision = db.query(ReorderDecision).filter(
        ReorderDecision.id == decision_id,
        ReorderDecision.brand_id == brand.id
    ).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@app.post("/api/decisions/{decision_id}/accept", response_model=ReorderDecisionResponse)
def accept_decision(
    decision_id: str,
    request: DecisionAcceptRequest,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept a reorder decision."""
    # Verify decision belongs to brand
    decision = db.query(ReorderDecision).filter(
        ReorderDecision.id == decision_id,
        ReorderDecision.brand_id == brand.id
    ).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    service = InventoryService(db)
    try:
        decision = service.accept_decision(
            decision_id=decision_id,
            user_id=current_user.id,
            notes=request.notes
        )
        return decision
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/decisions/{decision_id}/reject", response_model=ReorderDecisionResponse)
def reject_decision(
    decision_id: str,
    request: DecisionRejectRequest,
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject a reorder decision."""
    # Verify decision belongs to brand
    decision = db.query(ReorderDecision).filter(
        ReorderDecision.id == decision_id,
        ReorderDecision.brand_id == brand.id
    ).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    service = InventoryService(db)
    try:
        decision = service.reject_decision(
            decision_id=decision_id,
            user_id=current_user.id,
            reason=request.reason
        )
        return decision
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== DASHBOARD ====================

@app.get("/api/dashboard", response_model=DashboardSummary)
def get_dashboard(
    brand: Brand = Depends(get_user_brand),
    db: Session = Depends(get_db)
):
    """Get dashboard summary."""
    # Total products
    total_products = db.query(Product).filter(
        Product.brand_id == brand.id,
        Product.is_active == True
    ).count()
    
    # Inventory value
    products = db.query(Product).filter(
        Product.brand_id == brand.id,
        Product.is_active == True
    ).all()
    product_ids = [p.id for p in products]
    
    inventory_records = db.query(Inventory).filter(
        Inventory.product_id.in_(product_ids)
    ).all()
    
    product_dict = {p.id: p for p in products}
    total_inventory_value = sum(
        inv.current_quantity * product_dict[inv.product_id].unit_cost
        for inv in inventory_records
    )
    total_cash_locked = total_inventory_value
    
    # High risk products (from recent decisions)
    recent_decisions = db.query(ReorderDecision).filter(
        ReorderDecision.brand_id == brand.id,
        ReorderDecision.status == "pending"
    ).order_by(ReorderDecision.created_at.desc()).limit(10).all()
    
    high_risk_count = sum(
        1 for d in recent_decisions
        if d.risk_category_before in ["HIGH", "MEDIUM"]
    )
    
    pending_decisions = len(recent_decisions)
    
    return DashboardSummary(
        total_products=total_products,
        total_inventory_value=total_inventory_value,
        total_cash_locked=total_cash_locked,
        high_risk_products=high_risk_count,
        pending_decisions=pending_decisions,
        recent_decisions=[ReorderDecisionResponse.from_orm(d) for d in recent_decisions]
    )


# ==================== HEALTH CHECK ====================

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "stockpilot-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

