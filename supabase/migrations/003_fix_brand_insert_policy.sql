-- Fix RLS policy to allow brand creation during registration
-- This allows authenticated users to create brands when they register

-- Drop existing policies if they exist (to allow re-running)
DROP POLICY IF EXISTS "Authenticated users can create brands" ON brands;
DROP POLICY IF EXISTS "Authenticated users can view brands by slug" ON brands;
DROP POLICY IF EXISTS "Users can insert their own profile" ON users;

-- Allow authenticated users to insert brands (for registration)
-- This is needed because during registration, the user doesn't have a brand_id yet
CREATE POLICY "Authenticated users can create brands"
    ON brands FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Allow authenticated users to view brands by slug (needed during registration)
-- This allows checking if a brand already exists when trying to register
CREATE POLICY "Authenticated users can view brands by slug"
    ON brands FOR SELECT
    TO authenticated
    USING (true);

-- Also allow users to insert into users table during registration
-- Users can only insert their own profile (id must match auth.uid())
CREATE POLICY "Users can insert their own profile"
    ON users FOR INSERT
    TO authenticated
    WITH CHECK (id = auth.uid());

