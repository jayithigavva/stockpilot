'use client'

interface DecisionDetailsProps {
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
    expected_overstock_cost: number
    expected_understock_cost: number
    total_expected_loss: number
    cash_locked: number
    cash_freed: number
    explanation: string
  }
  isOpen: boolean
  onClose: () => void
  onAccept: () => void
  onReject: () => void
  formatCurrency: (amount: number) => string
}

export default function DecisionDetails({ 
  decision, 
  isOpen, 
  onClose, 
  onAccept, 
  onReject, 
  formatCurrency 
}: DecisionDetailsProps) {
  if (!isOpen) return null

  const riskReduction = ((decision.stockout_probability_before - decision.stockout_probability_after) * 100).toFixed(0)
  const expectedLossReduction = decision.total_expected_loss

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-30 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* Slide-over Panel */}
      <div className={`fixed right-0 top-0 h-full w-full max-w-2xl bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="h-full flex flex-col overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{decision.product_name}</h2>
              {decision.sku && (
                <p className="text-sm text-gray-500 mt-1">{decision.sku}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 px-6 py-6 space-y-8">
            {/* Before/After Comparison */}
            <div className="grid grid-cols-2 gap-4">
              {/* If you do nothing */}
              <div className="bg-red-50 rounded-xl p-6 border border-red-200">
                <h3 className="text-sm font-semibold text-red-900 mb-4">If you do nothing:</h3>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Stockout Probability</div>
                    <div className="text-2xl font-bold text-red-700">
                      {(decision.stockout_probability_before * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Expected Lost Sales</div>
                    <div className="text-xl font-semibold text-red-700">
                      {formatCurrency(decision.expected_understock_cost)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Risk Level</div>
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                      decision.risk_category_before === 'HIGH' ? 'bg-red-100 text-red-800' :
                      decision.risk_category_before === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {decision.risk_category_before}
                    </span>
                  </div>
                </div>
              </div>

              {/* If you accept AI decision */}
              <div className="bg-green-50 rounded-xl p-6 border border-green-200">
                <h3 className="text-sm font-semibold text-green-900 mb-4">If you accept AI decision:</h3>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Stockout Probability</div>
                    <div className="text-2xl font-bold text-green-700">
                      {(decision.stockout_probability_after * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Expected Loss</div>
                    <div className="text-xl font-semibold text-green-700">
                      {formatCurrency(decision.total_expected_loss)}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Risk Level</div>
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                      decision.risk_category_after === 'HIGH' ? 'bg-red-100 text-red-800' :
                      decision.risk_category_after === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {decision.risk_category_after}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendation Details */}
            <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
              <h3 className="text-sm font-semibold text-blue-900 mb-4">Recommendation</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Order Quantity</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {decision.recommended_quantity.toFixed(0)} units
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-600 mb-1">Order Value</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(decision.cash_locked)}
                    </div>
                  </div>
                </div>
                {decision.cash_freed > 0 && (
                  <div className="pt-4 border-t border-blue-200">
                    <div className="flex items-center gap-2">
                      <span className="text-green-600 text-lg">✓</span>
                      <div>
                        <div className="text-xs text-gray-600">Cash Saved vs Manual Ordering</div>
                        <div className="text-lg font-semibold text-green-700">
                          {formatCurrency(decision.cash_freed)}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Explanation */}
            {decision.explanation && (
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Why this decision?</h3>
                <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {decision.explanation}
                </p>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3">
            <button
              onClick={onReject}
              className="px-6 py-3 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              Reject
            </button>
            <button
              onClick={onAccept}
              className="px-6 py-3 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition flex items-center gap-2"
            >
              <span>✓</span>
              <span>Accept Decision</span>
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

