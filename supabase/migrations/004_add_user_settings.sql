-- Add user settings and free plan tracking

-- Add settings columns to brands table
ALTER TABLE brands 
ADD COLUMN IF NOT EXISTS available_cash DECIMAL(10, 2) DEFAULT 0,
ADD COLUMN IF NOT EXISTS free_plan_started_at TIMESTAMPTZ DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS plan_type TEXT DEFAULT 'free';

-- Create index for plan queries
CREATE INDEX IF NOT EXISTS idx_brands_plan_type ON brands(plan_type);

