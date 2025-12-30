# StockPilot Web Application

A production-ready SaaS MVP for D2C brands to manage inventory using AI-driven reorder decisions.

## 🎯 Overview

StockPilot is a multi-tenant web application that helps D2C brands:
- **Forecast demand** using AI (LightGBM quantile regression)
- **Simulate inventory risk** with Monte Carlo methods
- **Optimize reorder decisions** based on economic costs
- **Manage cash constraints** across multiple SKUs
- **Track decisions** with full audit logs

## 🏗️ Architecture

```
stockpilot/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   └── services/     # Business logic (AI service)
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/             # Next.js 14 app router
│   ├── lib/              # API client
│   └── package.json
├── models/              # Original AI pipeline
├── simulation/          # Monte Carlo simulation
├── inventory/           # Risk estimation
├── economics/           # Cost modeling
├── optimization/        # Reorder optimization
└── explainability/      # Decision explanations
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database URL

# Create database tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run server
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000
API docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run dev server
npm run dev
```

Frontend runs on: http://localhost:3000

### 3. Initial Setup

1. **Register**: Go to http://localhost:3000/register
2. **Create Product**: Use API or dashboard
3. **Upload Sales Data**: CSV or API
4. **Generate Recommendations**: Click "Run AI" on dashboard
5. **Accept/Reject Decisions**: Review and act on recommendations

## 📋 Core Features

### User Authentication
- JWT-based authentication
- Multi-tenant (brand-based isolation)
- User registration and login

### Product Management
- Create products with cost parameters
- Set supplier details
- Configure lead times and MOQ

### Sales Data Upload
- CSV upload
- API bulk upload
- Historical data management

### AI Recommendations
- On-demand generation
- Per-product recommendations
- Multi-SKU capital allocation
- Risk-based prioritization

### Decision Management
- Accept/reject recommendations
- Automatic inventory updates
- Full audit logging
- Decision history

### Dashboard
- Inventory overview
- Risk metrics
- Cash locked tracking
- Recent decisions

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/login-json` - Login (JSON)

### Products
- `GET /api/products` - List products
- `POST /api/products` - Create product
- `GET /api/products/{id}` - Get product

### Decisions
- `POST /api/decisions/generate` - Generate recommendations
- `GET /api/decisions` - List decisions
- `GET /api/decisions/recommendations` - Get pending recommendations
- `POST /api/decisions/{id}/accept` - Accept decision
- `POST /api/decisions/{id}/reject` - Reject decision

### Dashboard
- `GET /api/dashboard` - Get dashboard stats

### Data
- `POST /api/data/sales/upload` - Upload sales data (JSON)
- `POST /api/data/sales/upload-csv` - Upload sales CSV

## 🗄️ Database Schema

### Core Tables
- `users` - User accounts
- `brands` - Multi-tenant brands
- `products` - SKU definitions
- `inventory` - Current inventory levels
- `suppliers` - Supplier information
- `sales_history` - Historical sales data

### Decision Tables
- `reorder_decisions` - AI recommendations
- `decision_logs` - Audit trail

## 🔐 Security

- JWT token authentication
- Password hashing (bcrypt)
- Multi-tenant data isolation
- CORS configuration
- Environment-based secrets

## 📊 AI Pipeline Integration

The web app integrates the existing AI pipeline:

1. **Demand Forecasting**: LightGBM quantile regression
2. **Simulation**: Monte Carlo demand simulation
3. **Risk Estimation**: Stockout probability calculation
4. **Cost Modeling**: Overstock vs understock costs
5. **Optimization**: Minimize expected economic loss
6. **Explanation**: Human-readable decision summaries

## 🚢 Deployment

See [HOSTING.md](HOSTING.md) for deployment options:

- **Option 1**: Low-cost MVP (~$5-20/month)
- **Option 2**: Scalable MVP (~$50-150/month)
- **Option 3**: Production (~$200-500/month)

## 🧪 Testing

### Backend
```bash
cd backend
pytest  # Add tests as needed
```

### Frontend
```bash
cd frontend
npm test  # Add tests as needed
```

## 📝 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎯 User Flow

1. **Sign Up** → Create brand account
2. **Add Products** → Define SKUs with costs
3. **Upload Sales** → Historical data (CSV or API)
4. **Run AI** → Generate recommendations
5. **Review** → See cash impact, risk reduction
6. **Accept** → Inventory updates automatically
7. **Track** → View decision history

## 🔄 Decision Workflow

```
User clicks "Run AI"
    ↓
System generates recommendations
    ↓
Recommendations shown with:
    - Order quantity
    - Cash locked
    - Risk reduction
    - Explanation
    ↓
User accepts/rejects
    ↓
If accepted:
    - Inventory updated
    - Decision logged
    - Status changed
```

## 📈 Future Enhancements

- Scheduled recommendations (daily/weekly)
- Email notifications
- Advanced analytics
- Supplier integration
- Inventory forecasting charts
- Multi-user teams
- API webhooks

## 🐛 Troubleshooting

### Database Connection
- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Verify database exists

### CORS Errors
- Update `CORS_ORIGINS` in backend `.env`
- Include frontend URL

### Import Errors
- Check Python/Node versions
- Reinstall dependencies
- Verify file paths

## 📚 Documentation

- [SETUP.md](SETUP.md) - Detailed setup instructions
- [HOSTING.md](HOSTING.md) - Deployment guide
- [README.md](README.md) - Original AI pipeline docs

## 🤝 Contributing

This is an MVP. For production:
1. Add comprehensive tests
2. Implement proper error handling
3. Add monitoring and logging
4. Set up CI/CD
5. Add rate limiting
6. Implement backup strategy

## 📄 License

MIT License


