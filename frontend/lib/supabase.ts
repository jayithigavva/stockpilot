/**
 * Supabase client for StockPilot.
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key'

if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
  if (typeof window !== 'undefined') {
  console.warn('Supabase URL or Anon Key not set. Please set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY')
  }
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
})

// Auth API using Supabase
export const authAPI = {
  register: async (email: string, password: string, fullName: string, brandName: string) => {
    // Sign up user with Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
    })

    if (authError) throw authError
    if (!authData.user) throw new Error('User creation failed')

    // Create brand
    const { data: brandData, error: brandError } = await supabase
      .from('brands')
      .insert({
        name: brandName,
        slug: brandName.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
      })
      .select()
      .single()

    if (brandError) {
      // If brand exists, get it
      const { data: existingBrand } = await supabase
        .from('brands')
        .select()
        .eq('slug', brandName.toLowerCase().replace(/[^a-z0-9]+/g, '-'))
        .single()

      if (!existingBrand) throw brandError

      // Create user profile
      const { error: userError } = await supabase
        .from('users')
        .insert({
          id: authData.user.id,
          email,
          full_name: fullName,
          brand_id: existingBrand.id,
        })

      if (userError) throw userError
      return { access_token: authData.session?.access_token, token_type: 'bearer' }
    }

    // Create user profile
    const { error: userError } = await supabase
      .from('users')
      .insert({
        id: authData.user.id,
        email,
        full_name: fullName,
        brand_id: brandData.id,
      })

    if (userError) throw userError

    return { access_token: authData.session?.access_token, token_type: 'bearer' }
  },

  login: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (error) throw error
    if (!data.session) throw new Error('Login failed')

    return {
      access_token: data.session.access_token,
      token_type: 'bearer',
    }
  },

  logout: async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },

  getSession: async () => {
    const { data: { session } } = await supabase.auth.getSession()
    return session
  },

  getUser: async () => {
    const { data: { user } } = await supabase.auth.getUser()
    return user
  },
}

// Products API - See enhanced version below

// Decisions API using Supabase
export const decisionsAPI = {
  generate: async (productIds?: string[], availableCash?: number) => {
    const { data, error } = await supabase.functions.invoke('generate-decisions', {
      body: {
        product_ids: productIds,
        available_cash: availableCash,
      },
    })

    if (error) throw error
    return data
  },

  list: async (status?: string) => {
    let query = supabase
      .from('reorder_decisions')
      .select(`
        *,
        product:products(id, name, sku)
      `)
      .order('created_at', { ascending: false })

    if (status) {
      query = query.eq('status', status)
    }

    const { data, error } = await query

    if (error) throw error
    return data
  },

  accept: async (decisionId: string, notes?: string) => {
    const { data, error } = await supabase
      .from('reorder_decisions')
      .update({
        status: 'ACCEPTED',
        accepted_at: new Date().toISOString(),
      })
      .eq('id', decisionId)
      .select()
      .single()

    if (error) throw error

    // Log the action
    await supabase.from('decision_logs').insert({
      decision_id: decisionId,
      action: 'ACCEPTED',
      notes,
    })

    // Update inventory
    if (data) {
      const { data: inventory } = await supabase
        .from('inventory')
        .select('current_quantity')
        .eq('product_id', data.product_id)
        .single()

      if (inventory) {
        await supabase
          .from('inventory')
          .update({
            current_quantity: inventory.current_quantity + data.recommended_quantity,
            last_updated: new Date().toISOString(),
          })
          .eq('product_id', data.product_id)
      }
    }

    return data
  },

  reject: async (decisionId: string, notes?: string) => {
    const { data, error } = await supabase
      .from('reorder_decisions')
      .update({
        status: 'REJECTED',
      })
      .eq('id', decisionId)
      .select()
      .single()

    if (error) throw error

    // Log the action
    await supabase.from('decision_logs').insert({
      decision_id: decisionId,
      action: 'REJECTED',
      notes,
    })

    return data
  },
}

// Dashboard API using Supabase
export const dashboardAPI = {
  getStats: async () => {
    // Get product count
    const { count: productCount } = await supabase
      .from('products')
      .select('*', { count: 'exact', head: true })
      .eq('is_active', true)

    // Get pending decisions
    const { data: pendingDecisions } = await supabase
      .from('reorder_decisions')
      .select(`
        *,
        product:products(id, name, sku, unit_cost, selling_price)
      `)
      .eq('status', 'PENDING')
      .order('total_expected_loss', { ascending: false })

    // Get all inventory with products
    const { data: inventoryData } = await supabase
      .from('inventory')
      .select(`
        current_quantity,
        product:products(id, name, sku, unit_cost, selling_price, brand_id)
      `)

    // Calculate total inventory value
    const totalValue = inventoryData?.reduce((sum, inv) => {
      const cost = (inv.product as any)?.unit_cost || 0
      return sum + (inv.current_quantity * cost)
    }, 0) || 0

    // Calculate inventory at risk (high risk products)
    const { data: highRiskDecisions } = await supabase
      .from('reorder_decisions')
      .select(`
        cash_locked,
        product:products(unit_cost)
      `)
      .eq('status', 'PENDING')
      .eq('risk_category_before', 'HIGH')

    const inventoryAtRisk = highRiskDecisions?.reduce((sum, d) => {
      const cost = (d.product as any)?.unit_cost || 0
      return sum + (d.cash_locked || 0)
    }, 0) || 0

    // Count high risk SKUs
    const { count: highRiskCount } = await supabase
      .from('reorder_decisions')
      .select('*', { count: 'exact', head: true })
      .eq('status', 'PENDING')
      .eq('risk_category_before', 'HIGH')

    // Calculate average days of cover (simplified - would need sales history)
    // For now, return placeholder
    const avgDaysOfCover = 23 // TODO: Calculate from sales history

    // Calculate cash freed (sum of cash_freed from accepted decisions in current cycle)
    const { data: recentAccepted } = await supabase
      .from('reorder_decisions')
      .select('cash_freed')
      .eq('status', 'ACCEPTED')
      .gte('created_at', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())

    const cashFreed = recentAccepted?.reduce((sum, d) => sum + (parseFloat(d.cash_freed || 0)), 0) || 0

    // Get brand settings (available cash, plan info)
    const { data: { user } } = await supabase.auth.getUser()
    if (user) {
      const { data: userData } = await supabase
        .from('users')
        .select('brand_id')
        .eq('id', user.id)
        .single()

      if (userData) {
        const { data: brandData } = await supabase
          .from('brands')
          .select('available_cash, free_plan_started_at, plan_type')
          .eq('id', userData.brand_id)
          .single()

        const freePlanDaysRemaining = brandData?.plan_type === 'free' && brandData?.free_plan_started_at
          ? Math.max(0, 30 - Math.floor((Date.now() - new Date(brandData.free_plan_started_at).getTime()) / (1000 * 60 * 60 * 24)))
          : null

        return {
          total_products: productCount || 0,
          pending_decisions: pendingDecisions?.length || 0,
          total_inventory_value: totalValue,
          inventory_at_risk: inventoryAtRisk,
          high_risk_skus: highRiskCount || 0,
          avg_days_of_cover: avgDaysOfCover,
          cash_freed: cashFreed,
          pending_decisions_list: pendingDecisions || [],
          available_cash: brandData?.available_cash || 0,
          free_plan_days_remaining: freePlanDaysRemaining,
        }
      }
    }

    return {
      total_products: productCount || 0,
      pending_decisions: pendingDecisions?.length || 0,
      total_inventory_value: totalValue,
      inventory_at_risk: inventoryAtRisk,
      high_risk_skus: highRiskCount || 0,
      avg_days_of_cover: avgDaysOfCover,
      cash_freed: cashFreed,
      pending_decisions_list: pendingDecisions || [],
      available_cash: 0,
      free_plan_days_remaining: null,
    }
  },
}

// Settings API
export const settingsAPI = {
  getBrandSettings: async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('Not authenticated')

    const { data: userData } = await supabase
      .from('users')
      .select('brand_id')
      .eq('id', user.id)
      .single()

    if (!userData) throw new Error('User not found')

    const { data, error } = await supabase
      .from('brands')
      .select('available_cash, free_plan_started_at, plan_type, name')
      .eq('id', userData.brand_id)
      .single()

    if (error) throw error

    const freePlanDaysRemaining = data?.plan_type === 'free' && data?.free_plan_started_at
      ? Math.max(0, 30 - Math.floor((Date.now() - new Date(data.free_plan_started_at).getTime()) / (1000 * 60 * 60 * 24)))
      : null

    return {
      available_cash: data.available_cash || 0,
      plan_type: data.plan_type || 'free',
      free_plan_days_remaining: freePlanDaysRemaining,
      brand_name: data.name,
    }
  },

  updateAvailableCash: async (amount: number) => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) throw new Error('Not authenticated')

    const { data: userData } = await supabase
      .from('users')
      .select('brand_id')
      .eq('id', user.id)
      .single()

    if (!userData) throw new Error('User not found')

    const { error } = await supabase
      .from('brands')
      .update({ available_cash: amount })
      .eq('id', userData.brand_id)

    if (error) throw error
  },
}

// Suppliers API
export const suppliersAPI = {
  list: async () => {
    const { data, error } = await supabase
      .from('suppliers')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) throw error
    return data
  },

  create: async (supplier: any) => {
    const { data, error } = await supabase
      .from('suppliers')
      .insert({
        name: supplier.name,
        contact_email: supplier.contact_email,
        contact_phone: supplier.contact_phone,
        address: supplier.address,
      })
      .select()
      .single()

    if (error) throw error
    return data
  },

  update: async (id: string, supplier: any) => {
    const { data, error } = await supabase
      .from('suppliers')
      .update({
        name: supplier.name,
        contact_email: supplier.contact_email,
        contact_phone: supplier.contact_phone,
        address: supplier.address,
      })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  delete: async (id: string) => {
    const { error } = await supabase
      .from('suppliers')
      .delete()
      .eq('id', id)

    if (error) throw error
  },
}

// Inventory API
export const inventoryAPI = {
  list: async () => {
    const { data, error } = await supabase
      .from('inventory')
      .select(`
        *,
        product:products(id, name, sku, unit_cost, selling_price)
      `)
      .order('last_updated', { ascending: false })

    if (error) throw error
    return data
  },

  update: async (productId: string, quantity: number) => {
    const { data, error } = await supabase
      .from('inventory')
      .update({
        current_quantity: quantity,
        last_updated: new Date().toISOString(),
      })
      .eq('product_id', productId)
      .select()
      .single()

    if (error) {
      // If inventory doesn't exist, create it
      if (error.code === 'PGRST116') {
        const { data: newData, error: createError } = await supabase
          .from('inventory')
          .insert({
            product_id: productId,
            current_quantity: quantity,
          })
          .select()
          .single()

        if (createError) throw createError
        return newData
      }
      throw error
    }
    return data
  },
}

// Enhanced Products API with bulk operations
export const productsAPI = {
  list: async () => {
    const { data, error } = await supabase
      .from('products')
      .select(`
        *,
        inventory:inventory(current_quantity),
        supplier:suppliers(name)
      `)
      .eq('is_active', true)
      .order('created_at', { ascending: false })

    if (error) throw error

    return data.map((product: any) => ({
      id: product.id,
      sku: product.sku,
      name: product.name,
      description: product.description,
      unit_cost: product.unit_cost,
      selling_price: product.selling_price,
      lead_time_days: product.lead_time_days,
      min_order_quantity: product.min_order_quantity,
      order_multiple: product.order_multiple,
      supplier_id: product.supplier_id,
      supplier_name: product.supplier?.name,
      current_inventory: product.inventory?.[0]?.current_quantity || 0,
    }))
  },

  get: async (id: string) => {
    const { data, error } = await supabase
      .from('products')
      .select(`
        *,
        inventory:inventory(current_quantity),
        supplier:suppliers(name)
      `)
      .eq('id', id)
      .single()

    if (error) throw error

    return {
      id: data.id,
      sku: data.sku,
      name: data.name,
      description: data.description,
      unit_cost: data.unit_cost,
      selling_price: data.selling_price,
      lead_time_days: data.lead_time_days,
      min_order_quantity: data.min_order_quantity,
      order_multiple: data.order_multiple,
      supplier_id: data.supplier_id,
      supplier_name: data.supplier?.name,
      current_inventory: data.inventory?.[0]?.current_quantity || 0,
    }
  },

  create: async (product: any) => {
    const { data: productData, error: productError } = await supabase
      .from('products')
      .insert({
        sku: product.sku,
        name: product.name,
        description: product.description,
        unit_cost: product.unit_cost,
        selling_price: product.selling_price,
        lead_time_days: product.lead_time_days,
        min_order_quantity: product.min_order_quantity || 0,
        order_multiple: product.order_multiple || 1.0,
        supplier_id: product.supplier_id || null,
      })
      .select()
      .single()

    if (productError) throw productError

    // Create inventory record
    const { error: inventoryError } = await supabase
      .from('inventory')
      .insert({
        product_id: productData.id,
        current_quantity: product.initial_quantity || 0.0,
      })

    if (inventoryError) throw inventoryError

    return {
      id: productData.id,
      sku: productData.sku,
      name: productData.name,
      unit_cost: productData.unit_cost,
      selling_price: productData.selling_price,
      lead_time_days: productData.lead_time_days,
      current_inventory: product.initial_quantity || 0.0,
    }
  },

  bulkCreate: async (products: any[]) => {
    const results = []
    for (const product of products) {
      try {
        const created = await productsAPI.create(product)
        results.push({ success: true, data: created })
      } catch (error: any) {
        results.push({ success: false, error: error.message, sku: product.sku })
      }
    }
    return results
  },

  update: async (id: string, product: any) => {
    const { data, error } = await supabase
      .from('products')
      .update({
        sku: product.sku,
        name: product.name,
        description: product.description,
        unit_cost: product.unit_cost,
        selling_price: product.selling_price,
        lead_time_days: product.lead_time_days,
        min_order_quantity: product.min_order_quantity,
        order_multiple: product.order_multiple,
        supplier_id: product.supplier_id,
      })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error
    return data
  },

  delete: async (id: string) => {
    const { error } = await supabase
      .from('products')
      .update({ is_active: false })
      .eq('id', id)

    if (error) throw error
  },
}

// Enhanced Sales History API
export const salesHistoryAPI = {
  list: async (productId?: string) => {
    let query = supabase
      .from('sales_history')
      .select(`
        *,
        product:products(id, name, sku)
      `)
      .order('date', { ascending: false })

    if (productId) {
      query = query.eq('product_id', productId)
    }

    const { data, error } = await query
    if (error) throw error
    return data
  },

  create: async (salesData: any) => {
    const { data, error } = await supabase
      .from('sales_history')
      .insert({
        product_id: salesData.product_id,
        date: salesData.date,
        demand: salesData.demand,
        revenue: salesData.revenue,
      })
      .select()
      .single()

    if (error) throw error
    return data
  },

  bulkCreate: async (salesDataArray: any[]) => {
    const { data, error } = await supabase
      .from('sales_history')
      .insert(salesDataArray)
      .select()

    if (error) throw error
    return data
  },

  uploadCSV: async (file: File, productId: string) => {
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase())

    const salesData = lines.slice(1).map(line => {
      const values = line.split(',')
      const row: any = { product_id: productId }
      
      headers.forEach((header, index) => {
        const value = values[index]?.trim()
        if (header.includes('date')) {
          row.date = value || new Date().toISOString()
        } else if (header.includes('demand') || header.includes('quantity') || header.includes('qty')) {
          row.demand = parseFloat(value) || 0
        } else if (header.includes('revenue') || header.includes('sales')) {
          row.revenue = value ? parseFloat(value) : null
        }
      })

      return row
    })

    return await salesHistoryAPI.bulkCreate(salesData)
  },
}

// Data API using Supabase
export const dataAPI = {
  uploadSales: async (data: any[]) => {
    const { data: inserted, error } = await supabase
      .from('sales_history')
      .insert(data)
      .select()

    if (error) throw error
    return inserted
  },

  uploadSalesCSV: async (file: File, productId: string) => {
    // Parse CSV and upload
    const text = await file.text()
    const lines = text.split('\n').filter(line => line.trim())
    const headers = lines[0].split(',').map(h => h.trim())

    const salesData = lines.slice(1).map(line => {
      const values = line.split(',')
      return {
        product_id: productId,
        date: values[0] || new Date().toISOString(),
        demand: parseFloat(values[1]) || 0,
        revenue: values[2] ? parseFloat(values[2]) : null,
      }
    })

    return await dataAPI.uploadSales(salesData)
  },
}

