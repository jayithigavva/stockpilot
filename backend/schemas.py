"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Authentication Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Brand Schemas
class BrandCreate(BaseModel):
    name: str
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"


class BrandResponse(BaseModel):
    id: str
    name: str
    currency: str
    timezone: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    unit_cost: float
    selling_price: float
    holding_cost_rate: float = 0.02
    markdown_rate: float = 0.0
    churn_penalty: float = 0.0
    supplier_id: Optional[str] = None
    min_order_quantity: float = 0
    order_multiple: float = 1.0
    lead_time_days: int = 14


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    unit_cost: Optional[float] = None
    selling_price: Optional[float] = None
    holding_cost_rate: Optional[float] = None
    markdown_rate: Optional[float] = None
    churn_penalty: Optional[float] = None
    supplier_id: Optional[str] = None
    min_order_quantity: Optional[float] = None
    order_multiple: Optional[float] = None
    lead_time_days: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: str
    brand_id: str
    sku: str
    name: str
    description: Optional[str]
    unit_cost: float
    selling_price: float
    holding_cost_rate: float
    markdown_rate: float
    churn_penalty: float
    supplier_id: Optional[str]
    min_order_quantity: float
    order_multiple: float
    lead_time_days: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Supplier Schemas
class SupplierCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None


class SupplierResponse(BaseModel):
    id: str
    brand_id: str
    name: str
    contact_email: Optional[str]
    contact_phone: Optional[str]
    address: Optional[str]
    payment_terms: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Inventory Schemas
class InventoryResponse(BaseModel):
    id: str
    product_id: str
    current_quantity: float
    reserved_quantity: float
    last_updated: datetime
    
    class Config:
        from_attributes = True


class InventoryUpdate(BaseModel):
    current_quantity: float
    notes: Optional[str] = None


# Sales History Schemas
class SalesDataPoint(BaseModel):
    date: str  # YYYY-MM-DD
    demand: float
    revenue: Optional[float] = None


class SalesHistoryUpload(BaseModel):
    product_id: str
    sales_data: List[SalesDataPoint]


class SalesHistoryResponse(BaseModel):
    id: str
    product_id: str
    date: datetime
    demand: float
    revenue: Optional[float]
    
    class Config:
        from_attributes = True


# Reorder Decision Schemas
class DecisionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ReorderDecisionResponse(BaseModel):
    id: str
    brand_id: str
    product_id: str
    recommended_quantity: float
    current_inventory: float
    stockout_probability_before: float
    stockout_probability_after: float
    risk_category_before: str
    risk_category_after: str
    expected_overstock_cost: float
    expected_understock_cost: float
    total_expected_loss: float
    cash_locked: float
    cash_freed: float
    baseline_quantity: Optional[float]
    loss_reduction: Optional[float]
    loss_reduction_pct: Optional[float]
    status: str
    accepted_at: Optional[datetime]
    lead_time_days: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DecisionAcceptRequest(BaseModel):
    decision_id: str
    notes: Optional[str] = None


class DecisionRejectRequest(BaseModel):
    decision_id: str
    reason: Optional[str] = None


# AI Run Request
class RunAIRequest(BaseModel):
    product_ids: Optional[List[str]] = None  # None = all products
    available_cash: Optional[float] = None
    baseline_quantities: Optional[Dict[str, float]] = None


class RunAIResponse(BaseModel):
    decisions_created: int
    product_ids: List[str]
    total_cash_required: float
    message: str


# Dashboard Summary
class DashboardSummary(BaseModel):
    total_products: int
    total_inventory_value: float
    total_cash_locked: float
    high_risk_products: int
    pending_decisions: int
    recent_decisions: List[ReorderDecisionResponse]

