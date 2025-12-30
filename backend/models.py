"""
Database models for multi-tenant inventory management system.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base
import uuid


def generate_uuid():
    """Generate UUID for primary keys."""
    return str(uuid.uuid4())


class User(Base):
    """User accounts for brand owners/managers."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brands = relationship("Brand", back_populates="owner", cascade="all, delete-orphan")


class Brand(Base):
    """D2C brand/organization (multi-tenant isolation)."""
    __tablename__ = "brands"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    currency = Column(String, default="INR")
    timezone = Column(String, default="Asia/Kolkata")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="brands")
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="brand", cascade="all, delete-orphan")
    decisions = relationship("ReorderDecision", back_populates="brand", cascade="all, delete-orphan")
    decision_logs = relationship("DecisionLog", back_populates="brand", cascade="all, delete-orphan")


class Product(Base):
    """Product/SKU definition."""
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False, index=True)
    sku = Column(String, nullable=False)  # SKU code
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Cost parameters
    unit_cost = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    holding_cost_rate = Column(Float, default=0.02)  # 2% per month
    markdown_rate = Column(Float, default=0.0)
    churn_penalty = Column(Float, default=0.0)
    
    # Supplier constraints
    supplier_id = Column(String, ForeignKey("suppliers.id"), nullable=True)
    min_order_quantity = Column(Float, default=0)
    order_multiple = Column(Float, default=1.0)
    lead_time_days = Column(Integer, default=14)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    sales_history = relationship("SalesHistory", back_populates="product", cascade="all, delete-orphan")
    decisions = relationship("ReorderDecision", back_populates="product", cascade="all, delete-orphan")


class Supplier(Base):
    """Supplier information."""
    __tablename__ = "suppliers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    payment_terms = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier")


class Inventory(Base):
    """Current inventory levels per product."""
    __tablename__ = "inventory"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, unique=True, index=True)
    current_quantity = Column(Float, default=0.0, nullable=False)
    reserved_quantity = Column(Float, default=0.0)  # For pending orders
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory")


class SalesHistory(Base):
    """Historical sales data for demand forecasting."""
    __tablename__ = "sales_history"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    demand = Column(Float, nullable=False)  # Sales quantity
    revenue = Column(Float, nullable=True)  # Optional revenue tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="sales_history")
    
    # Index for efficient querying
    __table_args__ = (
        {"postgresql_indexes": [
            {"name": "idx_sales_product_date", "columns": ["product_id", "date"]}
        ]},
    )


class ReorderDecision(Base):
    """AI-generated reorder recommendations."""
    __tablename__ = "reorder_decisions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    
    # Decision details
    recommended_quantity = Column(Float, nullable=False)
    current_inventory = Column(Float, nullable=False)
    stockout_probability_before = Column(Float, nullable=False)
    stockout_probability_after = Column(Float, nullable=False)
    risk_category_before = Column(String, nullable=False)  # LOW, MEDIUM, HIGH
    risk_category_after = Column(String, nullable=False)
    
    # Economic metrics
    expected_overstock_cost = Column(Float, nullable=False)
    expected_understock_cost = Column(Float, nullable=False)
    total_expected_loss = Column(Float, nullable=False)
    cash_locked = Column(Float, nullable=False)
    cash_freed = Column(Float, default=0.0)  # If reducing order vs baseline
    
    # Comparison metrics (if baseline provided)
    baseline_quantity = Column(Float, nullable=True)
    loss_reduction = Column(Float, nullable=True)
    loss_reduction_pct = Column(Float, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, accepted, rejected
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    accepted_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Forecast metadata
    forecast_horizon_days = Column(Integer, default=30)
    lead_time_days = Column(Integer, nullable=False)
    n_simulations = Column(Integer, default=5000)
    
    # Raw forecast data (JSON)
    forecast_data = Column(JSON, nullable=True)  # Store forecast DataFrame as JSON
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="decisions")
    product = relationship("Product", back_populates="decisions")
    logs = relationship("DecisionLog", back_populates="decision", cascade="all, delete-orphan")


class DecisionLog(Base):
    """Audit log for decision actions."""
    __tablename__ = "decision_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    brand_id = Column(String, ForeignKey("brands.id"), nullable=False, index=True)
    decision_id = Column(String, ForeignKey("reorder_decisions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    action = Column(String, nullable=False)  # created, accepted, rejected, modified
    previous_state = Column(JSON, nullable=True)  # Snapshot before action
    new_state = Column(JSON, nullable=True)  # Snapshot after action
    
    # Inventory impact
    inventory_before = Column(Float, nullable=True)
    inventory_after = Column(Float, nullable=True)
    cash_impact = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="decision_logs")
    decision = relationship("ReorderDecision", back_populates="logs")

