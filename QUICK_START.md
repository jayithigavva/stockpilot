# Quick Start - See the App Now! 🚀

## Easiest Way (Automated Script)

Just run:

```bash
./START_DEMO.sh
```

This will:
- ✅ Set up backend with SQLite (no PostgreSQL needed!)
- ✅ Install all dependencies
- ✅ Start backend on http://localhost:8000
- ✅ Start frontend on http://localhost:3000
- ✅ Open your browser

Then go to **http://localhost:3000** and sign up!

---

## Manual Setup (Step by Step)

### Step 1: Backend (2 minutes)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./stockpilot_demo.db
SECRET_KEY=demo-secret-key-12345
CORS_ORIGINS=["http://localhost:3000"]
APP_NAME=StockPilot
DEBUG=True
EOF

# Create database
python3 -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend will run on: **http://localhost:8000**

### Step 2: Frontend (1 minute)

Open a **new terminal**:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Frontend will run on: **http://localhost:3000**

### Step 3: Use the App! 🎉

1. Open **http://localhost:3000** in your browser
2. Click **"Sign Up"**
3. Register with:
   - Brand Name: "My Brand"
   - Email: `demo@example.com`
   - Password: `demo123`
4. You'll see the dashboard!

---

## What You'll See

### Landing Page
- Clean login/register interface

### Dashboard
- Inventory stats
- "Run AI Recommendations" button
- Recent decisions

### Decisions Page
- View recommendations
- Accept/reject decisions

---

## Troubleshooting

### "Port already in use"
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill  # Backend
lsof -ti:3000 | xargs kill  # Frontend
```

### "Module not found"
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### "Database error"
The SQLite database is created automatically. If issues:
```bash
cd backend
rm stockpilot_demo.db
python3 -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## Next Steps After Demo

1. **Add a Product**: Use the API or create via dashboard
2. **Upload Sales Data**: CSV upload or API
3. **Generate Recommendations**: Click "Run AI"
4. **Accept Decisions**: See inventory update

---

## Stop the Servers

Press `Ctrl+C` in both terminals, or:

```bash
pkill -f uvicorn
pkill -f next
```

---

**That's it! You should see the app running now.** 🎊


