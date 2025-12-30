# StockPilot SaaS Setup Guide

Complete setup instructions for the StockPilot web application.

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Git

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database URL and secret key
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Set Up Database

```bash
# Create database
createdb stockpilot

# Run migrations (if using Alembic)
alembic upgrade head

# Or create tables directly
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4. Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Frontend

```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## Initial Setup

### 1. Register a User

1. Go to http://localhost:3000/register
2. Create an account with:
   - Brand name
   - Email
   - Password

### 2. Create a Product

Use the API or create a simple script:

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login-json', json={
    'email': 'your@email.com',
    'password': 'yourpassword'
})
token = response.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# Create product
product = requests.post('http://localhost:8000/api/products', json={
    'sku': 'SKU001',
    'name': 'Test Product',
    'unit_cost': 100,
    'selling_price': 150,
    'lead_time_days': 14
}, headers=headers)
```

### 3. Upload Sales Data

Upload historical sales data via CSV or API:

```python
# Upload sales CSV
files = {'file': open('sales.csv', 'rb')}
requests.post(
    f'http://localhost:8000/api/data/sales/upload-csv?product_id=1',
    files=files,
    headers=headers
)
```

### 4. Generate Recommendations

1. Go to Dashboard
2. Click "Run AI Recommendations"
3. View recommendations
4. Accept or reject decisions

## Testing

### Backend Tests

```bash
cd backend
pytest  # If you add tests
```

### Frontend Tests

```bash
cd frontend
npm test  # If you add tests
```

## Production Deployment

See [HOSTING.md](HOSTING.md) for deployment options.

## Troubleshooting

### Database Connection Issues

- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Verify database exists

### CORS Errors

- Update `CORS_ORIGINS` in backend `.env`
- Ensure frontend URL is included

### Import Errors

- Ensure you're in the correct directory
- Check Python path
- Verify all dependencies are installed

## Next Steps

1. Add more products
2. Upload historical sales data
3. Generate recommendations
4. Accept/reject decisions
5. Monitor inventory updates


