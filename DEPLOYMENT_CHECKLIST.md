# Deployment Checklist - What Needs to Be Connected

## 🎯 Recommended Setup (MVP)

**Frontend**: Vercel (Free)  
**Backend**: Render or Railway (Free tier)  
**Database**: Supabase (Free tier)  

---

## 📋 Step-by-Step Deployment

### 1️⃣ Database: Supabase (PostgreSQL)

**Why Supabase?**
- Free tier: 500MB database, 2GB bandwidth
- Easy PostgreSQL setup
- Web dashboard for database management
- Connection pooling included

**Steps:**
1. Go to https://supabase.com
2. Sign up / Login
3. Create new project
4. Wait for database to provision (~2 minutes)
5. Go to **Settings → Database**
6. Copy the **Connection String** (URI format)
   - Looks like: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres`

**What you need:**
- ✅ Supabase project URL
- ✅ Database connection string
- ✅ Database password (save this!)

---

### 2️⃣ Backend: Render or Railway

#### Option A: Render (Easier)

**Steps:**
1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New +" → "Web Service"**
4. Connect your GitHub repo
5. Configure:
   - **Name**: `stockpilot-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables:
   ```
   DATABASE_URL=<your-supabase-connection-string>
   SECRET_KEY=<generate-random-secret>
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   APP_NAME=StockPilot
   DEBUG=False
   ```
7. Deploy!

**Cost**: Free tier (spins down after inactivity), or $7/month for always-on

#### Option B: Railway (Alternative)

**Steps:**
1. Go to https://railway.app
2. Sign up with GitHub
3. **"New Project" → "Deploy from GitHub repo"**
4. Select your repo
5. Add **PostgreSQL** service (or use Supabase)
6. Set environment variables (same as Render)
7. Deploy!

**Cost**: $5 credit/month free, then pay-as-you-go

**What you need:**
- ✅ Backend URL (e.g., `https://stockpilot-backend.onrender.com`)
- ✅ Environment variables set

---

### 3️⃣ Frontend: Vercel

**Steps:**
1. Go to https://vercel.com
2. Sign up with GitHub
3. **"Add New Project"**
4. Import your GitHub repo
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
6. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```
7. Deploy!

**Cost**: Free for hobby projects

**What you need:**
- ✅ Frontend URL (e.g., `https://stockpilot.vercel.app`)

---

## 🔗 Connection Flow

```
User Browser
    ↓
Frontend (Vercel)
    ↓ (API calls)
Backend (Render/Railway)
    ↓ (Database queries)
Database (Supabase)
```

---

## 🔐 Environment Variables Needed

### Backend (.env on Render/Railway)
```bash
DATABASE_URL=postgresql://postgres:xxx@db.xxx.supabase.co:5432/postgres
SECRET_KEY=<generate-with: openssl rand -hex 32>
CORS_ORIGINS=["https://your-app.vercel.app"]
APP_NAME=StockPilot
DEBUG=False
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256
```

### Frontend (.env on Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 📝 Pre-Deployment Checklist

### Backend
- [ ] Code pushed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] Database migrations ready (or tables auto-create)
- [ ] Environment variables documented
- [ ] CORS origins configured

### Frontend
- [ ] Code pushed to GitHub
- [ ] `package.json` has build script
- [ ] Environment variables documented
- [ ] API URL points to backend

### Database
- [ ] Supabase project created
- [ ] Connection string saved
- [ ] Database password saved securely

---

## 🚀 Quick Deploy Commands

### Generate Secret Key
```bash
openssl rand -hex 32
```

### Test Database Connection
```bash
# From your local machine
psql "postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
```

### Run Migrations (if using Alembic)
```bash
# On Render/Railway, add to build command or run manually
alembic upgrade head
```

---

## 🐛 Common Issues

### "Database connection failed"
- Check DATABASE_URL format
- Verify Supabase project is active
- Check firewall/network settings

### "CORS error"
- Add frontend URL to CORS_ORIGINS
- Include protocol (https://)
- No trailing slashes

### "Build failed"
- Check Python version (3.9+)
- Verify all dependencies in requirements.txt
- Check build logs for specific errors

---

## 💰 Cost Summary

**Free Tier (MVP):**
- Vercel: Free
- Render: Free (spins down)
- Supabase: Free (500MB)

**Always-On (Recommended):**
- Vercel: Free
- Render: $7/month
- Supabase: Free
- **Total: ~$7/month**

---

## ✅ After Deployment

1. Test registration flow
2. Test API endpoints
3. Check database tables created
4. Monitor logs for errors
5. Set up custom domain (optional)

---

**Ready to deploy?** Start with Supabase → Backend → Frontend in that order!


