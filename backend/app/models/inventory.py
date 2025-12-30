"""
Inventory, Product, and Supplier models.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class Product(Base):
    """Product/SKU model."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    sku = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Cost parameters
    unit_cost = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    holding_cost_rate = Column(Float, default=0.02)  # 2% per month
    markdown_rate = Column(Float, default=0.0)
    churn_penalty = Column(Float, default=0.0)
    
    # Supplier info
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
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


class Inventory(Base):
    """Current inventory levels."""
    
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    current_quantity = Column(Float, nullable=False, default=0.0)
    reserved_quantity = Column(Float, default=0.0)  # For pending orders
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="inventory")


class Supplier(Base):
    """Supplier model."""
    
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    name = Column(String, nullable=False)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier")


class SalesHistory(Base):
    """Historical sales data for forecasting."""
    
    __tablename__ = "sales_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    demand = Column(Float, nullable=False)  # Units sold
    revenue = Column(Float, nullable=True)  # Optional revenue tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="sales_history")


class RiskCategory(str, Enum):
    """Risk category enum."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DecisionStatus(str, Enum):
    """Reorder decision status."""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class ReorderDecision(Base):
    """AI-generated reorder decision."""
    
    __tablename__ = "reorder_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Decision details
    recommended_quantity = Column(Float, nullable=False)
    current_inventory = Column(Float, nullable=False)
    stockout_probability_before = Column(Float, nullable=False)
    stockout_probability_after = Column(Float, nullable=False)
    risk_category_before = Column(SQLEnum(RiskCategory), nullable=False)
    risk_category_after = Column(SQLEnum(RiskCategory), nullable=False)
    
    # Economic impact
    expected_overstock_cost = Column(Float, nullable=False)
    expected_understock_cost = Column(Float, nullable=False)
    total_expected_loss = Column(Float, nullable=False)
    cash_locked = Column(Float, nullable=False)
    cash_freed = Column(Float, default=0.0)
    
    # Status
    status = Column(SQLEnum(DecisionStatus), default=DecisionStatus.PENDING, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    brand = relationship("Brand", back_populates="decisions")
    product = relationship("Product", back_populates="decisions")


class DecisionLog(Base):
    """Audit log for decision actions."""
    
    __tablename__ = "decision_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("reorder_decisions.id"), nullable=False)
    action = Column(String, nullable=False)  # "CREATED", "ACCEPTED", "REJECTED", "EXECUTED"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    decision = relationship("ReorderDecision")

