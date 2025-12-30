# Supabase Backend Setup Guide for StockPilot

This guide will help you set up Supabase as the backend for StockPilot, replacing the FastAPI backend.

## Prerequisites

- Supabase account (sign up at https://supabase.com - FREE tier available)
- GitHub repository connected
- Vercel account (for frontend deployment)

## Step 1: Create Supabase Project

1. **Go to Supabase Dashboard**
   - Visit https://supabase.com
   - Sign in or create account
   - Click "New Project"

2. **Configure Project**
   - **Name**: `stockpilot` (or your choice)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Free tier is perfect for MVP

3. **Wait for Setup** (2-3 minutes)

## Step 2: Run Database Migrations

1. **Go to SQL Editor** in Supabase dashboard

2. **Run Migration 1**: Copy and paste contents of `supabase/migrations/001_initial_schema.sql`
   - Click "Run" to execute

3. **Run Migration 2**: Copy and paste contents of `supabase/migrations/002_row_level_security.sql`
   - Click "Run" to execute

4. **Verify Tables**: Go to "Table Editor" and verify all tables are created:
   - brands
   - users
   - suppliers
   - products
   - inventory
   - sales_history
   - reorder_decisions
   - decision_logs

## Step 3: Set Up Authentication

1. **Go to Authentication → Settings** in Supabase dashboard

2. **Enable Email Auth** (should be enabled by default)

3. **Configure Site URL**:
   - Add your Vercel frontend URL: `https://your-app.vercel.app`
   - Add localhost for development: `http://localhost:3000`

4. **Disable Email Confirmations** (for MVP, optional):
   - Go to Authentication → Settings
   - Toggle "Enable email confirmations" to OFF (for faster testing)

## Step 4: Deploy Edge Function

1. **Install Supabase CLI** (if not installed):
   
   **On macOS (using Homebrew):**
   ```bash
   brew install supabase/tap/supabase
   ```
   
   **On Linux:**
   ```bash
   # Download binary
   curl -fsSL https://github.com/supabase/cli/releases/latest/download/supabase_linux_amd64.tar.gz | tar -xz
   sudo mv supabase /usr/local/bin/
   ```
   
   **On Windows:**
   ```bash
   # Using Scoop
   scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
   scoop install supabase
   ```
   
   **Or use npx (no installation needed):**
   ```bash
   npx supabase --help
   ```

2. **Login to Supabase**:
   ```bash
   supabase login
   ```

3. **Link Your Project**:
   ```bash
   cd /path/to/stockpilot
   supabase link --project-ref YOUR_PROJECT_REF
   ```
   (Find your project ref in Supabase dashboard → Settings → API)

4. **Deploy Edge Function**:

   **Option A: Using Supabase Dashboard (Easier - Recommended for MVP)**
   - Go to Supabase Dashboard → Edge Functions
   - Click "Create a new function"
   - Function name: `generate-decisions`
   - Copy contents of `supabase/functions/generate-decisions/index.ts`
   - Paste into the function editor
   - Click "Deploy"

   **Option B: Using CLI**
   ```bash
   supabase link --project-ref YOUR_PROJECT_REF
   supabase functions deploy generate-decisions
   ```
   (Find your project ref in Supabase Dashboard → Settings → API)

## Step 5: Update Frontend

1. **Install Supabase Client**:
   ```bash
   cd frontend
   npm install @supabase/supabase-js
   ```

2. **Get Supabase Credentials**:
   - Go to Supabase Dashboard → Settings → API
   - Copy:
     - `Project URL` (NEXT_PUBLIC_SUPABASE_URL)
     - `anon public` key (NEXT_PUBLIC_SUPABASE_ANON_KEY)

3. **Update Vercel Environment Variables**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
     NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
     ```
   - Remove old `NEXT_PUBLIC_API_URL` (no longer needed)

4. **Update Frontend Code**:
   - Replace imports from `lib/api.ts` to `lib/supabase.ts`
   - Example:
     ```typescript
     // Old
     import { authAPI } from '@/lib/api'
     
     // New
     import { authAPI } from '@/lib/supabase'
     ```

## Step 6: Update Frontend Components

Update all components that use the old API:

1. **Login/Register Pages**: Already updated to use `authAPI` from supabase
2. **Product Pages**: Update to use `productsAPI` from supabase
3. **Decision Pages**: Update to use `decisionsAPI` from supabase
4. **Dashboard**: Update to use `dashboardAPI` from supabase

## Step 7: Test the Setup

1. **Test Registration**:
   - Go to your Vercel-deployed frontend
   - Try registering a new user
   - Check Supabase Dashboard → Authentication → Users

2. **Test Login**:
   - Login with created user
   - Verify session is created

3. **Test Products**:
   - Create a product
   - Verify it appears in Supabase Table Editor → products

4. **Test Decisions**:
   - Generate a decision
   - Verify it appears in reorder_decisions table

## Environment Variables Summary

### Vercel (Frontend)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

### Supabase Edge Functions
Set in Supabase Dashboard → Edge Functions → Settings:
- `SUPABASE_URL` (auto-set)
- `SUPABASE_ANON_KEY` (auto-set)

## Database Schema Overview

- **brands**: Multi-tenant brands
- **users**: User profiles (linked to Supabase Auth)
- **products**: Product/SKU information
- **inventory**: Current inventory levels
- **sales_history**: Historical sales data
- **reorder_decisions**: AI-generated recommendations
- **decision_logs**: Audit trail
- **suppliers**: Supplier information

## Row Level Security (RLS)

All tables have RLS enabled. Users can only:
- See data from their own brand
- Modify data for their own brand
- Access is automatically filtered by `brand_id`

## Troubleshooting

### "Unauthorized" errors
- Check that user is logged in
- Verify RLS policies are applied
- Check user's `brand_id` is set correctly

### "Function not found" errors
- Verify Edge Function is deployed
- Check function name matches: `generate-decisions`
- Verify function has correct permissions

### Database connection errors
- Verify Supabase URL and keys are correct
- Check environment variables in Vercel
- Ensure Supabase project is active

### RLS blocking queries
- Verify user has `brand_id` set in `users` table
- Check RLS policies are correctly applied
- Test with Supabase Dashboard → Table Editor (bypasses RLS)

## Cost

**Supabase Free Tier Includes:**
- 500MB database
- 2GB bandwidth
- 50,000 monthly active users
- 2GB file storage
- 500MB edge function invocations

**Perfect for MVP!** ✅

## Next Steps

1. ✅ Supabase project created
2. ✅ Migrations run
3. ✅ Edge function deployed
4. ✅ Frontend updated
5. ✅ Environment variables set
6. ✅ Test registration/login
7. ✅ Test product creation
8. ✅ Test decision generation

## Support

- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Supabase GitHub: https://github.com/supabase/supabase

