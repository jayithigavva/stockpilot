# Vercel Deployment Guide for StockPilot

## Prerequisites
- GitHub repository connected (✅ Done)
- Vercel account (sign up at https://vercel.com)

## Step 1: Deploy Frontend to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com
   - Sign in with GitHub

2. **Import Your Project**
   - Click "Add New Project"
   - Select your GitHub repository: `jayithigavva/stockpilot`
   - Vercel will auto-detect it's a Next.js project

3. **Configure Project Settings**
   - **Root Directory**: Set to `frontend` (important!)
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Set Environment Variables**
   Click "Environment Variables" and add:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```
   Replace `your-backend-url.com` with your actual backend URL (see Backend Deployment below)

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (2-3 minutes)

### Option B: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

4. **Deploy**
   ```bash
   vercel
   ```
   - Follow the prompts
   - When asked for root directory, confirm it's `frontend`
   - Set environment variable: `NEXT_PUBLIC_API_URL`

5. **Set Environment Variable**
   ```bash
   vercel env add NEXT_PUBLIC_API_URL
   ```
   Enter your backend URL when prompted

## Step 2: Deploy Backend (Required Before Frontend Works)

Your FastAPI backend needs to be deployed separately. Options:

### Option A: Railway (Recommended for FastAPI)
1. Go to https://railway.app
2. Sign in with GitHub
3. Create new project → Deploy from GitHub
4. Select your repository
5. Set root directory to `backend`
6. Add environment variables:
   - `DATABASE_URL` (PostgreSQL connection string)
   - `SECRET_KEY` (generate a random string)
   - `CORS_ORIGINS` (your Vercel frontend URL)
7. Railway will auto-detect Python and install dependencies

### Option B: Render
1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as Railway)

### Option C: DigitalOcean App Platform
Similar process to Render

## Step 3: Update Frontend Environment Variable

Once your backend is deployed:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to your backend URL
3. Redeploy (or it will auto-redeploy)

## Step 4: Configure CORS in Backend

Make sure your backend `backend/app/core/config.py` has:

```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://your-vercel-app.vercel.app",  # Add your Vercel URL
]
```

## Important Notes

- **Root Directory**: Vercel needs to know the frontend is in the `frontend/` folder
- **Environment Variables**: `NEXT_PUBLIC_*` variables are exposed to the browser
- **Backend First**: Deploy backend before frontend, or frontend won't work
- **Database**: You'll need a PostgreSQL database (Supabase, Railway, Render all offer free tiers)

## Quick Checklist

- [ ] Backend deployed and running
- [ ] Backend URL obtained
- [ ] Frontend deployed to Vercel
- [ ] `NEXT_PUBLIC_API_URL` environment variable set in Vercel
- [ ] CORS configured in backend to allow Vercel domain
- [ ] Test the deployed frontend

## Troubleshooting

**Build Fails:**
- Check that root directory is set to `frontend`
- Verify `package.json` exists in `frontend/`
- Check build logs in Vercel dashboard

**API Calls Fail:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend CORS settings
- Ensure backend is running and accessible

**Images Not Loading:**
- Check image paths in components
- Verify images are in `frontend/public/`

