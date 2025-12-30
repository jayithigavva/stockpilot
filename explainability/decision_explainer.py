"""
Decision Explanation Module

Generates human-readable explanations of inventory decisions and their impact.
"""

from typing import Dict, Optional
import pandas as pd


class DecisionExplainer:
    """
    Generates human-readable explanations of reorder decisions.
    
    Explains:
    - Cash locked vs freed
    - Stockout risk reduction
    - Dead stock avoided
    - Inventory turnover improvement
    """
    
    def __init__(self, currency_symbol: str = '₹'):
        """
        Initialize decision explainer.
        
        Args:
            currency_symbol: Currency symbol to use in explanations
        """
        self.currency_symbol = currency_symbol
    
    def format_currency(self, amount: float) -> str:
        """
        Format currency amount with appropriate units.
        
        Args:
            amount: Amount in base currency units
            
        Returns:
            Formatted string (e.g., "₹1.9 lakh" or "₹50,000")
        """
        if abs(amount) >= 100000:
            lakhs = amount / 100000
            return f"{self.currency_symbol}{lakhs:.1f} lakh"
        elif abs(amount) >= 1000:
            thousands = amount / 1000
            return f"{self.currency_symbol}{thousands:.1f}K"
        else:
            return f"{self.currency_symbol}{amount:,.0f}"
    
    def explain_reorder_decision(
        self,
        optimization_result: Dict,
        current_inventory: float,
        unit_cost: float,
        selling_price: float,
        lead_time_days: int,
        comparison_result: Optional[Dict] = None
    ) -> str:
        """
        Generate explanation for a reorder decision.
        
        Args:
            optimization_result: Result from ReorderOptimizer.optimize_reorder()
            current_inventory: Current inventory level
            unit_cost: Cost per unit
            selling_price: Selling price per unit
            lead_time_days: Lead time in days
            comparison_result: Optional comparison with naive ordering
            
        Returns:
            Human-readable explanation string
        """
        optimal_qty = optimization_result['optimal_quantity']
        optimal_loss = optimization_result['optimal_loss']
        risk_metrics = optimization_result['risk_metrics']
        cash_locked = optimization_result['cash_locked']
        
        stockout_prob = risk_metrics['stockout_probability']
        risk_category = risk_metrics['risk_category']
        expected_ending_inv = risk_metrics['expected_ending_inventory']
        
        # Build explanation
        explanation_parts = []
        
        explanation_parts.append(f"📦 **Recommended Order: {optimal_qty:.0f} units**")
        explanation_parts.append("")
        
        # Cash impact
        explanation_parts.append(f"💰 **Cash Impact:**")
        explanation_parts.append(f"   - Cash locked: {self.format_currency(cash_locked)}")
        
        # Risk metrics
        explanation_parts.append("")
        explanation_parts.append(f"⚠️ **Stockout Risk:**")
        explanation_parts.append(f"   - Probability: {stockout_prob*100:.1f}%")
        explanation_parts.append(f"   - Risk category: {risk_category}")
        explanation_parts.append(f"   - Expected ending inventory: {expected_ending_inv:.0f} units")
        
        # Expected loss
        explanation_parts.append("")
        explanation_parts.append(f"📊 **Expected Economic Loss:**")
        explanation_parts.append(f"   - Total: {self.format_currency(optimal_loss)}")
        
        # Comparison with naive
        if comparison_result:
            explanation_parts.append("")
            explanation_parts.append(f"📈 **Comparison with Naive Ordering:**")
            
            naive_qty = comparison_result['naive_quantity']
            cash_saved = comparison_result['cash_saved']
            loss_reduction = comparison_result['loss_reduction']
            loss_reduction_pct = comparison_result['loss_reduction_pct']
            
            if cash_saved > 0:
                explanation_parts.append(
                    f"   - Ordering {optimal_qty:.0f} units instead of {naive_qty:.0f} "
                    f"frees {self.format_currency(cash_saved)}"
                )
            elif cash_saved < 0:
                explanation_parts.append(
                    f"   - Requires {self.format_currency(abs(cash_saved))} more cash "
                    f"than naive order of {naive_qty:.0f} units"
                )
            
            if loss_reduction > 0:
                explanation_parts.append(
                    f"   - Reduces expected loss by {self.format_currency(loss_reduction)} "
                    f"({loss_reduction_pct:.1f}%)"
                )
            
            optimal_risk = comparison_result['optimal_stockout_prob']
            naive_risk = comparison_result['naive_stockout_prob']
            if optimal_risk < naive_risk:
                explanation_parts.append(
                    f"   - Reduces stockout risk from {naive_risk*100:.1f}% to {optimal_risk*100:.1f}%"
                )
        
        return "\n".join(explanation_parts)
    
    def explain_capital_allocation(
        self,
        allocation_result: Dict,
        total_available_cash: float
    ) -> str:
        """
        Generate explanation for capital allocation across SKUs.
        
        Args:
            allocation_result: Result from CapitalAllocator.allocate_capital()
            total_available_cash: Total cash available
            
        Returns:
            Human-readable explanation string
        """
        allocations = allocation_result['allocations']
        total_cash_used = allocation_result['total_cash_used']
        remaining_cash = allocation_result['remaining_cash']
        allocation_order = allocation_result['allocation_order']
        
        explanation_parts = []
        
        explanation_parts.append(f"💼 **Capital Allocation Summary**")
        explanation_parts.append("")
        explanation_parts.append(f"Total available cash: {self.format_currency(total_available_cash)}")
        explanation_parts.append(f"Total cash allocated: {self.format_currency(total_cash_used)}")
        explanation_parts.append(f"Remaining cash: {self.format_currency(remaining_cash)}")
        explanation_parts.append("")
        
        explanation_parts.append("**Allocation by SKU (in priority order):**")
        explanation_parts.append("")
        
        for sku_id in allocation_order:
            alloc = allocations[sku_id]
            if alloc['quantity'] > 0:
                explanation_parts.append(
                    f"  - {sku_id}: {alloc['quantity']:.0f} units "
                    f"({self.format_currency(alloc['cash'])})"
                )
                if alloc['loss_avoided'] > 0:
                    explanation_parts.append(
                        f"    → Loss avoided: {self.format_currency(alloc['loss_avoided'])}"
                    )
        
        return "\n".join(explanation_parts)
    
    def generate_summary_report(
        self,
        optimization_result: Dict,
        risk_metrics: Dict,
        cost_breakdown: Dict,
        comparison_result: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Generate a summary report as a DataFrame.
        
        Args:
            optimization_result: Result from optimizer
            risk_metrics: Risk metrics dictionary
            cost_breakdown: Cost breakdown dictionary
            comparison_result: Optional comparison result
            
        Returns:
            DataFrame with summary metrics
        """
        data = {
            'Metric': [],
            'Value': []
        }
        
        # Basic metrics
        data['Metric'].extend([
            'Recommended Order Quantity',
            'Cash Locked',
            'Stockout Probability',
            'Risk Category',
            'Expected Ending Inventory'
        ])
        data['Value'].extend([
            f"{optimization_result['optimal_quantity']:.0f} units",
            self.format_currency(optimization_result['cash_locked']),
            f"{risk_metrics['stockout_probability']*100:.1f}%",
            risk_metrics['risk_category'],
            f"{risk_metrics['expected_ending_inventory']:.0f} units"
        ])
        
        # Cost breakdown
        if 'expected_overstock_cost' in cost_breakdown:
            data['Metric'].extend([
                'Expected Overstock Cost',
                'Expected Understock Cost',
                'Total Expected Loss'
            ])
            data['Value'].extend([
                self.format_currency(cost_breakdown['expected_overstock_cost']),
                self.format_currency(cost_breakdown['expected_understock_cost']),
                self.format_currency(cost_breakdown['total_expected_loss'])
            ])
        
        # Comparison
        if comparison_result:
            data['Metric'].extend([
                'Naive Order Quantity',
                'Naive Loss',
                'Loss Reduction',
                'Cash Saved'
            ])
            data['Value'].extend([
                f"{comparison_result['naive_quantity']:.0f} units",
                self.format_currency(comparison_result['naive_loss']),
                self.format_currency(comparison_result['loss_reduction']),
                self.format_currency(comparison_result['cash_saved'])
            ])
        
        return pd.DataFrame(data)

