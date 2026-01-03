"""
Inventory, Product, Supplier, and Footwear models.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class Product(Base):
    """Product/SKU model (can be linked to a Style for footwear)."""
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    sku = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Footwear-specific fields (nullable for backward compatibility)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=True, index=True)
    size = Column(String, nullable=True, index=True)  # "6", "7", "8", "9", "10", "11"
    color = Column(String, nullable=True)
    width = Column(String, nullable=True)  # "N", "M", "W"
    
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
    style = relationship("Style", back_populates="products")
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
    """AI-generated reorder decision (style-level for footwear, product-level for others)."""
    
    __tablename__ = "reorder_decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Nullable for style-level decisions
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=True, index=True)  # For footwear
    
    # Decision details
    recommended_quantity = Column(Float, nullable=False)  # Total units for style-level
    current_inventory = Column(Float, nullable=False)
    stockout_probability_before = Column(Float, nullable=False)
    stockout_probability_after = Column(Float, nullable=False)
    risk_category_before = Column(SQLEnum(RiskCategory), nullable=False)
    risk_category_after = Column(SQLEnum(RiskCategory), nullable=False)
    
    # Footwear-specific fields
    size_curve_id = Column(Integer, ForeignKey("size_curves.id"), nullable=True)
    size_breakdown = Column(JSON, nullable=True)  # {"6": 50, "7": 100, "8": 200, ...}
    size_risk_breakdown = Column(JSON, nullable=True)  # {"6": "HIGH", "7": "MEDIUM", ...}
    size_cash_at_risk = Column(JSON, nullable=True)  # {"6": 50000, "7": 100000, ...}
    size_expected_loss = Column(JSON, nullable=True)  # {"6": {"overstock": 20000, "understock": 0}, ...}
    
    # Economic impact
    expected_overstock_cost = Column(Float, nullable=False)
    expected_understock_cost = Column(Float, nullable=False)
    total_expected_loss = Column(Float, nullable=False)
    cash_locked = Column(Float, nullable=False)
    cash_freed = Column(Float, default=0.0)
    cash_at_risk = Column(Float, nullable=True)  # Cash in high-risk sizes (footwear)
    
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
    style = relationship("Style", back_populates="decisions")
    size_curve = relationship("SizeCurve", back_populates="decisions")


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


class Style(Base):
    """Footwear style model (style-level product grouping)."""
    
    __tablename__ = "styles"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    name = Column(String, nullable=False)
    style_code = Column(String, nullable=False, index=True)
    category = Column(String, nullable=True)  # e.g., 'sneakers', 'boots', 'sandals'
    gender = Column(String, nullable=True)  # 'men', 'women', 'unisex'
    
    # Cost parameters (base values, can vary by size)
    base_unit_cost = Column(Float, nullable=False)
    base_selling_price = Column(Float, nullable=False)
    lead_time_days = Column(Integer, default=60)  # Footwear typically 30-90 days
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="styles")
    products = relationship("Product", back_populates="style")
    size_profiles = relationship("SizeProfile", back_populates="style", cascade="all, delete-orphan")
    size_curves = relationship("SizeCurve", back_populates="style", cascade="all, delete-orphan")
    decisions = relationship("ReorderDecision", back_populates="style")


class SizeProfile(Base):
    """Historical size-share distribution for a style."""
    
    __tablename__ = "size_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=False, index=True)
    size = Column(String, nullable=False)  # "6", "7", "8", "9", "10", "11"
    historical_share = Column(Float, nullable=False)  # e.g., 0.20 = 20% of style demand
    sample_size = Column(Integer, default=0)  # Number of sales used to compute share
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    style = relationship("Style", back_populates="size_profiles")


class SizeCurve(Base):
    """Factory-valid size distribution curve for a style."""
    
    __tablename__ = "size_curves"
    
    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=False, index=True)
    name = Column(String, nullable=True)  # e.g., "Standard Curve", "Wide Curve"
    size_distribution = Column(JSON, nullable=False)  # {"6": 0.05, "7": 0.10, "8": 0.20, ...}
    min_order_total = Column(Integer, nullable=False)  # Minimum total units for this curve
    order_multiple = Column(Integer, default=1)  # Must order in multiples of this
    factory_valid = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    style = relationship("Style", back_populates="size_curves")
    decisions = relationship("ReorderDecision", back_populates="size_curve")

