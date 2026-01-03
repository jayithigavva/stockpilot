'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { decisionsAPI } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'
import Sidebar from '../components/Sidebar'

interface Recommendation {
  product_id?: string
  style_id?: string
  product_name?: string
  style_name?: string
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
  decision_id: string
  // Footwear-specific
  size_breakdown?: { [size: string]: number }
  size_risk_breakdown?: { [size: string]: string }
  size_cash_at_risk?: { [size: string]: number }
  is_style_level?: boolean
}

export default function DecisionsPage() {
  const router = useRouter()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [accepting, setAccepting] = useState<string | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }
      loadRecommendations()
    }
    checkAuth()
  }, [router])

  const loadRecommendations = async () => {
    try {
      // Get pending decisions from Supabase
      const decisions = await decisionsAPI.list('PENDING')
      
      // Get product/style details for each decision
      const recommendations = await Promise.all(decisions.map(async (d: any) => {
        const product = d.product || {}
        const style = d.style || {}
        const isStyleLevel = !!d.style_id
        
        return {
          product_id: d.product_id,
          style_id: d.style_id,
          product_name: product.name || 'Unknown Product',
          style_name: style.name || 'Unknown Style',
          sku: product.sku || '',
          recommended_quantity: parseFloat(d.recommended_quantity),
          current_inventory: parseFloat(d.current_inventory),
          stockout_probability_before: parseFloat(d.stockout_probability_before),
          stockout_probability_after: parseFloat(d.stockout_probability_after),
          risk_category_before: d.risk_category_before,
          risk_category_after: d.risk_category_after,
          expected_overstock_cost: parseFloat(d.expected_overstock_cost),
          expected_understock_cost: parseFloat(d.expected_understock_cost),
          total_expected_loss: parseFloat(d.total_expected_loss),
          cash_locked: parseFloat(d.cash_locked),
          cash_freed: parseFloat(d.cash_freed || 0),
          explanation: isStyleLevel 
            ? `Order ${d.recommended_quantity} units for style. Cash locked: ₹${parseFloat(d.cash_locked).toLocaleString()}. Risk: ${d.risk_category_before} → ${d.risk_category_after}.`
            : `Order ${d.recommended_quantity} units. Cash locked: ₹${parseFloat(d.cash_locked).toLocaleString()}. Risk: ${d.risk_category_before} → ${d.risk_category_after}.`,
          decision_id: d.id,
          is_style_level: isStyleLevel,
          size_breakdown: d.size_breakdown || {},
          size_risk_breakdown: d.size_risk_breakdown || {},
          size_cash_at_risk: d.size_cash_at_risk || {},
        }
      }))
      
      setRecommendations(recommendations)
    } catch (err) {
      console.error('Failed to load recommendations:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAccept = async (decisionId: string) => {
    setAccepting(decisionId)
    try {
      await decisionsAPI.accept(decisionId)
      await loadRecommendations()
      alert('Decision accepted! Inventory updated.')
    } catch (err) {
      console.error('Failed to accept decision:', err)
      alert('Failed to accept decision')
    } finally {
      setAccepting(null)
    }
  }

  const formatCurrency = (amount: number) => {
    if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`
    } else if (amount >= 1000) {
      return `₹${(amount / 1000).toFixed(1)}K`
    }
    return `₹${amount.toFixed(0)}`
  }

  const getRiskColor = (category: string) => {
    switch (category) {
      case 'LOW':
        return 'bg-green-100 text-green-800'
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800'
      case 'HIGH':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <h1 className="text-2xl font-semibold text-gray-900">Reorder Decisions</h1>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-6 py-6">
        <h2 className="text-2xl font-bold mb-6">Reorder Recommendations</h2>

        {recommendations.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 mb-4">No pending recommendations.</p>
            <a
              href="/dashboard"
              className="text-primary-600 hover:underline"
            >
              Go to Dashboard to generate recommendations
            </a>
          </div>
        ) : (
          <div className="space-y-6">
            {recommendations.map((rec) => (
              <div key={rec.decision_id} className="bg-white rounded-lg shadow p-6 mb-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold">
                      {rec.is_style_level ? rec.style_name : rec.product_name}
                    </h3>
                    <p className="text-gray-600">
                      {rec.is_style_level ? `Style ID: ${rec.style_id}` : `Product ID: ${rec.product_id}`}
                      {rec.sku && ` • SKU: ${rec.sku}`}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded text-sm ${getRiskColor(rec.risk_category_after)}`}>
                    {rec.risk_category_after} Risk
                  </span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-500">Recommended Quantity</p>
                    <p className="text-lg font-semibold">{rec.recommended_quantity.toFixed(0)} units</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Current Inventory</p>
                    <p className="text-lg font-semibold">{rec.current_inventory.toFixed(0)} units</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Cash Locked</p>
                    <p className="text-lg font-semibold">{formatCurrency(rec.cash_locked)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Stockout Risk</p>
                    <p className="text-lg font-semibold">
                      {(rec.stockout_probability_after * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                <div className="bg-gray-50 p-4 rounded mb-4">
                  <h4 className="font-medium mb-2">Risk Improvement</h4>
                  <div className="flex items-center space-x-4">
                    <div>
                      <p className="text-sm text-gray-500">Before</p>
                      <p className="font-semibold">{(rec.stockout_probability_before * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-gray-400">→</div>
                    <div>
                      <p className="text-sm text-gray-500">After</p>
                      <p className="font-semibold">{(rec.stockout_probability_after * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>

                {rec.is_style_level && rec.size_breakdown && Object.keys(rec.size_breakdown).length > 0 && (
                  <div className="bg-purple-50 p-4 rounded mb-4">
                    <h4 className="font-medium mb-3">Size Breakdown</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.entries(rec.size_breakdown).map(([size, qty]: [string, any]) => (
                        <div key={size} className="bg-white p-3 rounded border">
                          <div className="text-xs text-gray-500">Size {size}</div>
                          <div className="text-lg font-semibold">{qty} units</div>
                          {rec.size_risk_breakdown?.[size] && (
                            <div className={`text-xs mt-1 px-2 py-0.5 rounded inline-block ${getRiskColor(rec.size_risk_breakdown[size])}`}>
                              {rec.size_risk_breakdown[size]}
                            </div>
                          )}
                          {rec.size_cash_at_risk?.[size] && (
                            <div className="text-xs text-gray-600 mt-1">
                              Risk: {formatCurrency(rec.size_cash_at_risk[size])}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 p-4 rounded mb-4">
                  <pre className="text-sm whitespace-pre-wrap">{rec.explanation}</pre>
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={() => handleAccept(rec.decision_id)}
                    disabled={accepting === rec.decision_id}
                    className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                  >
                    {accepting === rec.decision_id ? 'Accepting...' : '✓ Accept Decision'}
                  </button>
                  <button
                    onClick={async () => {
                      await decisionsAPI.reject(rec.decision_id)
                      await loadRecommendations()
                    }}
                    className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition"
                  >
                    ✗ Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
          </div>
        </div>
      </div>
    </div>
  )
}

