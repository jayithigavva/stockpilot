# StockPilot AI Techniques & Implementation Guide

This document explains all the AI/ML techniques, optimization algorithms, and decision-making methods used in StockPilot to generate inventory recommendations for footwear brands.

---

## Table of Contents

1. [Demand Forecasting](#1-demand-forecasting)
2. [Monte Carlo Simulation](#2-monte-carlo-simulation)
3. [Economic Cost Modeling](#3-economic-cost-modeling)
4. [Risk Estimation](#4-risk-estimation)
5. [Reorder Optimization](#5-reorder-optimization)
6. [Capital Allocation](#6-capital-allocation)
7. [Footwear-Specific Techniques](#7-footwear-specific-techniques)
8. [Decision Explanation](#8-decision-explanation)
9. [Pipeline Orchestration](#9-pipeline-orchestration)

---

## 1. Demand Forecasting

### Technique: LightGBM Quantile Regression

**What it does:**
- Predicts future demand using machine learning (gradient boosting)
- Produces probabilistic forecasts (P10, P50, P90 quantiles) instead of single-point estimates
- Learns from historical sales patterns, seasonality, and trends

**Why it's useful:**
- **Probabilistic forecasts** capture uncertainty (demand could be high or low)
- **Quantile regression** gives us confidence intervals (P10 = 10% chance demand is lower, P90 = 90% chance demand is lower)
- **LightGBM** is fast, accurate, and handles non-linear patterns well
- **Feature engineering** captures calendar effects (weekends, months) and trends

**How it works:**
1. Creates features from historical data:
   - Calendar features: day of week, week of year, month, weekends
   - Lag features: demand 1, 7, 14, 30 days ago
   - Rolling statistics: 7/14/30-day moving averages and standard deviations
   - Trend features: short-term vs long-term demand trends
2. Trains separate models for each quantile (P10, P50, P90)
3. For each future day, predicts all three quantiles
4. Estimates mean and standard deviation from quantiles

**Where it's coded:**
- **File:** `models/demand_forecast.py`
- **Class:** `DemandForecaster`
- **Key methods:**
  - `train()`: Trains quantile regression models
  - `forecast()`: Generates probabilistic forecasts
  - `_create_features()`: Feature engineering
  - `_prepare_training_data()`: Data preparation

**Usage example:**
```python
forecaster = DemandForecaster()
forecaster.train(historical_sales_data, sku_id="SKU001")
forecast = forecaster.forecast(future_dates, last_known_data)
# Returns: DataFrame with p10, p50, p90, mean, std for each day
```

---

## 2. Monte Carlo Simulation

### Technique: Monte Carlo Demand Simulation

**What it does:**
- Simulates thousands of possible demand scenarios during lead time
- Samples demand from the forecast distribution (normal or quantile-based)
- Tracks inventory depletion day-by-day to estimate stockout probability

**Why it's useful:**
- **Captures uncertainty**: Instead of assuming average demand, we test 5000+ scenarios
- **Estimates stockout probability**: How likely are we to run out of stock?
- **Accounts for variability**: Some days demand is high, some days low
- **Realistic outcomes**: Shows distribution of possible ending inventory levels

**How it works:**
1. For each of 5000 simulations:
   - Sample daily demand from forecast distribution (normal or quantile-based)
   - Simulate day-by-day inventory depletion
   - Track when stockout occurs (if at all)
   - Record ending inventory level
2. Aggregate results:
   - Stockout probability = % of simulations where inventory went negative
   - Expected ending inventory = average across all simulations
   - Distribution percentiles (P10, P50, P90 of ending inventory)

**Where it's coded:**
- **File:** `simulation/demand_simulation.py`
- **Class:** `DemandSimulator`
- **Key methods:**
  - `simulate_demand_path()`: Simulates one demand scenario
  - `simulate_inventory_depletion()`: Runs full Monte Carlo simulation
  - `get_demand_statistics()`: Computes summary statistics
  - `get_stockout_statistics()`: Computes stockout metrics


**Usage example:**
```python
simulator = DemandSimulator(n_simulations=5000)
results = simulator.simulate_inventory_depletion(
    forecast_df=forecast,
    current_inventory=100,
    lead_time_days=14
)
# Returns: stockout_probability, ending_inventory distribution, etc.
```

---

## 3. Economic Cost Modeling

### Technique: Explicit Overstock vs Understock Cost Modeling

**What it does:**
- Quantifies the economic cost of two types of errors:
  - **Overstocking**: Ordering too much (cash locked, holding costs, markdowns)
  - **Understocking**: Ordering too little (lost sales, lost margin, customer churn)
- Computes expected costs across all simulation scenarios

**Why it's useful:**
- **Business-focused**: Optimizes for real economic outcomes, not just forecast accuracy
- **Balances trade-offs**: Finds the sweet spot between overstock and understock costs
- **Quantifies impact**: Shows exactly how much money is at risk
- **Decision support**: Helps make informed trade-offs

**How it works:**
1. **Overstock cost** = Cash locked + Holding cost + Markdown cost
   - Cash locked: Excess units × unit cost
   - Holding cost: Cash locked × holding rate × months
   - Markdown cost: Obsolete units × unit cost
2. **Understock cost** = Lost margin + Churn penalty
   - Lost margin: Unmet demand × (selling price - unit cost)
   - Churn penalty: One-time cost per stockout event
3. **Expected cost** = Average across all Monte Carlo simulations

**Where it's coded:**
- **File:** `economics/cost_model.py`
- **Class:** `CostModel`
- **Key methods:**
  - `compute_overstock_cost()`: Calculates overstock cost
  - `compute_understock_cost()`: Calculates understock cost
  - `compute_expected_economic_loss()`: Computes expected costs via simulation

**Usage example:**
```python
cost_model = CostModel(
    unit_cost=100,
    selling_price=150,
    holding_cost_rate=0.02,  # 2% per month
    markdown_rate=0.1  # 10% become obsolete
)
expected_loss = cost_model.compute_expected_economic_loss(
    forecast_df=forecast,
    current_inventory=100,
    reorder_quantity=200,
    lead_time_days=14
)
# Returns: expected_overstock_cost, expected_understock_cost, total_expected_loss
```

---

## 4. Risk Estimation

### Technique: Probabilistic Stockout Risk Assessment

**What it does:**
- Estimates probability oof stockout during lead time
- Categorizes risk as LOW, MEDIUM, or HIGH
- Computes expected days of inventory cover

**Why it's useful:**
- **Risk awareness**: Shows how likely you are to run out of stock
- **Decision support**: Helps prioritize which products need urgent reordering
- **Risk categories**: Simple LOW/MEDIUM/HIGH labels for quick understanding
- **Days of cover**: Shows how many days of inventory you have left

**How it works:**
1. Uses Monte Carlo simulation to estimate stockout probability
2. Categorizes risk:
   - **LOW**: < 5% stockout probability
   - **MEDIUM**: 5-20% stockout probability
   - **HIGH**: > 20% stockout probability
3. Computes expected days of cover = current_inventory / average_daily_demand

**Where it's coded:**
- **File:** `inventory/risk_estimator.py`
- **Class:** `RiskEstimator`
- **Key methods:**
  - `estimate_stockout_risk()`: Estimates current risk without reorder
  - `estimate_risk_with_reorder()`: Estimates risk after placing a reorder
  - `_categorize_risk()`: Maps probability to LOW/MEDIUM/HIGH

**Usage example:**
```python
risk_estimator = RiskEstimator(simulator=simulator)
risk = risk_estimator.estimate_stockout_risk(
    forecast_df=forecast,
    current_inventory=100,
    lead_time_days=14
)
# Returns: {
#   'stockout_probability': 0.15,
#   'risk_category': 'MEDIUM',
#   'expected_days_of_cover': 12.5
# }
```

---

## 5. Reorder Optimization

### Technique: Grid Search with Economic Loss Minimization

**What it does:**
- Evaluates multiple order quantities and selects the one that minimizes expected economic loss
- Respects constraints: MOQ, order multiples, cash limits, risk tolerance
- Finds the optimal balance between overstock and understock costs

**Why it's useful:**
- **Optimal decisions**: Finds the exact order quantity that minimizes total cost
- **Constraint handling**: Respects real-world constraints (minimum orders, cash limits)
- **Risk-aware**: Penalizes orders that exceed risk tolerance
- **Transparent**: Shows all evaluated quantities and their costs

**How it works:**
1. Generates feasible order quantities (respecting MOQ, multiples, cash constraints)
2. For each quantity:
   - Runs Monte Carlo simulation
   - Computes expected overstock and understock costs
   - Checks if risk is acceptable
   - Calculates total expected loss
3. Selects quantity with minimum expected loss
4. Returns optimal quantity, expected loss, and risk metrics

**Where it's coded:**
- **File:** `optimization/reorder_optimizer.py`
- **Class:** `ReorderOptimizer`
- **Key methods:**
  - `find_feasible_order_quantities()`: Generates candidate quantities
  - `optimize_reorder()`: Finds optimal quantity
  - `compare_with_naive()`: Compares optimal vs naive ordering

**Usage example:**
```python
optimizer = ReorderOptimizer(
    cost_model=cost_model,
    risk_estimator=risk_estimator,
    max_stockout_probability=0.20
)
result = optimizer.optimize_reorder(
    forecast_df=forecast,
    current_inventory=100,
    lead_time_days=14,
    min_order_quantity=50,
    max_order_quantity=1000,
    available_cash=50000
)
# Returns: optimal_quantity, optimal_loss, risk_metrics, cash_locked
```

---

## 6. Capital Allocation

### Technique: Greedy Allocation by Economic Efficiency

**What it does:**
- When cash is limited, optimally allocates capital across multiple SKUs
- Ranks SKUs by "economic loss avoided per rupee spent"
- Allocates to highest-efficiency SKUs first until cash runs out

**Why it's useful:**
- **Maximizes value**: Gets the most economic benefit from limited cash
- **Prioritization**: Shows which SKUs give the best return on investment
- **Cash-constrained**: Handles real-world budget limitations
- **Transparent ranking**: Shows why some SKUs are prioritized over others

**How it works:**
1. For each SKU, compute:
   - Optimal order quantity (without cash constraint)
   - Economic loss avoided = baseline_loss - optimal_loss
   - Cash required = optimal_quantity × unit_cost
   - Efficiency = loss_avoided / cash_required
2. Rank SKUs by efficiency (highest first)
3. Greedy allocation:
   - Allocate to highest-efficiency SKU first
   - Continue until cash is exhausted
   - If can't afford full optimal, allocate partial or skip

**Where it's coded:**
- **File:** `optimization/capital_allocator.py`
- **Class:** `CapitalAllocator`
- **Key methods:**
  - `compute_loss_avoided_per_rupee()`: Computes efficiency metric
  - `rank_skus_by_efficiency()`: Ranks SKUs by ROI
  - `allocate_capital()`: Performs greedy allocation

**Usage example:**
```python
allocator = CapitalAllocator(optimizers={sku_id: optimizer})
allocation = allocator.allocate_capital(
    sku_data=sku_list,
    total_available_cash=100000
)
# Returns: allocations dict, total_cash_used, remaining_cash, rankings
```

---

## 7. Footwear-Specific Techniques

### 7.1 Size-Share Forecasting

**What it does:**
- Predicts total style demand AND size distribution separately
- Models size demand as shares of total style demand (constrained to sum to 1)
- Combines to get size-level demand forecasts

**Why it's useful:**
- **Size coupling**: Sizes are not independent - if style sells well, all sizes sell
- **Realistic modeling**: Captures that size 8 and 9 are more popular than size 6
- **Style-level decisions**: Enables style-level reorder planning
- **Size breakdown**: Shows demand per size, not just total

**How it works:**
1. Train style-level demand model (total demand across all sizes)
2. Train size-share models (each size's share of total demand)
3. Forecast total style demand (P10, P50, P90)
4. Forecast size shares (constrained to sum to 1)
5. Combine: size_demand = total_demand × size_share

**Where it's coded:**
- **File:** `models/size_share_forecast.py`
- **Class:** `SizeShareForecaster`
- **Key methods:**
  - `train()`: Trains style and size-share models
  - `forecast()`: Generates size-level forecasts

**Usage example:**
```python
forecaster = SizeShareForecaster()
forecaster.train(sales_df, style_id="STYLE001", sizes=["6", "7", "8", "9", "10", "11"])
forecast = forecaster.forecast(forecast_horizon_days=30)
# Returns: total_demand, size_shares, size_demands (per size)
```

### 7.2 Footwear Cost Model

**What it does:**
- Models size-specific overstock and understock costs
- Accounts for footwear-specific factors:
  - Overstock in unpopular sizes (6, 11) is worse (must discount entire style)
  - Understock in popular sizes (8, 9) loses more revenue

**Why it's useful:**
- **Size-specific penalties**: Recognizes that not all sizes are equal
- **Style-level markdowns**: Accounts for the fact that you can't discount just one size
- **Popular size protection**: Prioritizes keeping popular sizes in stock
- **Realistic costs**: Better reflects actual footwear business economics

**How it works:**
1. **Size-specific multipliers**:
   - Overstock: Size 6/11 have 1.3x penalty (harder to sell)
   - Understock: Size 8/9 have 1.5x penalty (more revenue lost)
2. **Style-level markdown**: If any size doesn't sell, must discount entire style
3. Computes costs per size, then aggregates to style level

**Where it's coded:**
- **File:** `economics/footwear_cost_model.py`
- **Class:** `FootwearCostModel`
- **Key methods:**
  - `compute_size_overstock_cost()`: Size-specific overstock cost
  - `compute_size_understock_cost()`: Size-specific understock cost
  - `compute_style_level_costs()`: Aggregates to style level

**Usage example:**
```python
cost_model = FootwearCostModel(
    base_unit_cost=500,
    base_selling_price=1000,
    markdown_rate=0.5  # 50% markdown for unsold sizes
)
overstock_cost = cost_model.compute_size_overstock_cost(
    size="6",  # Unpopular size
    excess_units=50
)
# Returns higher cost than size 8/9 for same excess
```

### 7.3 Size Curve Optimization

**What it does:**
- Optimizes style-level reorder decisions considering factory-valid size curves
- Evaluates multiple size distribution curves and selects the best one
- Ranks by "expected ₹ saved per ₹ committed"

**Why it's useful:**
- **Factory constraints**: Footwear factories require specific size distributions
- **Style-level planning**: Makes decisions at style level, not individual SKU level
- **Size coupling**: Accounts for the fact that sizes must be ordered together
- **Risk per size**: Shows which sizes are high-risk and need more inventory

**How it works:**
1. Generates factory-valid size curves (respecting min order total, order multiples)
2. For each curve:
   - Simulates demand depletion for each size
   - Computes size-level overstock/understock costs
   - Aggregates to style-level costs
   - Calculates expected return per rupee
3. Selects curve with highest expected return
4. Returns size breakdown, risk per size, cash at risk

**Where it's coded:**
- **File:** `optimization/size_curve_optimizer.py`
- **Class:** `SizeCurveOptimizer`
- **Key methods:**
  - `generate_valid_size_curves()`: Creates factory-valid curves
  - `evaluate_size_curve()`: Evaluates a curve and computes costs
  - `optimize_style_reorder()`: Finds optimal curve

**Usage example:**
```python
optimizer = SizeCurveOptimizer(
    cost_model=footwear_cost_model,
    simulator=size_simulator
)
optimal_curve = optimizer.optimize_style_reorder(
    forecast=size_forecast,
    current_inventory_by_size={"6": 10, "7": 20, "8": 30, ...},
    size_curve_templates=valid_curves,
    available_cash=500000
)
# Returns: optimal size breakdown, size-level risks, total cash required
```

### 7.4 Size Demand Simulation

**What it does:**
- Simulates size-level demand depletion considering size coupling
- Models joint size demand (not independent SKU demand)
- Aggregates size-level risks to style level

**Why it's useful:**
- **Joint simulation**: Accounts for correlation between sizes
- **Size-level tracking**: Shows which sizes are at risk
- **Style-level aggregation**: Combines size risks into overall style risk

**How it works:**
1. Simulates demand for each size (using size-share forecast)
2. Tracks inventory depletion per size day-by-day
3. Computes stockout probability per size
4. Aggregates to style level (probability that any size stockouts)

**Where it's coded:**
- **File:** `simulation/size_demand_simulation.py`
- **Class:** `SizeDemandSimulator`
- **Key methods:**
  - `simulate_size_demand_depletion()`: Simulates per-size depletion
  - `compute_style_level_risk()`: Aggregates to style level

---

## 8. Decision Explanation

### Technique: Natural Language Explanation Generation

**What it does:**
- Generates human-readable explanations for recommendations
- Explains why a specific quantity was recommended
- Shows risk improvement and economic impact

**Why it's useful:**
- **Transparency**: Users understand why the AI made a recommendation
- **Trust**: Builds confidence in the system
- **Education**: Helps users learn better inventory practices
- **Justification**: Provides reasoning for decision-making

**How it works:**
1. Extracts key metrics from optimization results:
   - Recommended quantity
   - Risk improvement (before vs after)
   - Expected costs (overstock vs understock)
   - Cash impact
2. Formats into natural language explanation
3. Highlights key insights (risk reduction, cost savings)

**Where it's coded:**
- **File:** `explainability/decision_explainer.py`
- **Class:** `DecisionExplainer`
- **Key methods:**
  - `explain_reorder_decision()`: Generates explanation for single SKU
  - `explain_capital_allocation()`: Explains multi-SKU allocation

**Usage example:**
```python
explainer = DecisionExplainer()
explanation = explainer.explain_reorder_decision(
    optimization_result=result,
    current_inventory=100,
    unit_cost=500,
    comparison_result=comparison
)
# Returns: Human-readable explanation string
```

---

## 9. Pipeline Orchestration

### Technique: End-to-End Decision Pipeline

**What it does:**
- Orchestrates all components into a complete decision pipeline
- Runs forecasting → simulation → optimization → explanation
- Handles both single-SKU and multi-SKU scenarios

**Why it's useful:**
- **Complete workflow**: One function call does everything
- **Consistency**: Ensures all steps are executed in correct order
- **Reusability**: Same pipeline works for different products
- **Maintainability**: Centralized orchestration logic

**How it works:**
1. **Data preparation**: Loads historical sales data
2. **Training**: Trains forecasters for each SKU/style
3. **Forecasting**: Generates probabilistic demand forecasts
4. **Risk assessment**: Estimates current stockout risk
5. **Optimization**: Finds optimal reorder quantity
6. **Comparison**: Compares with naive/baseline (optional)
7. **Explanation**: Generates human-readable explanation
8. **Return results**: Complete recommendation with all metrics


  **Where it's coded:**
- **File:** `pipeline.py`
- **Class:** `InventoryDecisionPipeline`
- **Key methods:**
  - `train_forecaster()`: Trains demand forecaster for a SKU
  - `run_pipeline()`: Runs complete pipeline for single SKU
  - `run_multi_sku_pipeline()`: Runs pipeline with capital allocation

**Usage example:**
```python
pipeline = InventoryDecisionPipeline(
    unit_cost=100,
    selling_price=150,
    holding_cost_rate=0.02,
    n_simulations=5000
)

# Train forecaster
pipeline.train_forecaster(historical_data, sku_id="SKU001")

# Run pipeline
result = pipeline.run_pipeline(
    sku_id="SKU001",
    current_inventory=100,
    lead_time_days=14,
    min_order_quantity=50,
    available_cash=50000
)
# Returns: Complete recommendation with forecast, risk, optimization, explanation
```

---

## 10. Integration Points

### Backend API Integration

**Where decisions are generated:**
- **Supabase Edge Function:** `supabase/functions/generate-decisions/index.ts`
  - Currently uses simplified logic (placeholder)
  - Should be replaced with full pipeline integration
  - Receives product data, generates recommendations, saves to database

**Backend Service:**
- **File:** `backend/app/services/ai_service.py`
- **Class:** `AIService`
- **Purpose:** Integrates pipeline with FastAPI backend
- **Methods:**
  - `generate_recommendation()`: Generates recommendation for single product
  - `generate_recommendations_for_brand()`: Generates for multiple products with capital allocation

---

## 11. Key Algorithms Summary

### 1. Demand Forecasting Algorithm
- **Input:** Historical sales data (date, demand)
- **Output:** Probabilistic forecast (P10, P50, P90, mean, std)
- **Algorithm:** LightGBM quantile regression
- **Complexity:** O(n × m) where n = historical data points, m = features

### 2. Monte Carlo Simulation Algorithm
- **Input:** Forecast distribution, current inventory, lead time
- **Output:** Stockout probability, ending inventory distribution
- **Algorithm:** Monte Carlo sampling (5000 iterations)
- **Complexity:** O(simulations × lead_time_days)

### 3. Economic Optimization Algorithm
- **Input:** Forecast, constraints (MOQ, cash, risk tolerance)
- **Output:** Optimal order quantity, expected costs
- **Algorithm:** Grid search with loss minimization
- **Complexity:** O(feasible_quantities × simulations)

### 4. Capital Allocation Algorithm
- **Input:** Multiple SKUs, total cash available
- **Output:** Allocated quantities per SKU
- **Algorithm:** Greedy allocation by efficiency
- **Complexity:** O(n × log n) where n = number of SKUs

### 5. Size Curve Optimization Algorithm
- **Input:** Style forecast, size curves, current inventory by size
- **Output:** Optimal size breakdown, size-level risks
- **Algorithm:** Evaluate-all-curves, select best
- **Complexity:** O(curves × sizes × simulations)

---

## 12. Mathematical Foundations

### Expected Economic Loss Formula

```
Total Expected Loss = E[Overstock Cost] + E[Understock Cost]

Where:
- E[Overstock Cost] = Σ scenarios P(scenario) × Overstock_Cost(scenario)
- E[Understock Cost] = Σ scenarios P(scenario) × Understock_Cost(scenario)
```

### Stockout Probability Formula

```
Stockout Probability = (Number of simulations with negative ending inventory) / Total simulations
```

### Risk Categorization

```
Risk Category = {
    LOW    if stockout_probability < 0.05
    MEDIUM if 0.05 ≤ stockout_probability < 0.20
    HIGH   if stockout_probability ≥ 0.20
}
```

### Capital Allocation Efficiency

```
Efficiency = (Baseline Loss - Optimal Loss) / Incremental Cash Required

Where:
- Baseline Loss = Expected loss with no order or naive order
- Optimal Loss = Expected loss with optimal order
- Incremental Cash = Cash required for optimal order - baseline cash
```

---

## 13. Performance Characteristics

### Computational Complexity

- **Forecasting:** O(n × m) per SKU, where n = historical data, m = features
- **Simulation:** O(5000 × lead_time_days) per evaluation
- **Optimization:** O(feasible_quantities × simulation_cost)
- **Capital Allocation:** O(SKUs × optimization_cost)

### Scalability

- **Single SKU:** Processes in seconds
- **Multi-SKU (10-50 SKUs):** Processes in minutes
- **Large-scale (100+ SKUs):** May require batch processing or optimization

### Accuracy Considerations

- **Forecast accuracy:** Depends on data quality and quantity (minimum 30 days)
- **Simulation accuracy:** 5000 simulations provide ~1% precision
- **Optimization accuracy:** Grid search step size affects precision vs speed trade-off

---

## 14. Assumptions and Limitations

### Key Assumptions

1. **Demand distribution:** Assumed normal or quantile-based (may not hold for highly volatile products)
2. **Independence:** Daily demand is assumed independent (may not hold during promotions)
3. **Lead time:** Assumed constant (doesn't account for variability)
4. **Cost parameters:** Holding cost, markdown rate assumed constant

### Known Limitations

1. **No seasonality modeling:** Calendar features help but don't explicitly model seasons
2. **No promotion impact:** Doesn't account for marketing campaigns or discounts
3. **Single-location:** Doesn't handle multi-warehouse scenarios
4. **No supplier variability:** Assumes fixed lead time and reliable supply

### Future Improvements

1. Add explicit seasonality modeling
2. Incorporate promotion impact forecasting
3. Model supplier lead time variability
4. Support multi-location inventory
5. Add real-time demand updates

---

## 15. How to Use in Production

### Step 1: Prepare Data
- Ensure you have at least 30 days of historical sales data
- Data format: CSV with columns: `date`, `demand` (or `sales`, `quantity`)

### Step 2: Initialize Pipeline
```python
from pipeline import InventoryDecisionPipeline

pipeline = InventoryDecisionPipeline(
    unit_cost=product.unit_cost,
    selling_price=product.selling_price,
    holding_cost_rate=0.02,
    markdown_rate=0.1,
    n_simulations=5000
)
```

### Step 3: Train Forecaster
```python
historical_df = pd.DataFrame({
    'date': sales_history['date'],
    'demand': sales_history['demand']
})
pipeline.train_forecaster(historical_df, sku_id=f"product_{product.id}")
```

### Step 4: Run Pipeline
```python
result = pipeline.run_pipeline(
    sku_id=f"product_{product.id}",
    current_inventory=inventory.current_quantity,
    lead_time_days=product.lead_time_days,
    min_order_quantity=product.min_order_quantity,
    order_multiple=product.order_multiple,
    available_cash=available_cash
)
```

### Step 5: Extract Recommendation
```python
recommendation = {
    'recommended_quantity': result['optimization_result']['optimal_quantity'],
    'stockout_probability_before': result['current_risk']['stockout_probability'],
    'stockout_probability_after': result['optimization_result']['risk_metrics']['stockout_probability'],
    'expected_loss': result['cost_breakdown']['total_expected_loss'],
    'explanation': result['explanation']
}
```

---

## 16. Footwear-Specific Workflow

For footwear products, the workflow is slightly different:

### Step 1: Train Size-Share Forecaster
```python
from models.size_share_forecast import SizeShareForecaster

forecaster = SizeShareForecaster()
forecaster.train(
    sales_df=sales_by_size_df,  # DataFrame with date, size, demand
    style_id="STYLE001",
    sizes=["6", "7", "8", "9", "10", "11"]
)
```

### Step 2: Generate Size-Level Forecast
```python
forecast = forecaster.forecast(forecast_horizon_days=30)
# Returns: total_demand, size_shares, size_demands
```

### Step 3: Optimize Size Curve
```python
from optimization.size_curve_optimizer import SizeCurveOptimizer

optimizer = SizeCurveOptimizer(
    cost_model=footwear_cost_model,
    simulator=size_simulator
)

optimal_curve = optimizer.optimize_style_reorder(
    forecast=forecast,
    current_inventory_by_size={"6": 10, "7": 20, "8": 30, ...},
    size_curve_templates=valid_curves,
    available_cash=500000
)
```

---

## Summary

StockPilot uses a sophisticated combination of:
- **Machine Learning** (LightGBM) for demand forecasting
- **Monte Carlo Simulation** for risk assessment
- **Economic Optimization** for decision-making
- **Greedy Algorithms** for capital allocation
- **Footwear-Specific Models** for size-level decisions

All techniques work together to provide data-driven, economically-optimized inventory recommendations that balance risk, cost, and cash constraints.nd forecaster for a SKU
  - `run_pipeline()`: Runs complete pipeline for single SKU
  - `run_multi_sku_pipeline()`: Runs pipeline with capital allocation

**Usage example:**
```python
pipeline = InventoryDecisionPipeline(
    unit_cost=100,
    selling_price=150,
    holding_cost_rate=0.02,
    n_simulations=5000
)

# Train forecaster
pipeline.train_forecaster(historical_data, sku_id="SKU001")

# Run pipeline
result = pipeline.run_pipeline(
    sku_id="SKU001",
    current_inventory=100,
    lead_time_days=14,
    min_order_quantity=50,
    available_cash=50000
)
# Returns: Complete recommendation with forecast, risk, optimization, explanation
```

---

## 10. Integration Points

### Backend API Integration

**Where decisions are generated:**
- **Supabase Edge Function:** `supabase/functions/generate-decisions/index.ts`
  - Currently uses simplified logic (placeholder)
  - Should be replaced with full pipeline integration
  - Receives product data, generates recommendations, saves to database

**Backend Service:**
- **File:** `backend/app/services/ai_service.py`
- **Class:** `AIService`
- **Purpose:** Integrates pipeline with FastAPI backend
- **Methods:**
  - `generate_recommendation()`: Generates recommendation for single product
  - `generate_recommendations_for_brand()`: Generates for multiple products with capital allocation

---

## 11. Key Algorithms Summary

### 1. Demand Forecasting Algorithm
- **Input:** Historical sales data (date, demand)
- **Output:** Probabilistic forecast (P10, P50, P90, mean, std)
- **Algorithm:** LightGBM quantile regression
- **Complexity:** O(n × m) where n = historical data points, m = features

### 2. Monte Carlo Simulation Algorithm
- **Input:** Forecast distribution, current inventory, lead time
- **Output:** Stockout probability, ending inventory distribution
- **Algorithm:** Monte Carlo sampling (5000 iterations)
- **Complexity:** O(simulations × lead_time_days)

### 3. Economic Optimization Algorithm
- **Input:** Forecast, constraints (MOQ, cash, risk tolerance)
- **Output:** Optimal order quantity, expected costs
- **Algorithm:** Grid search with loss minimization
- **Complexity:** O(feasible_quantities × simulations)

### 4. Capital Allocation Algorithm
- **Input:** Multiple SKUs, total cash available
- **Output:** Allocated quantities per SKU
- **Algorithm:** Greedy allocation by efficiency
- **Complexity:** O(n × log n) where n = number of SKUs

### 5. Size Curve Optimization Algorithm
- **Input:** Style forecast, size curves, current inventory by size
- **Output:** Optimal size breakdown, size-level risks
- **Algorithm:** Evaluate-all-curves, select best
- **Complexity:** O(curves × sizes × simulations)

---

## 12. Mathematical Foundations

### Expected Economic Loss Formula

```
Total Expected Loss = E[Overstock Cost] + E[Understock Cost]

Where:
- E[Overstock Cost] = Σ scenarios P(scenario) × Overstock_Cost(scenario)
- E[Understock Cost] = Σ scenarios P(scenario) × Understock_Cost(scenario)
```

### Stockout Probability Formula

```
Stockout Probability = (Number of simulations with negative ending inventory) / Total simulations
```

### Risk Categorization

```
Risk Category = {
    LOW    if stockout_probability < 0.05
    MEDIUM if 0.05 ≤ stockout_probability < 0.20
    HIGH   if stockout_probability ≥ 0.20
}
```

### Capital Allocation Efficiency

```
Efficiency = (Baseline Loss - Optimal Loss) / Incremental Cash Required

Where:
- Baseline Loss = Expected loss with no order or naive order
- Optimal Loss = Expected loss with optimal order
- Incremental Cash = Cash required for optimal order - baseline cash
```

---

## 13. Performance Characteristics

### Computational Complexity

- **Forecasting:** O(n × m) per SKU, where n = historical data, m = features
- **Simulation:** O(5000 × lead_time_days) per evaluation
- **Optimization:** O(feasible_quantities × simulation_cost)
- **Capital Allocation:** O(SKUs × optimization_cost)

### Scalability

- **Single SKU:** Processes in seconds
- **Multi-SKU (10-50 SKUs):** Processes in minutes
- **Large-scale (100+ SKUs):** May require batch processing or optimization

### Accuracy Considerations

- **Forecast accuracy:** Depends on data quality and quantity (minimum 30 days)
- **Simulation accuracy:** 5000 simulations provide ~1% precision
- **Optimization accuracy:** Grid search step size affects precision vs speed trade-off

---

## 14. Assumptions and Limitations

### Key Assumptions

1. **Demand distribution:** Assumed normal or quantile-based (may not hold for highly volatile products)
2. **Independence:** Daily demand is assumed independent (may not hold during promotions)
3. **Lead time:** Assumed constant (doesn't account for variability)
4. **Cost parameters:** Holding cost, markdown rate assumed constant

### Known Limitations

1. **No seasonality modeling:** Calendar features help but don't explicitly model seasons
2. **No promotion impact:** Doesn't account for marketing campaigns or discounts
3. **Single-location:** Doesn't handle multi-warehouse scenarios
4. **No supplier variability:** Assumes fixed lead time and reliable supply

### Future Improvements

1. Add explicit seasonality modeling
2. Incorporate promotion impact forecasting
3. Model supplier lead time variability
4. Support multi-location inventory
5. Add real-time demand updates

---

## 15. How to Use in Production

### Step 1: Prepare Data
- Ensure you have at least 30 days of historical sales data
- Data format: CSV with columns: `date`, `demand` (or `sales`, `quantity`)

### Step 2: Initialize Pipeline
```python
from pipeline import InventoryDecisionPipeline

pipeline = InventoryDecisionPipeline(
    unit_cost=product.unit_cost,
    selling_price=product.selling_price,
    holding_cost_rate=0.02,
    markdown_rate=0.1,
    n_simulations=5000
)
```

### Step 3: Train Forecaster
```python
historical_df = pd.DataFrame({
    'date': sales_history['date'],
    'demand': sales_history['demand']
})
pipeline.train_forecaster(historical_df, sku_id=f"product_{product.id}")
```

### Step 4: Run Pipeline
```python
result = pipeline.run_pipeline(
    sku_id=f"product_{product.id}",
    current_inventory=inventory.current_quantity,
    lead_time_days=product.lead_time_days,
    min_order_quantity=product.min_order_quantity,
    order_multiple=product.order_multiple,
    available_cash=available_cash
)
```

### Step 5: Extract Recommendation
```python
recommendation = {
    'recommended_quantity': result['optimization_result']['optimal_quantity'],
    'stockout_probability_before': result['current_risk']['stockout_probability'],
    'stockout_probability_after': result['optimization_result']['risk_metrics']['stockout_probability'],
    'expected_loss': result['cost_breakdown']['total_expected_loss'],
    'explanation': result['explanation']
}
```

---

## 16. Footwear-Specific Workflow

For footwear products, the workflow is slightly different:

### Step 1: Train Size-Share Forecaster
```python
from models.size_share_forecast import SizeShareForecaster

forecaster = SizeShareForecaster()
forecaster.train(
    sales_df=sales_by_size_df,  # DataFrame with date, size, demand
    style_id="STYLE001",
    sizes=["6", "7", "8", "9", "10", "11"]
)
```

### Step 2: Generate Size-Level Forecast
```python
forecast = forecaster.forecast(forecast