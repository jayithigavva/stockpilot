'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { dashboardAPI, decisionsAPI } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'
import DecisionCard from '../components/DecisionCard'
import DecisionDetails from '../components/DecisionDetails'
import Sidebar from '../components/Sidebar'

interface DashboardStats {
  total_products: number
  total_inventory_value: number
  inventory_at_risk: number
  high_risk_skus: number
  avg_days_of_cover: number
  cash_freed: number
  pending_decisions: number
  pending_decisions_list: any[]
}

interface SelectedDecision {
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
  product_id: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [selectedDecision, setSelectedDecision] = useState<SelectedDecision | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }
      loadDashboard()
    }
    checkAuth()
  }, [router])

  const loadDashboard = async () => {
    try {
      const data = await dashboardAPI.getStats()
      setStats(data as DashboardStats)
    } catch (err) {
      console.error('Failed to load dashboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunAI = async () => {
    setGenerating(true)
    try {
      await decisionsAPI.generate()
      await loadDashboard()
    } catch (err) {
      console.error('Failed to generate recommendations:', err)
      alert('Failed to generate recommendations. Make sure you have products with sales history.')
    } finally {
      setGenerating(false)
    }
  }

  const handleAccept = async (decisionId: string) => {
    try {
      await decisionsAPI.accept(decisionId)
      await loadDashboard()
      setSelectedDecision(null)
    } catch (err) {
      console.error('Failed to accept decision:', err)
      alert('Failed to accept decision')
    }
  }

  const handleReject = async (decisionId: string) => {
    try {
      await decisionsAPI.reject(decisionId)
      await loadDashboard()
      setSelectedDecision(null)
    } catch (err) {
      console.error('Failed to reject decision:', err)
      alert('Failed to reject decision')
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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW':
        return 'text-green-600 bg-green-50'
      case 'MEDIUM':
        return 'text-amber-600 bg-amber-50'
      case 'HIGH':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-red-500">Failed to load dashboard</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Top: Big-picture health */}
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-semibold text-gray-900">Inventory Health</h1>
              <button
                onClick={handleRunAI}
                disabled={generating}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 text-sm font-medium"
              >
                {generating ? 'Generating...' : '🤖 Generate Recommendations'}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Card 1: Inventory Value */}
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
                <div className="text-sm font-medium text-gray-600 mb-1">Total Inventory</div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {formatCurrency(stats.total_inventory_value)}
                </div>
                <div className="text-xs text-gray-600">
                  {formatCurrency(stats.inventory_at_risk)} at risk
                </div>
              </div>

              {/* Card 2: Stockout Risk */}
              <div className={`rounded-xl p-6 border ${
                stats.high_risk_skus > 0 
                  ? 'bg-gradient-to-br from-red-50 to-red-100 border-red-200' 
                  : 'bg-gradient-to-br from-green-50 to-green-100 border-green-200'
              }`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Stockout Risk</div>
                <div className={`text-3xl font-bold mb-2 ${
                  stats.high_risk_skus > 0 ? 'text-red-700' : 'text-green-700'
                }`}>
                  {stats.high_risk_skus} SKUs
                </div>
                <div className="text-xs text-gray-600">
                  {stats.high_risk_skus > 0 ? 'HIGH risk' : 'All clear'}
                </div>
              </div>

              {/* Card 3: Days of Cover */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
                <div className="text-sm font-medium text-gray-600 mb-1">Days of Cover</div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stats.avg_days_of_cover} days
                </div>
                <div className="text-xs text-gray-600">Target: 30 days</div>
              </div>

              {/* Card 4: Cash Freed */}
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
                <div className="text-sm font-medium text-gray-600 mb-1">Cash Freed</div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {formatCurrency(stats.cash_freed)}
                </div>
                <div className="text-xs text-gray-600">This cycle</div>
              </div>
            </div>
          </div>
        </div>

        {/* Middle: What needs attention */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Recommended Actions</h2>

            {stats.pending_decisions === 0 ? (
              <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
                <div className="text-gray-400 mb-4 text-6xl">✓</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">All Clear</h3>
                <p className="text-gray-500 mb-6">No pending recommendations. Your inventory is optimized.</p>
                <button
                  onClick={handleRunAI}
                  disabled={generating}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 font-medium"
                >
                  {generating ? 'Generating...' : 'Generate New Recommendations'}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {stats.pending_decisions_list.map((decision: any) => {
                  const product = decision.product || {}
                  const daysUntilStockout = Math.ceil(
                    (decision.current_inventory / (decision.current_inventory / 30)) || 12
                  )
                  
                  return (
                    <DecisionCard
                      key={decision.id}
                      decision={{
                        id: decision.id,
                        product_name: product.name || 'Unknown Product',
                        sku: product.sku,
                        recommended_quantity: parseFloat(decision.recommended_quantity),
                        current_inventory: parseFloat(decision.current_inventory),
                        stockout_probability_before: parseFloat(decision.stockout_probability_before),
                        stockout_probability_after: parseFloat(decision.stockout_probability_after),
                        risk_category_before: decision.risk_category_before,
                        risk_category_after: decision.risk_category_after,
                        expected_overstock_cost: parseFloat(decision.expected_overstock_cost),
                        expected_understock_cost: parseFloat(decision.expected_understock_cost),
                        total_expected_loss: parseFloat(decision.total_expected_loss),
                        cash_locked: parseFloat(decision.cash_locked),
                        cash_freed: parseFloat(decision.cash_freed || 0),
                        explanation: decision.explanation || '',
                        product_id: decision.product_id,
                      }}
                      onViewDetails={() => {
                        setSelectedDecision({
                          id: decision.id,
                          product_name: product.name || 'Unknown Product',
                          sku: product.sku,
                          recommended_quantity: parseFloat(decision.recommended_quantity),
                          current_inventory: parseFloat(decision.current_inventory),
                          stockout_probability_before: parseFloat(decision.stockout_probability_before),
                          stockout_probability_after: parseFloat(decision.stockout_probability_after),
                          risk_category_before: decision.risk_category_before,
                          risk_category_after: decision.risk_category_after,
                          expected_overstock_cost: parseFloat(decision.expected_overstock_cost),
                          expected_understock_cost: parseFloat(decision.expected_understock_cost),
                          total_expected_loss: parseFloat(decision.total_expected_loss),
                          cash_locked: parseFloat(decision.cash_locked),
                          cash_freed: parseFloat(decision.cash_freed || 0),
                          explanation: decision.explanation || '',
                          product_id: decision.product_id,
                        })
                        setSidebarOpen(true)
                      }}
                      onAccept={() => handleAccept(decision.id)}
                      onReject={() => handleReject(decision.id)}
                      formatCurrency={formatCurrency}
                    />
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Decision Details Slide-over */}
      {selectedDecision && (
        <DecisionDetails
          decision={selectedDecision}
          isOpen={sidebarOpen}
          onClose={() => {
            setSidebarOpen(false)
            setSelectedDecision(null)
          }}
          onAccept={() => handleAccept(selectedDecision.id)}
          onReject={() => handleReject(selectedDecision.id)}
          formatCurrency={formatCurrency}
        />
      )}
    </div>
  )
}
