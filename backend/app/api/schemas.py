"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.inventory import RiskCategory, DecisionStatus


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    brand_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Product schemas
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    unit_cost: float
    selling_price: float
    holding_cost_rate: Optional[float] = 0.02
    markdown_rate: Optional[float] = 0.0
    churn_penalty: Optional[float] = 0.0
    supplier_id: Optional[int] = None
    min_order_quantity: Optional[float] = 0
    order_multiple: Optional[float] = 1.0
    lead_time_days: Optional[int] = 14


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    unit_cost: float
    selling_price: float
    lead_time_days: int
    current_inventory: Optional[float] = None
    
    class Config:
        from_attributes = True


# Inventory schemas
class InventoryUpdate(BaseModel):
    current_quantity: float


# Sales history schemas
class SalesDataUpload(BaseModel):
    product_id: int
    date: datetime
    demand: float
    revenue: Optional[float] = None


class SalesDataBulkUpload(BaseModel):
    data: List[SalesDataUpload]


# Decision schemas
class ReorderRecommendation(BaseModel):
    product_id: int
    product_name: str
    recommended_quantity: float
    current_inventory: float
    stockout_probability_before: float
    stockout_probability_after: float
    risk_category_before: RiskCategory
    risk_category_after: RiskCategory
    expected_overstock_cost: float
    expected_understock_cost: float
    total_expected_loss: float
    cash_locked: float
    cash_freed: float
    explanation: str


class DecisionAccept(BaseModel):
    decision_id: int
    notes: Optional[str] = None


class DecisionResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    recommended_quantity: float
    status: DecisionStatus
    cash_locked: float
    stockout_probability_after: float
    risk_category_after: RiskCategory
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardStats(BaseModel):
    total_products: int
    total_inventory_value: float
    total_cash_locked: float
    high_risk_products: int
    pending_decisions: int
    recent_decisions: List[DecisionResponse]

