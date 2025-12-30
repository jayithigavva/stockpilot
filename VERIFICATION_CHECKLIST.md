# StockPilot Verification Checklist

## ✅ Frontend Configuration (Vercel Deployment)

### 1. Path Alias Configuration
- ✅ `tsconfig.json` - Path alias `@/*` configured correctly
- ✅ `next.config.js` - Webpack alias for `@/` added for Vercel compatibility
- ✅ All imports using `@/lib/supabase` are correct

### 2. Build Configuration
- ✅ `next.config.js` - Clean configuration without conflicting webpack rules
- ✅ `package.json` - All dependencies properly defined
- ✅ Old `src/` directory renamed to `src-old/` to prevent build conflicts
- ✅ Unused `lib/api.ts` removed

### 3. TypeScript Configuration
- ✅ `tsconfig.json` - Proper module resolution and path aliases
- ✅ All TypeScript errors fixed in:
  - `app/dashboard/page.tsx`
  - `app/decisions/page.tsx`
  - `app/login/page.tsx`
  - `app/register/page.tsx`

### 4. Dynamic Pages
- ✅ All Supabase-dependent pages marked as `force-dynamic`:
  - Login page
  - Register page
  - Dashboard page
  - Decisions page

## ✅ Supabase Backend Configuration

### 1. Database Schema
- ✅ `001_initial_schema.sql` - All tables created correctly
- ✅ Foreign key relationships properly defined
- ✅ Indexes created for performance

### 2. Row Level Security (RLS)
- ✅ `002_row_level_security.sql` - RLS enabled on all tables
- ✅ Helper function `get_user_brand_id()` created
- ✅ Policies for SELECT and UPDATE operations

### 3. Registration Fix (NEW)
- ✅ `003_fix_brand_insert_policy.sql` - Migration created to fix registration
- ✅ INSERT policy for `brands` table (allows authenticated users to create brands)
- ✅ INSERT policy for `users` table (allows users to create their own profile)
- ✅ SELECT policy for `brands` table (allows checking if brand exists during registration)

## ✅ Registration Flow

### Current Flow:
1. User signs up with Supabase Auth ✅
2. Create brand in `brands` table ✅ (requires INSERT policy)
3. Create user profile in `users` table ✅ (requires INSERT policy)
4. If brand exists, use existing brand ✅ (requires SELECT policy)

### Files Involved:
- `frontend/lib/supabase.ts` - Registration logic
- `frontend/app/register/page.tsx` - Registration UI
- `supabase/migrations/003_fix_brand_insert_policy.sql` - RLS policies for registration

## ⚠️ Action Required

### To Fix Registration Issue:
1. Go to Supabase Dashboard → SQL Editor
2. Run the migration: `supabase/migrations/003_fix_brand_insert_policy.sql`
3. This will add the necessary INSERT and SELECT policies

## 📝 Notes

- The `brands` table SELECT policy now allows authenticated users to view brands (needed for registration checks)
- This is safe because `brands` table only contains `name` and `slug` (not sensitive data)
- Sensitive data (products, inventory) is still protected by brand_id-based RLS policies
- All other RLS policies remain intact and secure

