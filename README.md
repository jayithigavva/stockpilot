# StockPilot: Production-Ready Inventory Decision System

A Python-based system that optimizes reorder decisions under demand uncertainty and cash constraints. The system focuses on **minimizing expected economic loss** and **freeing working capital** rather than just forecast accuracy.

## 🎯 System Objective

Given uncertain demand, limited cash, and supplier constraints, the system answers:
> **"What is the best inventory decision that minimizes economic loss and frees working capital?"**

## 🏗️ Architecture

The system is built as modular components:

```
stockpilot/
├── data/                    # Data files
├── models/
│   └── demand_forecast.py   # LightGBM quantile regression forecasting
├── simulation/
│   └── demand_simulation.py # Monte Carlo simulation engine
├── inventory/
│   └── risk_estimator.py    # Stockout risk estimation
├── economics/
│   └── cost_model.py        # Overstock/understock cost modeling
├── optimization/
│   ├── reorder_optimizer.py # Optimal reorder quantity
│   └── capital_allocator.py # Multi-SKU capital allocation
├── explainability/
│   └── decision_explainer.py # Human-readable explanations
└── pipeline.py              # End-to-end orchestration
```

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### Single SKU Optimization

```python
from pipeline import InventoryDecisionPipeline
import pandas as pd

# Initialize pipeline
pipeline = InventoryDecisionPipeline(
    unit_cost=100,           # Cost per unit
    selling_price=150,        # Selling price
    holding_cost_rate=0.02,   # 2% per month
    n_simulations=5000
)

# Load historical data
df = pd.read_csv('data/historical_sales.csv')
df.columns = ['date', 'demand']  # Ensure columns are named correctly

# Train forecaster
pipeline.train_forecaster(df, sku_id='SKU001')

# Run optimization
result = pipeline.run_pipeline(
    sku_id='SKU001',
    current_inventory=500,
    lead_time_days=14,
    forecast_horizon_days=30,
    min_order_quantity=100,   # MOQ
    max_order_quantity=5000,
    order_multiple=10,        # Order in multiples of 10
    available_cash=500000,    # ₹5 lakh available
    naive_quantity=2000       # Compare with gut-based ordering
)

# Print explanation
print(result['explanation'])
```

### Multi-SKU Capital Allocation

```python
# Prepare SKU configurations
sku_configs = [
    {
        'sku_id': 'SKU001',
        'forecast_df': forecast_df_1,
        'current_inventory': 500,
        'lead_time_days': 14,
        'unit_cost': 100,
        'selling_price': 150,
        'min_order_quantity': 100,
        'max_order_quantity': 5000
    },
    {
        'sku_id': 'SKU002',
        'forecast_df': forecast_df_2,
        'current_inventory': 300,
        'lead_time_days': 21,
        'unit_cost': 200,
        'selling_price': 300,
        'min_order_quantity': 50,
        'max_order_quantity': 3000
    }
]

# Allocate capital
allocation_result = pipeline.run_multi_sku_pipeline(
    sku_configs=sku_configs,
    total_available_cash=1000000,  # ₹10 lakh
    baseline_quantities={'SKU001': 1500, 'SKU002': 800}
)

print(allocation_result['explanation'])
```

## 📊 Key Features

### 1. Probabilistic Demand Forecasting
- Uses LightGBM with quantile regression
- Produces P10, P50, P90 forecasts
- Features: calendar, lags, rolling statistics

### 2. Monte Carlo Simulation
- Simulates 5000+ demand paths
- Estimates stockout probability
- Models inventory depletion day-by-day

### 3. Economic Cost Modeling
- **Overstocking costs**: Cash locked, holding costs, markdown/expiry
- **Understocking costs**: Lost sales, lost margin, churn penalty
- Quantifies total expected economic loss

### 4. Risk Estimation
- Stockout probability before replenishment
- Expected days of cover
- Risk categories: LOW (<5%), MEDIUM (5-20%), HIGH (>20%)

### 5. Reorder Optimization
- Minimizes expected economic loss
- Respects constraints: cash, MOQ, order multiples, risk tolerance
- Compares with naive (gut-based) ordering

### 6. Capital Allocation
- Ranks SKUs by economic loss avoided per ₹ spent
- Optimally allocates limited capital across SKUs
- Greedy allocation algorithm

