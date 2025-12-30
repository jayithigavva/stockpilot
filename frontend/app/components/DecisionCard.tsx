'use client'

interface DecisionCardProps {
  decision: {
    id: string
    product_name: string
    sku?: string
    recommended_quantity: number
    current_inventory: number
    stockout_probability_before: number
    stockout_probability_after: number
    risk_category_before: string
    risk_category_after: string
    expected_overstock_cost?: number
    expected_understock_cost?: number
    total_expected_loss?: number
    cash_locked: number
    cash_freed: number
    explanation?: string
    product_id: string
  }
  onViewDetails: () => void
  onAccept: () => void
  onReject: () => void
  formatCurrency: (amount: number) => string
}

export default function DecisionCard({ decision, onViewDetails, onAccept, onReject, formatCurrency }: DecisionCardProps) {
  const riskReduction = ((decision.stockout_probability_before - decision.stockout_probability_after) * 100).toFixed(0)
  const daysUntilStockout = Math.ceil(decision.current_inventory / (decision.current_inventory / 30) || 12)

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between gap-6">
        {/* Left: Product Info */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <h3 className="text-lg font-semibold text-gray-900">{decision.product_name}</h3>
            {decision.sku && (
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {decision.sku}
              </span>
            )}
          </div>
          
          <div className="space-y-2 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="font-medium">Current stock:</span>
              <span>{decision.current_inventory.toFixed(0)} units</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-medium">Stockout risk in:</span>
              <span className="text-amber-600 font-semibold">{daysUntilStockout} days</span>
            </div>
          </div>
        </div>

        {/* Middle: Intelligence */}
        <div className="flex-1 border-l border-r border-gray-200 px-6">
          <div className="space-y-3">
            <div>
              <div className="text-sm text-gray-600 mb-1">Risk Reduction</div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-semibold text-red-600">
                  {(decision.stockout_probability_before * 100).toFixed(0)}%
                </span>
                <span className="text-gray-400">→</span>
                <span className="text-lg font-semibold text-green-600">
                  {(decision.stockout_probability_after * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-600 mb-1">Suggested Order</div>
              <div className="text-lg font-semibold text-gray-900">
                {decision.recommended_quantity.toFixed(0)} units
              </div>
            </div>
          </div>
        </div>

        {/* Right: Cash Impact */}
        <div className="flex-1 text-right">
          <div className="space-y-2">
            <div>
              <div className="text-sm text-gray-600 mb-1">Order Value</div>
              <div className="text-xl font-bold text-gray-900">
                {formatCurrency(decision.cash_locked)}
              </div>
            </div>
            {decision.cash_freed > 0 && (
              <div className="inline-flex items-center gap-1 bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-medium">
                <span>✓</span>
                <span>Cash saved: {formatCurrency(decision.cash_freed)}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom: Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between">
        <button
          onClick={onViewDetails}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
        >
          <span>👀</span>
          <span>View details</span>
        </button>
        
        <div className="flex items-center gap-3">
          <button
            onClick={onReject}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
          >
            Reject
          </button>
          <button
            onClick={onAccept}
            className="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition flex items-center gap-2"
          >
            <span>✓</span>
            <span>Accept Decision</span>
          </button>
        </div>
      </div>
    </div>
  )
}

