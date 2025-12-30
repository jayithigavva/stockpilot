# DigitalOcean App Platform Deployment Guide

This guide will help you deploy the StockPilot backend to DigitalOcean App Platform.

## Prerequisites

- DigitalOcean account (sign up at https://www.digitalocean.com)
- GitHub repository connected (✅ Done)
- Credit card (for App Platform, but free tier available)

## Step 1: Create App on DigitalOcean

### Option A: Using App Spec File (Recommended)

1. **Go to DigitalOcean Dashboard**
   - Visit https://cloud.digitalocean.com
   - Sign in or create account

2. **Create New App**
   - Click "Create" → "Apps"
   - Select "GitHub" as source
   - Authorize DigitalOcean to access your GitHub
   - Select repository: `jayithigavva/stockpilot`
   - Select branch: `main`

3. **Configure App**
   - **App Name**: `stockpilot-backend` (or your choice)
   - **Region**: Choose closest to you (e.g., `nyc1`, `sfo3`, `blr1`)
   - **Source Directory**: Set to `backend` (IMPORTANT!)

4. **Configure Service**
   - **Type**: Web Service
   - **HTTP Port**: `8080` (DigitalOcean sets `$PORT` automatically)
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Add Database**
   - Click "Add Database"
   - **Database Engine**: PostgreSQL
   - **Version**: 15 (or latest)
   - **Plan**: Basic ($12/month) or Dev Database ($7/month for testing)
   - **Database Name**: `stockpilot` (auto-generated)

6. **Set Environment Variables**
   Click "Edit" next to Environment Variables and add:

   ```
   SECRET_KEY=<generate-a-random-secret-key>
   CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
   DEBUG=False
   ```

   **To generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   **Note**: `DATABASE_URL` will be automatically set by DigitalOcean when you add the database.

7. **Review and Deploy**
   - Review all settings
   - Click "Create Resources"
   - Wait for deployment (5-10 minutes)

### Option B: Using App Spec File (Advanced)

If you prefer using the `.do/app.yaml` file:

1. **Push the app.yaml file to GitHub** (already created)
2. **Create App from App Spec**
   - In DigitalOcean, click "Create" → "Apps"
   - Select "App Spec" tab
   - Select your repository and branch
   - DigitalOcean will read `.do/app.yaml`
   - Review and deploy

## Step 2: Get Your Backend URL

After deployment:

1. Go to your app in DigitalOcean dashboard
2. Find the **Live App URL** (e.g., `https://stockpilot-backend-xxxxx.ondigitalocean.app`)
3. Copy this URL - you'll need it for the frontend

## Step 3: Update Frontend Environment Variable

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `NEXT_PUBLIC_API_URL` to your DigitalOcean backend URL
3. Redeploy frontend

## Step 4: Test Your Deployment

1. **Health Check**: Visit `https://your-backend-url.ondigitalocean.app/health`
   - Should return: `{"status": "healthy"}`

2. **API Docs**: Visit `https://your-backend-url.ondigitalocean.app/docs`
   - Should show Swagger UI

3. **Test from Frontend**: Try logging in from your Vercel-deployed frontend

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by DigitalOcean |
| `SECRET_KEY` | JWT secret key | Generate random string |
| `CORS_ORIGINS` | Allowed frontend origins | `https://your-app.vercel.app,http://localhost:3000` |
| `DEBUG` | Debug mode | `False` for production |

## Database Migrations

If you need to run database migrations:

1. **Option 1: Via DigitalOcean Console**
   - Go to your app → Settings → Console
   - Run: `alembic upgrade head`

2. **Option 2: Add to Build Command**
   - Update build command to:
   ```
   pip install -r requirements.txt && alembic upgrade head
   ```

## Troubleshooting

### Build Fails

**Issue**: `ModuleNotFoundError` or import errors
- **Solution**: Check that `source_dir` is set to `backend`
- Verify `requirements.txt` is in `backend/` directory

**Issue**: `Port already in use`
- **Solution**: Make sure run command uses `$PORT` variable

### Database Connection Fails

**Issue**: `could not connect to server`
- **Solution**: 
  - Verify `DATABASE_URL` is set (should be auto-set)
  - Check database is running in DigitalOcean dashboard
  - Ensure database and app are in same region

### CORS Errors

**Issue**: `CORS policy: No 'Access-Control-Allow-Origin' header`
- **Solution**: 
  - Add your Vercel frontend URL to `CORS_ORIGINS`
  - Format: `https://your-app.vercel.app` (no trailing slash)
  - Redeploy backend after updating

### App Crashes on Startup

**Issue**: App starts then crashes
- **Solution**: 
  - Check logs in DigitalOcean dashboard
  - Verify all environment variables are set
  - Check that `SECRET_KEY` is set

## Cost Estimation

- **Basic Plan**: $5/month (512MB RAM, 1 vCPU)
- **Professional Plan**: $12/month (1GB RAM, 1 vCPU) - Recommended
- **Database (Dev)**: $7/month (1GB storage)
- **Database (Basic)**: $12/month (1GB storage, automated backups)

**Total (Recommended)**: ~$19-24/month

## Scaling

As your app grows:

1. **Increase Instance Size**: Settings → Components → Edit → Instance Size
2. **Add More Instances**: Settings → Components → Edit → Instance Count
3. **Upgrade Database**: Settings → Database → Edit Plan

## Monitoring

- **Logs**: View in DigitalOcean dashboard → Runtime Logs
- **Metrics**: CPU, Memory, Request Rate in dashboard
- **Alerts**: Set up alerts for errors or high resource usage

## Next Steps

1. ✅ Backend deployed to DigitalOcean
2. ✅ Backend URL obtained
3. ✅ Update `NEXT_PUBLIC_API_URL` in Vercel
4. ✅ Test full stack deployment
5. ✅ Set up custom domain (optional)

## Quick Command Reference

**Generate Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Test Database Connection Locally:**
```bash
psql $DATABASE_URL
```

**Run Migrations:**
```bash
alembic upgrade head
```

## Support

- DigitalOcean Docs: https://docs.digitalocean.com/products/app-platform/
- DigitalOcean Community: https://www.digitalocean.com/community/tags/app-platform