### 7. Decision Explanation
- Human-readable explanations
- Cash impact (locked vs freed)
- Risk reduction metrics
- Comparison with baseline decisions

## 📈 Example Output

```
📦 **Recommended Order: 900 units**

💰 **Cash Impact:**
   - Cash locked: ₹90,000

⚠️ **Stockout Risk:**
   - Probability: 4.2%
   - Risk category: LOW
   - Expected ending inventory: 150 units

📊 **Expected Economic Loss:**
   - Total: ₹12,500

📈 **Comparison with Naive Ordering:**
   - Ordering 900 units instead of 1,400 frees ₹50,000
   - Reduces expected loss by ₹8,500 (40.5%)
   - Reduces stockout risk from 2.1% to 4.2%
```

## 🔧 Configuration

### Cost Parameters
- `unit_cost`: Cost per unit purchased
- `selling_price`: Selling price per unit
- `holding_cost_rate`: Monthly holding cost as fraction of unit cost (default: 0.02 = 2%)
- `markdown_rate`: Fraction of excess inventory that becomes obsolete (default: 0.0)
- `churn_penalty`: Penalty per stockout event (default: 0.0)

### Optimization Parameters
- `max_stockout_probability`: Maximum acceptable stockout probability (default: 0.20 = 20%)
- `n_simulations`: Number of Monte Carlo simulations (default: 5000)
- `holding_period_months`: Expected holding period for excess inventory (default: 1.0)

### Constraints
- `min_order_quantity`: Minimum order quantity (MOQ)
- `max_order_quantity`: Maximum order quantity
- `order_multiple`: Order must be multiple of this value
- `available_cash`: Available cash constraint

## 📝 Data Format

Historical sales data should be a CSV with:
- `date`: Date column (YYYY-MM-DD format)
- `demand`: Daily/weekly demand/sales quantity

Example:
```csv
date,demand
2023-01-01,120
2023-01-02,95
2023-01-03,150
...
```

## 🎓 Philosophy

**This system optimizes for business outcomes, not forecast accuracy.**

- Focus: Minimize expected economic loss
- Constraint: Limited working capital
- Trade-off: Overstocking vs understocking costs
- Outcome: Cash-efficient inventory decisions

## 📚 Module Details

### Demand Forecasting (`models/demand_forecast.py`)
- LightGBM quantile regression
- Calendar features (day of week, month, holidays)
- Lag features (t-1, t-7, t-14, t-30)
- Rolling statistics (mean, std over 7/14/30 days)
- Outputs: P10, P50, P90, mean, std

### Demand Simulation (`simulation/demand_simulation.py`)
- Monte Carlo simulation (5000+ paths)
- Samples from forecast distribution
- Simulates day-by-day inventory depletion
- Outputs: Stockout probability, cumulative demand distribution

### Risk Estimation (`inventory/risk_estimator.py`)
- Pure logic module (no ML)
- Computes stockout probability
- Categorizes risk (LOW/MEDIUM/HIGH)
- Estimates days of cover

### Cost Model (`economics/cost_model.py`)
- Overstocking: Cash locked + holding + markdown
- Understocking: Lost margin + churn penalty
- Computes expected economic loss

### Reorder Optimizer (`optimization/reorder_optimizer.py`)
- Grid search over feasible quantities
- Minimizes expected loss
- Respects all constraints
- Compares with naive ordering

### Capital Allocator (`optimization/capital_allocator.py`)
- Ranks SKUs by efficiency (loss avoided / ₹ spent)
- Greedy allocation algorithm
- Handles cash constraints

### Decision Explainer (`explainability/decision_explainer.py`)
- Human-readable explanations
- Currency formatting (₹ lakh, ₹K)
- Summary reports

## 🔍 Testing

```python
# Example test
pipeline = InventoryDecisionPipeline(unit_cost=100, selling_price=150)
# ... load data and train ...
result = pipeline.run_pipeline(...)
assert result['optimization_result']['optimal_quantity'] > 0
```

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code is modular and well-commented
- Focus on business outcomes, not just metrics
- Maintain backward compatibility

## 📧 Support

For issues or questions, please open an issue on GitHub.

