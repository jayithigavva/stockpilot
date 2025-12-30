'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { settingsAPI } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'
import Sidebar from '../components/Sidebar'

export default function SettingsPage() {
  const router = useRouter()
  const [settings, setSettings] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [availableCash, setAvailableCash] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }
      loadSettings()
    }
    checkAuth()
  }, [router])

  const loadSettings = async () => {
    try {
      const data = await settingsAPI.getBrandSettings()
      setSettings(data)
      setAvailableCash(data.available_cash || 0)
    } catch (err: any) {
      setError(err.message || 'Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateCash = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      await settingsAPI.updateAvailableCash(availableCash)
      setSuccess('Available cash updated successfully!')
      await loadSettings()
    } catch (err: any) {
      setError(err.message || 'Failed to update cash')
    }
  }

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        <div className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}

            {/* Free Plan Status */}
            {settings?.plan_type === 'free' && settings?.free_plan_days_remaining !== null && (
              <div className={`rounded-xl p-6 border-2 ${
                settings.free_plan_days_remaining <= 7
                  ? 'bg-red-50 border-red-200'
                  : settings.free_plan_days_remaining <= 14
                  ? 'bg-amber-50 border-amber-200'
                  : 'bg-blue-50 border-blue-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">Free Plan Status</h3>
                    <p className="text-sm text-gray-600">
                      {settings.free_plan_days_remaining > 0
                        ? `${settings.free_plan_days_remaining} days remaining`
                        : 'Free plan has ended'}
                    </p>
                  </div>
                  <div className="text-3xl font-bold text-gray-900">
                    {settings.free_plan_days_remaining}
                  </div>
                </div>
                {settings.free_plan_days_remaining <= 7 && (
                  <div className="mt-4 pt-4 border-t border-red-200">
                    <p className="text-sm text-red-700">
                      Your free plan is ending soon. Consider upgrading to continue using StockPilot.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Available Cash */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Cash</h2>
              <p className="text-sm text-gray-600 mb-4">
                Set the amount of cash available for inventory purchases. This helps AI recommendations stay within your budget.
              </p>
              <form onSubmit={handleUpdateCash} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Available Cash (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={availableCash}
                    onChange={(e) => setAvailableCash(parseFloat(e.target.value) || 0)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                    placeholder="Enter available cash"
                  />
                  <p className="mt-2 text-xs text-gray-500">
                    Current: {formatCurrency(settings?.available_cash || 0)}
                  </p>
                </div>
                <button
                  type="submit"
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  Update Cash
                </button>
              </form>
            </div>

            {/* Account Info */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Brand Name</label>
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900">
                    {settings?.brand_name || 'N/A'}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Plan Type</label>
                  <div className="px-4 py-2 bg-gray-50 rounded-lg text-gray-900 capitalize">
                    {settings?.plan_type || 'free'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

