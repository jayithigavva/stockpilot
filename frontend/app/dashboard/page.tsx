'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { dashboardAPI, decisionsAPI } from '@/lib/api'
import Link from 'next/link'

interface DashboardStats {
  total_products: number
  total_inventory_value: number
  total_cash_locked: number
  high_risk_products: number
  pending_decisions: number
  recent_decisions: any[]
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
      return
    }
    loadDashboard()
  }, [router])

  const loadDashboard = async () => {
    try {
      const data = await dashboardAPI.getStats()
      setStats(data)
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
      await loadDashboard() // Reload to show new decisions
    } catch (err) {
      console.error('Failed to generate recommendations:', err)
      alert('Failed to generate recommendations. Make sure you have products with sales history.')
    } finally {
      setGenerating(false)
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

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!stats) {
    return <div className="min-h-screen flex items-center justify-center">Failed to load dashboard</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold">StockPilot</h1>
            <button
              onClick={() => {
                localStorage.removeItem('access_token')
                router.push('/login')
              }}
              className="text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
          <button
            onClick={handleRunAI}
            disabled={generating}
            className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition disabled:opacity-50"
          >
            {generating ? 'Generating Recommendations...' : '🤖 Run AI Recommendations'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Total Products</h3>
            <p className="text-3xl font-bold">{stats.total_products}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Inventory Value</h3>
            <p className="text-3xl font-bold">{formatCurrency(stats.total_inventory_value)}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-1">Cash Locked</h3>
            <p className="text-3xl font-bold">{formatCurrency(stats.total_cash_locked)}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500 mb-1">High Risk Products</h3>
            <p className="text-3xl font-bold text-red-600">{stats.high_risk_products}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold">Pending Decisions ({stats.pending_decisions})</h3>
          </div>
          <div className="p-6">
            <Link
              href="/decisions"
              className="text-primary-600 hover:underline"
            >
              View all decisions →
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold">Recent Decisions</h3>
          </div>
          <div className="p-6">
            {stats.recent_decisions.length === 0 ? (
              <p className="text-gray-500">No decisions yet. Click "Run AI Recommendations" to generate suggestions.</p>
            ) : (
              <div className="space-y-4">
                {stats.recent_decisions.map((decision) => (
                  <div key={decision.id} className="border-b pb-4 last:border-0">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium">{decision.product_name}</h4>
                        <p className="text-sm text-gray-600">
                          Recommended: {decision.recommended_quantity.toFixed(0)} units
                        </p>
                        <p className="text-sm text-gray-600">
                          Cash: {formatCurrency(decision.cash_locked)}
                        </p>
                      </div>
                      <span className={`px-3 py-1 rounded text-sm ${
                        decision.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                        decision.status === 'ACCEPTED' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {decision.status}
                      </span>
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

