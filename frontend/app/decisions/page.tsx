'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { decisionsAPI } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'

interface Recommendation {
  product_id: string
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
  decision_id: string
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
      
      // Get product details for each decision
      const recommendations = await Promise.all(decisions.map(async (d: any) => {
        const product = d.product || {}
        return {
          product_id: d.product_id,
          product_name: product.name || 'Unknown Product',
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
          explanation: `Order ${d.recommended_quantity} units. Cash locked: ₹${parseFloat(d.cash_locked).toLocaleString()}. Risk: ${d.risk_category_before} → ${d.risk_category_after}.`,
          decision_id: d.id
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
    setAccepting(parseInt(decisionId))
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
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold">StockPilot</h1>
            <div className="space-x-4">
              <a href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</a>
              <button
                onClick={async () => {
                  await supabase.auth.signOut()
                  router.push('/login')
                }}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
              <div key={rec.product_id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold">{rec.product_name}</h3>
                    <p className="text-gray-600">Product ID: {rec.product_id}</p>
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

                <div className="bg-blue-50 p-4 rounded mb-4">
                  <pre className="text-sm whitespace-pre-wrap">{rec.explanation}</pre>
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={() => handleAccept(rec.decision_id)}
                    disabled={accepting === rec.product_id}
                    className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50"
                  >
                    {accepting === rec.product_id ? 'Accepting...' : '✓ Accept Decision'}
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
  )
}

