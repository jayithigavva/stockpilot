# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Basic Usage

### 1. Prepare Your Data

Your historical sales data should be a CSV file with at least two columns:
- `date`: Date in YYYY-MM-DD format
- `demand`: Daily or weekly demand/sales quantity

Example `data/sales.csv`:
```csv
date,demand
2023-01-01,120
2023-01-02,95
2023-01-03,150
2023-01-04,110
...
```

### 2. Single SKU Optimization

```python
from pipeline import InventoryDecisionPipeline
import pandas as pd

# Initialize pipeline with your cost parameters
pipeline = InventoryDecisionPipeline(
    unit_cost=100,           # Your cost per unit
    selling_price=150,        # Your selling price
    holding_cost_rate=0.02,   # 2% per month
    n_simulations=5000
)

# Load your data
df = pd.read_csv('data/sales.csv')
df.columns = ['date', 'demand']  # Ensure correct column names

# Train the forecaster
pipeline.train_forecaster(df, sku_id='SKU001')

# Run optimization
result = pipeline.run_pipeline(
    sku_id='SKU001',
    current_inventory=500,
    lead_time_days=14,
    forecast_horizon_days=30,
    min_order_quantity=100,   # Your MOQ
    max_order_quantity=5000,
    order_multiple=10,
    available_cash=500000,     # Your available cash
    naive_quantity=2000        # Compare with current practice
)

# View results
print(result['explanation'])
```

### 3. Run Example

```bash
python example_usage.py
```

This will run two examples:
- Single SKU optimization
- Multi-SKU capital allocation

## Key Parameters

### Cost Parameters
- `unit_cost`: Cost per unit purchased
- `selling_price`: Selling price per unit
- `holding_cost_rate`: Monthly holding cost (e.g., 0.02 = 2%)
- `markdown_rate`: Fraction of excess inventory that becomes obsolete
- `churn_penalty`: Penalty per stockout event

### Optimization Parameters
- `current_inventory`: Current stock level
- `lead_time_days`: Supplier lead time
- `min_order_quantity`: Minimum order quantity (MOQ)
- `max_order_quantity`: Maximum order quantity
- `order_multiple`: Order must be multiple of this
- `available_cash`: Cash constraint
- `max_stockout_probability`: Maximum acceptable stockout risk (default: 0.20)

## Output Explanation

The system provides:
- **Recommended order quantity**: Optimal units to order
- **Cash impact**: Cash locked in inventory
- **Stockout risk**: Probability and category (LOW/MEDIUM/HIGH)
- **Expected economic loss**: Total cost of the decision
- **Comparison**: How it compares to naive ordering

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running from the project root:
```bash
cd /path/to/stockpilot
python your_script.py
```

### Data Format Issues
Ensure your data has:
- Date column in YYYY-MM-DD format
- Demand column with numeric values
- At least 30 days of historical data

### Training Errors
If training fails:
- Check that you have sufficient data (minimum 30 days)
- Ensure demand values are non-negative
- Verify date column is properly formatted

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Customize cost parameters for your business
3. Integrate with your inventory management system
4. Set up automated runs on a schedule

