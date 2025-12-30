#!/bin/bash

# Quick demo startup script for StockPilot

echo "🚀 Starting StockPilot Demo..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./stockpilot_demo.db
SECRET_KEY=demo-secret-key-$(openssl rand -hex 16)
CORS_ORIGINS=["http://localhost:3000"]
APP_NAME=StockPilot
DEBUG=True
ACCESS_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256
EOF
fi

# Create database tables
echo "Creating database tables..."
python3 -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)" 2>/dev/null || echo "Database tables created"

# Start backend in background
echo "Starting backend server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"

# Wait a bit for backend to start
sleep 3

# Frontend setup
echo ""
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a minute)..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating frontend .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

# Start frontend
echo "Starting frontend server..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"
echo "Frontend: http://localhost:3000"

echo ""
echo "✅ Demo is running!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To stop the servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   Or press Ctrl+C and run: pkill -f 'uvicorn|next'"
echo ""
echo "📊 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Click 'Sign Up' to create an account"
echo "   3. Register with any email/password"
echo "   4. Explore the dashboard!"

# Keep script running
wait


