# Setup Checklist - Quick Reference

## ✅ Your System Status

- ✅ Python 3.14.1 (Perfect!)
- ✅ Node.js v20.19.2 (Perfect!)
- ✅ npm 10.8.2 (Perfect!)

**You're all set to proceed!** 🎉

---

## 📋 Setup Steps (In Order)

### 1️⃣ Backend Setup (5-10 minutes)

```bash
# Step 1: Go to backend directory
cd /Users/jayithigavva/stockpilot/backend

# Step 2: Create virtual environment
python3 -m venv venv

# Step 3: Activate virtual environment
source venv/bin/activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Create .env file
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./stockpilot_demo.db
SECRET_KEY=demo-secret-key-12345
CORS_ORIGINS=["http://localhost:3000"]
APP_NAME=StockPilot
DEBUG=True
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256
EOF

# Step 6: Create database
python3 -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Step 7: Test backend (optional)
uvicorn app.main:app --reload --port 8000
# Press Ctrl+C to stop
```

**Checklist:**
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file created
- [ ] Database initialized
- [ ] Backend runs on http://localhost:8000

---

### 2️⃣ Frontend Setup (3-5 minutes)

**Open a NEW terminal window:**

```bash
# Step 1: Go to frontend directory
cd /Users/jayithigavva/stockpilot/frontend

# Step 2: Install dependencies
npm install

# Step 3: Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Step 4: Test frontend (optional)
npm run dev
# Press Ctrl+C to stop
```

**Checklist:**
- [ ] Dependencies installed
- [ ] .env.local file created
- [ ] Frontend runs on http://localhost:3000

---

### 3️⃣ Run Both Servers

**Terminal 1 (Backend):**
```bash
cd /Users/jayithigavva/stockpilot/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd /Users/jayithigavva/stockpilot/frontend
npm run dev
```

**Then open:** http://localhost:3000

---

## 🎯 Quick Test

1. Open http://localhost:3000
2. Click "Sign Up"
3. Register with:
   - Brand: "Test Brand"
   - Email: `test@test.com`
   - Password: `test123`
4. You should see the dashboard!

---

## 📁 Files You'll Create

| File | Location | Created By |
|------|----------|------------|
| `.env` | `backend/` | You (Step 1.5) |
| `.env.local` | `frontend/` | You (Step 2.3) |
| `stockpilot_demo.db` | `backend/` | Python (Step 1.6) |
| `venv/` | `backend/` | Python (Step 1.2) |
| `node_modules/` | `frontend/` | npm (Step 2.2) |

---

## ⚡ Quick Commands Reference

```bash
# Start backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend && npm run dev

# Stop servers
# Press Ctrl+C in each terminal

# Kill processes if stuck
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
```

---

## 🆘 Common Issues

**"Module not found"** → Run `pip install -r requirements.txt` again

**"Port in use"** → Kill process: `lsof -ti:8000 | xargs kill`

**"Cannot connect"** → Check both servers are running

**"Database error"** → Delete `stockpilot_demo.db` and recreate

---

## 📚 Full Documentation

For detailed instructions, see: **COMPLETE_SETUP_GUIDE.md**

---

**Ready? Start with Step 1!** 🚀


