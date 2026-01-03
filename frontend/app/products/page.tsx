'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { productsAPI, suppliersAPI, stylesAPI } from '@/lib/supabase'
import { supabase } from '@/lib/supabase'
import Sidebar from '../components/Sidebar'

interface Product {
  id?: string
  sku: string
  name: string
  description: string
  unit_cost: number
  selling_price: number
  lead_time_days: number
  min_order_quantity: number
  order_multiple: number
  supplier_id: string
  initial_quantity: number
  // Footwear fields
  style_id?: string
  size?: string
  color?: string
  width?: string
  is_footwear?: boolean
}

export default function ProductsPage() {
  const router = useRouter()
  const [products, setProducts] = useState<any[]>([])
  const [suppliers, setSuppliers] = useState<any[]>([])
  const [styles, setStyles] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [importMode, setImportMode] = useState<'manual' | 'csv'>('manual')
  const [formData, setFormData] = useState<Product>({
    sku: '',
    name: '',
    description: '',
    unit_cost: 0,
    selling_price: 0,
    lead_time_days: 14,
    min_order_quantity: 0,
    order_multiple: 1,
    supplier_id: '',
    initial_quantity: 0,
    is_footwear: false,
    style_id: '',
    size: '',
    color: '',
    width: '',
  })
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvData, setCsvData] = useState<any[]>([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }
      loadData()
    }
    checkAuth()
  }, [router])

  const loadData = async () => {
    try {
      const [productsData, suppliersData, stylesData] = await Promise.all([
        productsAPI.list(),
        suppliersAPI.list(),
        stylesAPI.list().catch(() => []), // Styles might not exist yet
      ])
      setProducts(productsData)
      setSuppliers(suppliersData)
      setStyles(stylesData || [])
    } catch (err: any) {
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      const productData: any = {
        sku: formData.sku,
        name: formData.name,
        description: formData.description,
        unit_cost: formData.unit_cost,
        selling_price: formData.selling_price,
        lead_time_days: formData.lead_time_days,
        min_order_quantity: formData.min_order_quantity,
        order_multiple: formData.order_multiple,
        supplier_id: formData.supplier_id || null,
        initial_quantity: formData.initial_quantity,
      }

      // Add footwear fields if it's a footwear product
      if (formData.is_footwear && formData.style_id) {
        productData.style_id = formData.style_id
        productData.size = formData.size || null
        productData.color = formData.color || null
        productData.width = formData.width || null
      }

      await productsAPI.create(productData)
      setSuccess('Product added successfully!')
      setFormData({
        sku: '',
        name: '',
        description: '',
        unit_cost: 0,
        selling_price: 0,
        lead_time_days: 14,
        min_order_quantity: 0,
        order_multiple: 1,
        supplier_id: '',
        initial_quantity: 0,
        is_footwear: false,
        style_id: '',
        size: '',
        color: '',
        width: '',
      })
      await loadData()
    } catch (err: any) {
      setError(err.message || 'Failed to add product')
    }
  }

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setCsvFile(file)
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase())

    const parsed = lines.slice(1).map(line => {
      const values = line.split(',')
      const row: any = {}
      headers.forEach((header, index) => {
        const value = values[index]?.trim()
        if (header.includes('sku')) row.sku = value
        else if (header.includes('name') || header.includes('product')) row.name = value
        else if (header.includes('description')) row.description = value
        else if (header.includes('cost') || header.includes('unit_cost')) row.unit_cost = parseFloat(value) || 0
        else if (header.includes('price') || header.includes('selling')) row.selling_price = parseFloat(value) || 0
        else if (header.includes('lead') || header.includes('lead_time')) row.lead_time_days = parseInt(value) || 14
        else if (header.includes('min') || header.includes('minimum')) row.min_order_quantity = parseFloat(value) || 0
        else if (header.includes('multiple') || header.includes('order_multiple')) row.order_multiple = parseFloat(value) || 1
        else if (header.includes('quantity') || header.includes('qty') || header.includes('initial')) row.initial_quantity = parseFloat(value) || 0
      })
      return row
    })

    setCsvData(parsed.filter(row => row.sku && row.name))
  }

  const handleBulkImport = async () => {
    setError('')
    setSuccess('')

    try {
      const results = await productsAPI.bulkCreate(csvData)
      const successCount = results.filter((r: any) => r.success).length
      setSuccess(`Imported ${successCount} of ${csvData.length} products successfully!`)
      setCsvData([])
      setCsvFile(null)
      await loadData()
    } catch (err: any) {
      setError(err.message || 'Failed to import products')
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
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-semibold text-gray-900">Products</h1>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowAddForm(!showAddForm)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium"
                >
                  {showAddForm ? 'Cancel' : '+ Add Product'}
                </button>
              </div>
            </div>
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

            {showAddForm && (
              <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                <div className="flex items-center gap-4 mb-6">
                  <button
                    onClick={() => setImportMode('manual')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                      importMode === 'manual'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Manual Entry
                  </button>
                  <button
                    onClick={() => setImportMode('csv')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                      importMode === 'csv'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Import CSV/Excel
                  </button>
                </div>

                {importMode === 'manual' ? (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="mb-4">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={formData.is_footwear}
                          onChange={(e) => setFormData({ ...formData, is_footwear: e.target.checked, style_id: e.target.checked ? formData.style_id : '' })}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm font-medium text-gray-700">This is a footwear product</span>
                      </label>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">SKU *</label>
                        <input
                          type="text"
                          value={formData.sku}
                          onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                          required
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Product Name *</label>
                        <input
                          type="text"
                          value={formData.name}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          required
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    {formData.is_footwear && (
                      <div className="grid grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Style *</label>
                          <select
                            value={formData.style_id}
                            onChange={(e) => setFormData({ ...formData, style_id: e.target.value })}
                            required={formData.is_footwear}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">Select style</option>
                            {styles.map((s) => (
                              <option key={s.id} value={s.id}>{s.name} ({s.style_code})</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Size</label>
                          <select
                            value={formData.size}
                            onChange={(e) => setFormData({ ...formData, size: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">Select size</option>
                            {['6', '7', '8', '9', '10', '11', '12'].map((size) => (
                              <option key={size} value={size}>Size {size}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
                          <input
                            type="text"
                            value={formData.color}
                            onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                            placeholder="e.g., Black, White, Red"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Width</label>
                          <select
                            value={formData.width}
                            onChange={(e) => setFormData({ ...formData, width: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">Select width</option>
                            <option value="N">Narrow (N)</option>
                            <option value="M">Medium (M)</option>
                            <option value="W">Wide (W)</option>
                          </select>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        rows={2}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Unit Cost (₹) *</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.unit_cost}
                          onChange={(e) => setFormData({ ...formData, unit_cost: parseFloat(e.target.value) || 0 })}
                          required
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Selling Price (₹) *</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.selling_price}
                          onChange={(e) => setFormData({ ...formData, selling_price: parseFloat(e.target.value) || 0 })}
                          required
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Lead Time (days)</label>
                        <input
                          type="number"
                          value={formData.lead_time_days}
                          onChange={(e) => setFormData({ ...formData, lead_time_days: parseInt(e.target.value) || 14 })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Min Order Qty</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.min_order_quantity}
                          onChange={(e) => setFormData({ ...formData, min_order_quantity: parseFloat(e.target.value) || 0 })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Order Multiple</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.order_multiple}
                          onChange={(e) => setFormData({ ...formData, order_multiple: parseFloat(e.target.value) || 1 })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Supplier</label>
                        <select
                          value={formData.supplier_id}
                          onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="">Select supplier</option>
                          {suppliers.map((s) => (
                            <option key={s.id} value={s.id}>{s.name}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Initial Quantity</label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.initial_quantity}
                          onChange={(e) => setFormData({ ...formData, initial_quantity: parseFloat(e.target.value) || 0 })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
                    >
                      Add Product
                    </button>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Upload CSV/Excel File</label>
                      <input
                        type="file"
                        accept=".csv,.xlsx,.xls"
                        onChange={handleCSVUpload}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <p className="mt-2 text-xs text-gray-500">
                        CSV should have columns: SKU, Name, Description, Unit Cost, Selling Price, Lead Time, Min Order Qty, Order Multiple, Initial Quantity
                      </p>
                    </div>

                    {csvData.length > 0 && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-sm font-medium text-gray-700">
                            Preview ({csvData.length} products)
                          </p>
                          <button
                            onClick={handleBulkImport}
                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium"
                          >
                            Import All
                          </button>
                        </div>
                        <div className="border border-gray-200 rounded-lg overflow-x-auto">
                          <table className="w-full text-sm">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left">SKU</th>
                                <th className="px-4 py-2 text-left">Name</th>
                                <th className="px-4 py-2 text-left">Cost</th>
                                <th className="px-4 py-2 text-left">Price</th>
                              </tr>
                            </thead>
                            <tbody>
                              {csvData.slice(0, 10).map((row, idx) => (
                                <tr key={idx} className="border-t">
                                  <td className="px-4 py-2">{row.sku}</td>
                                  <td className="px-4 py-2">{row.name}</td>
                                  <td className="px-4 py-2">{formatCurrency(row.unit_cost || 0)}</td>
                                  <td className="px-4 py-2">{formatCurrency(row.selling_price || 0)}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Products List */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">All Products ({products.length})</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Style/Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cost</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stock</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lead Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {products.map((product) => (
                      <tr key={product.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{product.sku}</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{product.name}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {product.style_id ? (
                            <div className="flex flex-col">
                              <span className="font-medium">{product.style?.name || 'Style'}</span>
                              {product.size && (
                                <span className="text-xs text-gray-500">
                                  Size {product.size}
                                  {product.color && ` • ${product.color}`}
                                  {product.width && ` • ${product.width === 'N' ? 'Narrow' : product.width === 'W' ? 'Wide' : 'Medium'}`}
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-gray-400">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">{formatCurrency(product.unit_cost)}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{formatCurrency(product.selling_price)}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{product.current_inventory?.toFixed(0) || '0'}</td>
                        <td className="px-6 py-4 text-sm text-gray-600">{product.lead_time_days} days</td>
                      </tr>
                    ))}
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






