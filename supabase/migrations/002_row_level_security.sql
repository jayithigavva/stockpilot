-- Row Level Security (RLS) Policies for Multi-Tenancy

-- Enable RLS on all tables
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE reorder_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE decision_logs ENABLE ROW LEVEL SECURITY;

-- Helper function to get user's brand_id
CREATE OR REPLACE FUNCTION get_user_brand_id()
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT brand_id FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Brands policies
CREATE POLICY "Users can view their own brand"
    ON brands FOR SELECT
    USING (id = get_user_brand_id());

CREATE POLICY "Users can update their own brand"
    ON brands FOR UPDATE
    USING (id = get_user_brand_id());

-- Users policies
CREATE POLICY "Users can view users in their brand"
    ON users FOR SELECT
    USING (brand_id = get_user_brand_id());

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (id = auth.uid());

-- Suppliers policies
CREATE POLICY "Users can manage suppliers in their brand"
    ON suppliers FOR ALL
    USING (brand_id = get_user_brand_id());

-- Products policies
CREATE POLICY "Users can manage products in their brand"
    ON products FOR ALL
    USING (brand_id = get_user_brand_id());

-- Inventory policies
CREATE POLICY "Users can manage inventory for their brand's products"
    ON inventory FOR ALL
    USING (
        product_id IN (
            SELECT id FROM products WHERE brand_id = get_user_brand_id()
        )
    );

-- Sales history policies
CREATE POLICY "Users can manage sales history for their brand's products"
    ON sales_history FOR ALL
    USING (
        product_id IN (
            SELECT id FROM products WHERE brand_id = get_user_brand_id()
        )
    );

-- Reorder decisions policies
CREATE POLICY "Users can manage decisions for their brand"
    ON reorder_decisions FOR ALL
    USING (brand_id = get_user_brand_id());

-- Decision logs policies
CREATE POLICY "Users can view logs for their brand's decisions"
    ON decision_logs FOR SELECT
    USING (
        decision_id IN (
            SELECT id FROM reorder_decisions WHERE brand_id = get_user_brand_id()
        )
    );

CREATE POLICY "Users can create logs for their brand's decisions"
    ON decision_logs FOR INSERT
    WITH CHECK (
        decision_id IN (
            SELECT id FROM reorder_decisions WHERE brand_id = get_user_brand_id()
        )
    );

