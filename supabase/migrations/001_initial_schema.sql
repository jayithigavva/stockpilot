-- StockPilot Supabase Schema
-- Multi-tenant inventory management system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Brands table (multi-tenant)
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_brands_slug ON brands(slug);

-- Users table (linked to Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_brand_id ON users(brand_id);
CREATE INDEX idx_users_email ON users(email);

-- Suppliers table
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    contact_email TEXT,
    contact_phone TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_suppliers_brand_id ON suppliers(brand_id);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Cost parameters
    unit_cost DECIMAL(10, 2) NOT NULL,
    selling_price DECIMAL(10, 2) NOT NULL,
    holding_cost_rate DECIMAL(5, 4) DEFAULT 0.02,
    markdown_rate DECIMAL(5, 4) DEFAULT 0.0,
    churn_penalty DECIMAL(10, 2) DEFAULT 0.0,
    
    -- Supplier info
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    min_order_quantity DECIMAL(10, 2) DEFAULT 0,
    order_multiple DECIMAL(10, 2) DEFAULT 1.0,
    lead_time_days INTEGER DEFAULT 14,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(brand_id, sku)
);

CREATE INDEX idx_products_brand_id ON products(brand_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_supplier_id ON products(supplier_id);

-- Inventory table
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID UNIQUE NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    current_quantity DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
    reserved_quantity DECIMAL(10, 2) DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_inventory_product_id ON inventory(product_id);

-- Sales history table
CREATE TABLE sales_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    date TIMESTAMPTZ NOT NULL,
    demand DECIMAL(10, 2) NOT NULL,
    revenue DECIMAL(10, 2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sales_history_product_id ON sales_history(product_id);
CREATE INDEX idx_sales_history_date ON sales_history(date);

-- Risk category enum
CREATE TYPE risk_category AS ENUM ('LOW', 'MEDIUM', 'HIGH');

-- Decision status enum
CREATE TYPE decision_status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'EXECUTED');

-- Reorder decisions table
CREATE TABLE reorder_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    
    -- Decision details
    recommended_quantity DECIMAL(10, 2) NOT NULL,
    current_inventory DECIMAL(10, 2) NOT NULL,
    stockout_probability_before DECIMAL(5, 4) NOT NULL,
    stockout_probability_after DECIMAL(5, 4) NOT NULL,
    risk_category_before risk_category NOT NULL,
    risk_category_after risk_category NOT NULL,
    
    -- Economic impact
    expected_overstock_cost DECIMAL(10, 2) NOT NULL,
    expected_understock_cost DECIMAL(10, 2) NOT NULL,
    total_expected_loss DECIMAL(10, 2) NOT NULL,
    cash_locked DECIMAL(10, 2) NOT NULL,
    cash_freed DECIMAL(10, 2) DEFAULT 0.0,
    
    -- Status
    status decision_status DEFAULT 'PENDING' NOT NULL,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_reorder_decisions_brand_id ON reorder_decisions(brand_id);
CREATE INDEX idx_reorder_decisions_product_id ON reorder_decisions(product_id);
CREATE INDEX idx_reorder_decisions_status ON reorder_decisions(status);

-- Decision logs table
CREATE TABLE decision_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_id UUID NOT NULL REFERENCES reorder_decisions(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_decision_logs_decision_id ON decision_logs(decision_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_brands_updated_at BEFORE UPDATE ON brands
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_last_updated BEFORE UPDATE ON inventory
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

