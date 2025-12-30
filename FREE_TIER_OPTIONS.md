# Free Tier Deployment Options for StockPilot

## 🆓 Completely Free Options

### Option 1: Vercel (Frontend) + Railway (Backend) - **BEST FREE OPTION**

**Frontend - Vercel (FREE)**
- ✅ Unlimited deployments
- ✅ Free SSL certificates
- ✅ Global CDN
- ✅ Automatic deployments from GitHub
- ✅ 100GB bandwidth/month
- **Cost: $0/month**

**Backend - Railway (FREE)**
- ✅ $5 free credit/month (usually enough for small apps)
- ✅ PostgreSQL database included
- ✅ Auto-deploys from GitHub
- ✅ Free SSL
- **Cost: $0/month** (if you stay within $5 credit)

**Total: $0/month** (if usage stays low)

---

### Option 2: Vercel (Frontend) + Render (Backend) - **ALSO FREE**

**Frontend - Vercel (FREE)**
- Same as above
- **Cost: $0/month**

**Backend - Render (FREE)**
- ✅ Free tier available
- ✅ PostgreSQL database (free tier: 90 days, then $7/month)
- ✅ Auto-deploys from GitHub
- ⚠️ Spins down after 15 minutes of inactivity (wakes up on request)
- **Cost: $0/month** (first 90 days, then $7/month for database)

**Total: $0/month** (first 90 days), then $7/month

---

### Option 3: Vercel (Frontend) + Supabase (Backend) - **FREE BUT LIMITED**

**Frontend - Vercel (FREE)**
- Same as above
- **Cost: $0/month**

**Backend - Supabase (FREE)**
- ✅ PostgreSQL database (500MB free)
- ✅ 2GB bandwidth/month
- ✅ API auto-generated
- ⚠️ You'd need to rewrite backend to use Supabase functions
- **Cost: $0/month**

**Total: $0/month** (but requires code changes)

---

## 💰 Low-Cost Options (Almost Free)

### Option 4: Vercel (Frontend) + DigitalOcean (Backend)

**Frontend - Vercel (FREE)**
- **Cost: $0/month**

**Backend - DigitalOcean**
- ❌ No free tier for App Platform
- ✅ But has $200 free credit for new users (lasts ~3-4 months)
- Database: $7/month (Dev Database)
- **Cost: $0/month** (first 3-4 months with credit), then $7/month

**Total: $0/month** (with credit), then $7/month

---

## 🏆 Recommended: Railway (Best Free Option)

### Why Railway?

1. **Truly Free**: $5 credit/month is usually enough for MVP
2. **Easy Setup**: Just connect GitHub and deploy
3. **Database Included**: PostgreSQL comes with it
4. **No Spindown**: Unlike Render, stays awake
5. **Simple**: No complex configuration needed

### Railway Setup (Free Tier)

1. **Sign up**: https://railway.app (use GitHub login)
2. **Create Project**: "New Project" → "Deploy from GitHub"
3. **Select Repo**: `jayithigavva/stockpilot`
4. **Configure**:
   - Root Directory: `backend`
   - Build Command: (auto-detected)
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Add Database**: Click "+ New" → "Database" → "PostgreSQL"
6. **Environment Variables**:
   - `DATABASE_URL` (auto-set by Railway)
   - `SECRET_KEY` (generate one)
   - `CORS_ORIGINS` (your Vercel URL)

**Cost: $0/month** (within $5 credit limit)

---

## 📊 Comparison Table

| Service | Frontend | Backend | Database | Total Cost |
|---------|----------|---------|----------|------------|
| **Railway** | Vercel (Free) | Railway (Free) | Included | **$0/month** ✅ |
| **Render** | Vercel (Free) | Render (Free) | Free 90 days | **$0-7/month** |
| **DigitalOcean** | Vercel (Free) | $200 credit | $7/month | **$0-7/month** |
| **Supabase** | Vercel (Free) | Rewrite needed | Free | **$0/month** ⚠️ |

---

## 🎯 My Recommendation

**For completely free MVP:**
1. **Frontend**: Deploy to Vercel (free)
2. **Backend**: Deploy to Railway (free tier)
3. **Database**: Use Railway's PostgreSQL (included)

**Total: $0/month** ✅

Railway's $5 credit is usually enough for:
- Small backend API
- Low traffic
- Development/testing
- MVP launch

If you exceed $5/month, you'll be charged only for what you use (usually still very cheap).

---

## 🚀 Quick Start (Free Tier)

### Step 1: Deploy Frontend to Vercel (Free)
- Follow `VERCEL_DEPLOYMENT.md`
- **Cost: $0**

### Step 2: Deploy Backend to Railway (Free)
1. Go to https://railway.app
2. Sign in with GitHub
3. New Project → Deploy from GitHub
4. Select `jayithigavva/stockpilot`
5. Set root directory to `backend`
6. Add PostgreSQL database
7. Set environment variables
8. Deploy!

**Cost: $0/month** (within credit)

### Step 3: Connect Them
- Update Vercel env var: `NEXT_PUBLIC_API_URL` = your Railway backend URL
- Done! 🎉

---

## ⚠️ Free Tier Limitations

**Railway Free Tier:**
- $5 credit/month
- If exceeded, pay-as-you-go (usually $1-5 more)
- No custom domain on free tier

**Vercel Free Tier:**
- 100GB bandwidth/month
- Unlimited deployments
- Perfect for MVP

**Render Free Tier:**
- Spins down after 15 min inactivity
- 90-day database trial
- Then $7/month for database

---

## 💡 When to Upgrade

Upgrade when:
- You have paying customers
- Traffic exceeds free tier limits
- You need custom domains
- You need 24/7 uptime guarantees

But for MVP/testing: **Free tier is perfect!** ✅

