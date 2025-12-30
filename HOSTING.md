# Hosting Guide for StockPilot SaaS MVP

This guide provides multiple hosting options for your StockPilot application, from low-cost MVP to scalable production setups.

## 🎯 Option 1: Low-Cost MVP Setup (Recommended for Start)

**Best for**: Early MVP, testing, first 10-50 users  
**Monthly Cost**: ~$20-50  
**Setup Time**: 2-4 hours

### Architecture

- **Frontend**: Vercel (Free tier)
- **Backend**: Railway or Render (Free tier, then $5-20/month)
- **Database**: Railway PostgreSQL or Supabase (Free tier)

### Setup Steps

#### 1. Frontend (Vercel)

```bash
cd frontend
npm install
npm run build
```

Then:
1. Push code to GitHub
2. Connect GitHub repo to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.com`
4. Deploy (automatic on push)

**Cost**: Free for hobby projects

#### 2. Backend (Railway)

1. Sign up at [railway.app](https://railway.app)
2. Create new project
3. Deploy from GitHub repo (select `backend` folder)
4. Add PostgreSQL service
5. Set environment variables:
   ```
   DATABASE_URL=<railway-postgres-url>
   SECRET_KEY=<generate-random-key>
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```

**Cost**: 
- Free tier: $5 credit/month
- Hobby: $5/month + usage
- Pro: $20/month

#### 3. Database (Railway PostgreSQL)

- Included with Railway backend
- Or use Supabase (free tier: 500MB, 2GB bandwidth)

**Cost**: Free tier or $5-10/month

### Total: ~$5-20/month

---

## 🚀 Option 2: Scalable MVP Setup

**Best for**: Growing user base (50-500 users)  
**Monthly Cost**: ~$50-150  
**Setup Time**: 4-6 hours

### Architecture

- **Frontend**: Vercel Pro ($20/month)
- **Backend**: DigitalOcean App Platform ($12/month) or AWS Elastic Beanstalk
- **Database**: DigitalOcean Managed PostgreSQL ($15/month) or AWS RDS

### Setup Steps

#### 1. Frontend (Vercel Pro)

- Same as Option 1, but upgrade to Pro for:
  - Custom domains
  - More bandwidth
  - Team features

**Cost**: $20/month

#### 2. Backend (DigitalOcean App Platform)

1. Sign up at [digitalocean.com](https://digitalocean.com)
2. Create App Platform app
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set run command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
6. Add environment variables

**Cost**: $12/month (Basic plan)

#### 3. Database (DigitalOcean Managed PostgreSQL)

1. Create PostgreSQL database
2. Choose Basic plan (1GB RAM, 10GB storage)
3. Update `DATABASE_URL` in backend

**Cost**: $15/month

### Total: ~$47/month

---

## 🏢 Option 3: Production-Ready Setup

**Best for**: 500+ users, production workload  
**Monthly Cost**: ~$200-500  
**Setup Time**: 1-2 days

### Architecture

- **Frontend**: Vercel Enterprise or AWS CloudFront + S3
- **Backend**: AWS ECS/Fargate or Google Cloud Run
- **Database**: AWS RDS PostgreSQL or Google Cloud SQL
- **CDN**: CloudFront or Cloudflare

### Setup Steps

#### 1. Frontend (AWS S3 + CloudFront)

- Build Next.js static export
- Upload to S3
- Configure CloudFront distribution
- Or use Vercel Enterprise

**Cost**: $10-50/month

#### 2. Backend (AWS ECS/Fargate)

1. Create ECR repository
2. Build Docker image
3. Create ECS task definition
4. Deploy to Fargate
5. Set up Application Load Balancer

**Cost**: $50-200/month (depending on traffic)

#### 3. Database (AWS RDS PostgreSQL)

1. Create RDS instance (db.t3.micro or db.t3.small)
2. Enable automated backups
3. Configure security groups

**Cost**: $15-50/month

### Total: ~$75-300/month

---

## 📋 Quick Comparison

| Feature | Option 1 (MVP) | Option 2 (Scalable) | Option 3 (Production) |
|---------|---------------|---------------------|----------------------|
| **Monthly Cost** | $5-20 | $50-150 | $200-500 |
| **Users Supported** | 10-50 | 50-500 | 500+ |
| **Setup Complexity** | Low | Medium | High |
| **Scalability** | Limited | Good | Excellent |
| **Best For** | Testing/MVP | Growing startup | Production |

---

## 🔧 Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=["https://your-frontend.vercel.app"]

# Application
APP_NAME=StockPilot
DEBUG=False
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

---

## 🚀 Deployment Checklist

### Backend

- [ ] Set up database (PostgreSQL)
- [ ] Run migrations: `alembic upgrade head`
- [ ] Set environment variables
- [ ] Test API endpoints
- [ ] Configure CORS
- [ ] Set up SSL/HTTPS

### Frontend

- [ ] Set `NEXT_PUBLIC_API_URL`
- [ ] Build and test locally
- [ ] Deploy to hosting
- [ ] Test authentication flow
- [ ] Verify API connectivity

### Database

- [ ] Create database
- [ ] Run initial migrations
- [ ] Set up backups
- [ ] Configure connection pooling
- [ ] Test connection from backend

---

## 💡 Cost Optimization Tips

1. **Start with Option 1**: Don't over-provision early
2. **Use free tiers**: Vercel, Supabase free tiers are generous
3. **Monitor usage**: Set up alerts for unexpected costs
4. **Optimize database**: Use connection pooling, index properly
5. **Cache aggressively**: Reduce database queries
6. **Scale gradually**: Only upgrade when you hit limits

---

## 🔄 Migration Path

**Start**: Option 1 (Low-Cost MVP)  
**Grow**: Option 2 (Scalable MVP) when you hit 50+ users  
**Scale**: Option 3 (Production) when you need enterprise features

---

## 🛠️ What NOT to Overbuild Early

❌ **Don't build**:
- Kubernetes clusters
- Microservices architecture
- Complex CI/CD pipelines
- Multi-region deployments
- Real-time streaming
- GPU instances

✅ **Do build**:
- Simple, working MVP
- Basic monitoring
- Database backups
- Environment-based config
- Error logging

---

## 📞 Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **DigitalOcean Guides**: https://www.digitalocean.com/community/tags/deployment
- **AWS Getting Started**: https://aws.amazon.com/getting-started

---

## 🎯 Recommended Starting Point

**For your MVP, start with Option 1**:
1. Deploy frontend to Vercel (free)
2. Deploy backend to Railway (free tier)
3. Use Railway PostgreSQL (included)
4. Total cost: **$0-5/month** initially

This gives you:
- ✅ Fast deployment
- ✅ Low cost
- ✅ Easy scaling
- ✅ Professional URLs
- ✅ SSL certificates included

Upgrade to Option 2 when you have paying customers and need more reliability.


