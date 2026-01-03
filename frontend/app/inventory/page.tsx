'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { inventoryAPI, productsAPI } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'
import Sidebar from '../components/Sidebar'

export default function InventoryPage() {
  const router = useRouter()
  const [inventory, setInventory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editQuantity, setEditQuantity] = useState(0)
  const [expandedStyles, setExpandedStyles] = useState<Set<string>>(new Set())
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }
      loadInventory()
    }
    checkAuth()
  }, [router])

  const loadInventory = async () => {
    try {
      const data = await inventoryAPI.list()
      setInventory(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load inventory')
    } finally {
      setLoading(false)
    }
  }

  // Group inventory by style for footwear products
  const groupByStyle = () => {
    const styleGroups: { [key: string]: any[] } = {}
    const regularProducts: any[] = []

    inventory.forEach((item) => {
      const product = item.product || {}
      if (product.style_id && product.style) {
        const styleId = product.style_id
        if (!styleGroups[styleId]) {
          styleGroups[styleId] = {
            style: product.style,
            items: [],
            totalQuantity: 0,
            totalValue: 0,
          }
        }
        styleGroups[styleId].items.push(item)
        styleGroups[styleId].totalQuantity += item.current_quantity || 0
        styleGroups[styleId].totalValue += (item.current_quantity || 0) * (product.unit_cost || 0)
      } else {
        regularProducts.push(item)
      }
    })

    return { styleGroups, regularProducts }
  }

  const handleUpdate = async (productId: string) => {
    setError('')
    setSuccess('')

    try {
      await inventoryAPI.update(productId, editQuantity)
      setSuccess('Inventory updated successfully!')
      setEditingId(null)
      await loadInventory()
    } catch (err: any) {
      setError(err.message || 'Failed to update inventory')
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
            <h1 className="text-2xl font-semibold text-gray-900">Inventory Management</h1>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-6 py-6">
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                {success}
              </div>
            )}

            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Current Inventory ({inventory.length} items)</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Quantity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit Cost</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Value</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Updated</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {(() => {
                      const { styleGroups, regularProducts } = groupByStyle()
                      const rows: JSX.Element[] = []

                      // Add style groups
                      Object.entries(styleGroups).forEach(([styleId, group]: [string, any]) => {
                        const isExpanded = expandedStyles.has(styleId)
                        rows.push(
                          <tr key={`style-${styleId}`} className="bg-blue-50">
                            <td colSpan={7} className="px-6 py-3">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <button
                                    onClick={() => {
                                      const newExpanded = new Set(expandedStyles)
                                      if (isExpanded) {
                                        newExpanded.delete(styleId)
                                      } else {
                                        newExpanded.add(styleId)
                                      }
                                      setExpandedStyles(newExpanded)
                                    }}
                                    className="text-gray-600 hover:text-gray-900"
                                  >
                                    {isExpanded ? '▼' : '▶'}
                                  </button>
                                  <span className="font-semibold text-gray-900">
                                    {group.style.name} ({group.style.style_code})
                                  </span>
                                </div>
                                <div className="flex items-center gap-6 text-sm">
                                  <span className="text-gray-600">Total: <strong>{group.totalQuantity.toFixed(0)}</strong></span>
                                  <span className="text-gray-600">Value: <strong>{formatCurrency(group.totalValue)}</strong></span>
                                </div>
                              </div>
                            </td>
                          </tr>
                        )

                        if (isExpanded) {
                          group.items.forEach((item: any) => {
                            const product = item.product || {}
                            const totalValue = (item.current_quantity || 0) * (product.unit_cost || 0)
                            const isEditing = editingId === product.id
                            rows.push(
                              <tr key={item.id} className="hover:bg-gray-50 bg-gray-50">
                                <td className="px-6 py-4 text-sm pl-12">
                                  <div>
                                    <div className="font-medium text-gray-900">{product.name || 'Unknown'}</div>
                                    <div className="text-xs text-gray-500">
                                      Size {product.size || '-'}
                                      {product.color && ` • ${product.color}`}
                                      {product.width && ` • ${product.width}`}
                                    </div>
                                  </div>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">{product.sku || '-'}</td>
                                <td className="px-6 py-4 text-sm text-gray-900">
                                  {isEditing ? (
                                    <input
                                      type="number"
                                      step="0.01"
                                      value={editQuantity}
                                      onChange={(e) => setEditQuantity(parseFloat(e.target.value) || 0)}
                                      className="w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                                      autoFocus
                                    />
                                  ) : (
                                    <span className="font-semibold">{item.current_quantity.toFixed(0)}</span>
                                  )}
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">{formatCurrency(product.unit_cost || 0)}</td>
                                <td className="px-6 py-4 text-sm font-semibold text-gray-900">{formatCurrency(totalValue)}</td>
                                <td className="px-6 py-4 text-sm text-gray-600">
                                  {item.last_updated ? new Date(item.last_updated).toLocaleDateString() : '-'}
                                </td>
                                <td className="px-6 py-4 text-sm">
                                  {isEditing ? (
                                    <div className="flex items-center gap-2">
                                      <button
                                        onClick={() => handleUpdate(product.id)}
                                        className="text-green-600 hover:text-green-700 font-medium"
                                      >
                                        Save
                                      </button>
                                      <button
                                        onClick={() => {
                                          setEditingId(null)
                                          setEditQuantity(0)
                                        }}
                                        className="text-gray-600 hover:text-gray-700 font-medium"
                                      >
                                        Cancel
                                      </button>
                                    </div>
                                  ) : (
                                    <button
                                      onClick={() => {
                                        setEditingId(product.id)
                                        setEditQuantity(item.current_quantity)
                                      }}
                                      className="text-blue-600 hover:text-blue-700 font-medium"
                                    >
                                      Edit
                                    </button>
                                  )}
                                </td>
                              </tr>
                            )
                          })
                        }
                      })

                      // Add regular products
                      regularProducts.forEach((item) => {
                        const product = item.product || {}
                        const totalValue = (item.current_quantity || 0) * (product.unit_cost || 0)
                        const isEditing = editingId === product.id
                        rows.push(
                          <tr key={item.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">{product.name || 'Unknown'}</td>
                            <td className="px-6 py-4 text-sm text-gray-600">{product.sku || '-'}</td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {isEditing ? (
                                <input
                                  type="number"
                                  step="0.01"
                                  value={editQuantity}
                                  onChange={(e) => setEditQuantity(parseFloat(e.target.value) || 0)}
                                  className="w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                                  autoFocus
                                />
                              ) : (
                                <span className="font-semibold">{item.current_quantity.toFixed(0)}</span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">{formatCurrency(product.unit_cost || 0)}</td>
                            <td className="px-6 py-4 text-sm font-semibold text-gray-900">{formatCurrency(totalValue)}</td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {item.last_updated ? new Date(item.last_updated).toLocaleDateString() : '-'}
                            </td>
                            <td className="px-6 py-4 text-sm">
                              {isEditing ? (
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => handleUpdate(product.id)}
                                    className="text-green-600 hover:text-green-700 font-medium"
                                  >
                                    Save
                                  </button>
                                  <button
                                    onClick={() => {
                                      setEditingId(null)
                                      setEditQuantity(0)
                                    }}
                                    className="text-gray-600 hover:text-gray-700 font-medium"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => {
                                    setEditingId(product.id)
                                    setEditQuantity(item.current_quantity)
                                  }}
                                  className="text-blue-600 hover:text-blue-700 font-medium"
                                >
                                  Edit
                                </button>
                              )}
                            </td>
                          </tr>
                        )
                      })

                      return rows
                    })()}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
            {(() => {
              const { styleGroups, regularProducts } = groupByStyle()
              const styleKeys = Object.keys(styleGroups)
              
              return (
                <div className="space-y-6">
                  {/* Footwear Styles Section */}
                  {styleKeys.length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                      <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Footwear Styles ({styleKeys.length})</h2>
                      </div>
                      <div className="divide-y divide-gray-200">
                        {styleKeys.map((styleId) => {
                          const group = styleGroups[styleId]
                          const isExpanded = expandedStyles.has(styleId)
                          const sizeBreakdown: { [size: string]: { qty: number; value: number } } = {}
                          
                          group.items.forEach((item: any) => {
                            const product = item.product || {}
                            const size = product.size || 'N/A'
                            if (!sizeBreakdown[size]) {
                              sizeBreakdown[size] = { qty: 0, value: 0 }
                            }
                            sizeBreakdown[size].qty += item.current_quantity || 0
                            sizeBreakdown[size].value += (item.current_quantity || 0) * (product.unit_cost || 0)
                          })

                          return (
                            <div key={styleId} className="hover:bg-gray-50">
                              <div
                                className="px-6 py-4 flex items-center justify-between cursor-pointer"
                                onClick={() => {
                                  const newExpanded = new Set(expandedStyles)
                                  if (isExpanded) {
                                    newExpanded.delete(styleId)
                                  } else {
                                    newExpanded.add(styleId)
                                  }
                                  setExpandedStyles(newExpanded)
                                }}
                              >
                                <div className="flex-1">
                                  <div className="flex items-center gap-3">
                                    <span className="text-lg">{isExpanded ? '▼' : '▶'}</span>
                                    <div>
                                      <h3 className="text-sm font-semibold text-gray-900">
                                        {group.style.name} ({group.style.style_code})
                                      </h3>
                                      <p className="text-xs text-gray-500">
                                        Total: {group.totalQuantity.toFixed(0)} units • {formatCurrency(group.totalValue)}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                                <div className="text-sm text-gray-600">
                                  {Object.keys(sizeBreakdown).length} sizes
                                </div>
                              </div>
                              
                              {isExpanded && (
                                <div className="px-6 pb-4 bg-gray-50">
                                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                                    {Object.entries(sizeBreakdown)
                                      .sort(([a], [b]) => {
                                        const numA = parseInt(a) || 0
                                        const numB = parseInt(b) || 0
                                        return numA - numB
                                      })
                                      .map(([size, data]) => (
                                        <div key={size} className="bg-white p-3 rounded border border-gray-200">
                                          <div className="text-xs text-gray-500 mb-1">Size {size}</div>
                                          <div className="text-sm font-semibold text-gray-900">{data.qty.toFixed(0)}</div>
                                          <div className="text-xs text-gray-600">{formatCurrency(data.value)}</div>
                                        </div>
                                      ))}
                                  </div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )
                        }
                      })

                      // Add regular products
                      regularProducts.forEach((item) => {
                        const product = item.product || {}
                        const totalValue = (item.current_quantity || 0) * (product.unit_cost || 0)
                        const isEditing = editingId === product.id
                        rows.push(
                          <tr key={item.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 text-sm font-medium text-gray-900">{product.name || 'Unknown'}</td>
                            <td className="px-6 py-4 text-sm text-gray-600">{product.sku || '-'}</td>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {isEditing ? (
                                <input
                                  type="number"
                                  step="0.01"
                                  value={editQuantity}
                                  onChange={(e) => setEditQuantity(parseFloat(e.target.value) || 0)}
                                  className="w-24 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                                  autoFocus
                                />
                              ) : (
                                <span className="font-semibold">{item.current_quantity.toFixed(0)}</span>
                              )}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">{formatCurrency(product.unit_cost || 0)}</td>
                            <td className="px-6 py-4 text-sm font-semibold text-gray-900">{formatCurrency(totalValue)}</td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {item.last_updated ? new Date(item.last_updated).toLocaleDateString() : '-'}
                            </td>
                            <td className="px-6 py-4 text-sm">
                              {isEditing ? (
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => handleUpdate(product.id)}
                                    className="text-green-600 hover:text-green-700 font-medium"
                                  >
                                    Save
                                  </button>
                                  <button
                                    onClick={() => {
                                      setEditingId(null)
                                      setEditQuantity(0)
                                    }}
                                    className="text-gray-600 hover:text-gray-700 font-medium"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => {
                                    setEditingId(product.id)
                                    setEditQuantity(item.current_quantity)
                                  }}
                                  className="text-blue-600 hover:text-blue-700 font-medium"
                                >
                                  Edit
                                </button>
                              )}
                            </td>
                          </tr>
                        )
                      })

                      return rows
                    })()}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}



