# Quick Demo - See the App in 5 Minutes

This guide will help you see the app running locally without full database setup.

## Option 1: Quick Visual Demo (No Database Required)

### 1. Start Frontend Only

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 to see:
- Landing page
- Login/Register pages
- Dashboard UI (will show errors without backend, but you can see the design)

## Option 2: Full Demo with Mock Backend

### 1. Start Backend (with SQLite for simplicity)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./stockpilot.db
SECRET_KEY=demo-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:3000"]
APP_NAME=StockPilot
DEBUG=True
EOF

# Update database.py to support SQLite
# (SQLite works for demo, PostgreSQL for production)

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Test the App

1. Go to http://localhost:3000
2. Click "Sign Up"
3. Register with:
   - Brand Name: "Demo Brand"
   - Email: demo@example.com
   - Password: demo123
4. You'll be logged in and see the dashboard
5. Click "Run AI Recommendations" (will need products first)

## Option 3: Use SQLite (Easiest for Demo)

The backend can work with SQLite for a quick demo. Let me update the database config to support SQLite.


