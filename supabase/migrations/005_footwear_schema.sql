-- Footwear-Specific Schema Extensions
-- Extends existing schema to support style-level decisions with size coupling

-- Styles table (style-level product grouping)
CREATE TABLE styles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    style_code TEXT NOT NULL,
    category TEXT, -- e.g., 'sneakers', 'boots', 'sandals'
    gender TEXT, -- 'men', 'women', 'unisex'
    base_unit_cost DECIMAL(10, 2) NOT NULL,
    base_selling_price DECIMAL(10, 2) NOT NULL,
    lead_time_days INTEGER DEFAULT 60, -- Footwear typically 30-90 days
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(brand_id, style_code)
);

CREATE INDEX idx_styles_brand_id ON styles(brand_id);
CREATE INDEX idx_styles_style_code ON styles(style_code);

-- Link existing products to styles (additive, doesn't break existing)
ALTER TABLE products ADD COLUMN IF NOT EXISTS style_id UUID REFERENCES styles(id) ON DELETE SET NULL;
ALTER TABLE products ADD COLUMN IF NOT EXISTS size TEXT; -- "6", "7", "8", "9", "10", "11", etc.
ALTER TABLE products ADD COLUMN IF NOT EXISTS color TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS width TEXT; -- "N", "M", "W" (narrow, medium, wide)

CREATE INDEX idx_products_style_id ON products(style_id);
CREATE INDEX idx_products_size ON products(size);

-- Size profiles (historical size-share distribution)
CREATE TABLE size_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    style_id UUID NOT NULL REFERENCES styles(id) ON DELETE CASCADE,
    size TEXT NOT NULL,
    historical_share DECIMAL(5, 4) NOT NULL, -- e.g., 0.20 = 20% of style demand
    sample_size INTEGER DEFAULT 0, -- Number of sales used to compute share
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(style_id, size)
);

CREATE INDEX idx_size_profiles_style_id ON size_profiles(style_id);

-- Size curve templates (factory-valid size distributions)
CREATE TABLE size_curves (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    style_id UUID NOT NULL REFERENCES styles(id) ON DELETE CASCADE,
    name TEXT, -- e.g., "Standard Curve", "Wide Curve"
    size_distribution JSONB NOT NULL, -- {"6": 0.05, "7": 0.10, "8": 0.20, "9": 0.30, "10": 0.20, "11": 0.15}
    min_order_total INTEGER NOT NULL, -- Minimum total units for this curve
    order_multiple INTEGER DEFAULT 1, -- Must order in multiples of this
    factory_valid BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_size_curves_style_id ON size_curves(style_id);

-- Reorder plans (style-level decisions with size breakdown)
-- This extends reorder_decisions to be style-level
ALTER TABLE reorder_decisions ADD COLUMN IF NOT EXISTS style_id UUID REFERENCES styles(id) ON DELETE CASCADE;
ALTER TABLE reorder_decisions ADD COLUMN IF NOT EXISTS size_curve_id UUID REFERENCES size_curves(id) ON DELETE SET NULL;
ALTER TABLE reorder_decisions ADD COLUMN IF NOT EXISTS size_breakdown JSONB; -- {"6": 50, "7": 100, "8": 200, "9": 300, "10": 200, "11": 150}
ALTER TABLE reorder_decisions ADD COLUMN IF NOT EXISTS size_risk_breakdown JSONB; -- {"6": "HIGH", "7": "MEDIUM", "8": "LOW", ...}
ALTER TABLE reorder_decisions ADD COLUMN IF NOT EXISTS size_cash_at_risk JSONB; -- {"6": 50000, "7": 100000, ...}
ALTER TABLE reorder_decisions ADD COLUMN IF NOT EXISTS size_expected_loss JSONB; -- {"6": {"overstock": 20000, "understock": 0}, ...}

CREATE INDEX idx_reorder_decisions_style_id ON reorder_decisions(style_id);

-- Helper function to get style-level inventory
CREATE OR REPLACE FUNCTION get_style_inventory(style_uuid UUID)
RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT jsonb_object_agg(
            p.size,
            COALESCE(i.current_quantity, 0)
        )
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
        WHERE p.style_id = style_uuid
        GROUP BY p.style_id
    );
END;
$$ LANGUAGE plpgsql;

-- Helper function to get style-level sales history
CREATE OR REPLACE FUNCTION get_style_sales_history(style_uuid UUID, days_back INTEGER DEFAULT 365)
RETURNS TABLE (
    date TIMESTAMPTZ,
    size TEXT,
    demand DECIMAL(10, 2),
    revenue DECIMAL(10, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        sh.date,
        p.size,
        sh.demand,
        sh.revenue
    FROM sales_history sh
    JOIN products p ON p.id = sh.product_id
    WHERE p.style_id = style_uuid
      AND sh.date >= NOW() - (days_back || ' days')::INTERVAL
    ORDER BY sh.date, p.size;
END;
$$ LANGUAGE plpgsql;

