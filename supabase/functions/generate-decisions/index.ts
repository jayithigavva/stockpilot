// Supabase Edge Function: Generate AI Reorder Decisions
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Create Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    // Get authenticated user
    const {
      data: { user },
    } = await supabaseClient.auth.getUser()

    if (!user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get user's brand_id
    const { data: userData, error: userError } = await supabaseClient
      .from('users')
      .select('brand_id')
      .eq('id', user.id)
      .single()

    if (userError || !userData) {
      return new Response(
        JSON.stringify({ error: 'User not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const brandId = userData.brand_id

    // Parse request body
    const { product_ids, available_cash } = await req.json()

    // Get products
    let productsQuery = supabaseClient
      .from('products')
      .select('*')
      .eq('brand_id', brandId)
      .eq('is_active', true)

    if (product_ids && product_ids.length > 0) {
      productsQuery = productsQuery.in('id', product_ids)
    }

    const { data: products, error: productsError } = await productsQuery

    if (productsError || !products || products.length === 0) {
      return new Response(
        JSON.stringify({ error: 'No products found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get inventory and sales history for each product
    const recommendations = []

    for (const product of products) {
      // Get inventory
      const { data: inventory } = await supabaseClient
        .from('inventory')
        .select('current_quantity')
        .eq('product_id', product.id)
        .single()

      if (!inventory) continue

      // Get sales history (last 365 days)
      const { data: salesHistory } = await supabaseClient
        .from('sales_history')
        .select('date, demand')
        .eq('product_id', product.id)
        .order('date', { ascending: true })
        .limit(365)

      if (!salesHistory || salesHistory.length < 30) continue // Need at least 30 days of data

      // Simple recommendation logic (replace with actual AI model)
      const avgDailyDemand = salesHistory.reduce((sum, s) => sum + parseFloat(s.demand), 0) / salesHistory.length
      const leadTimeDays = product.lead_time_days || 14
      const safetyStock = avgDailyDemand * leadTimeDays * 1.5 // 1.5x safety factor
      const recommendedQuantity = Math.max(0, safetyStock - inventory.current_quantity)

      if (recommendedQuantity <= 0) continue

      // Calculate costs (simplified)
      const unitCost = parseFloat(product.unit_cost)
      const cashLocked = recommendedQuantity * unitCost

      // Check cash constraint
      if (available_cash && cashLocked > available_cash) {
        continue // Skip if exceeds available cash
      }

      // Create recommendation
      recommendations.push({
        product_id: product.id,
        product_name: product.name,
        sku: product.sku,
        current_inventory: inventory.current_quantity,
        recommended_quantity: recommendedQuantity,
        stockout_probability_before: 0.3, // Placeholder
        stockout_probability_after: 0.1, // Placeholder
        risk_category_before: 'MEDIUM',
        risk_category_after: 'LOW',
        expected_overstock_cost: recommendedQuantity * unitCost * 0.1,
        expected_understock_cost: avgDailyDemand * parseFloat(product.selling_price) * 0.2,
        total_expected_loss: 0,
        cash_locked: cashLocked,
        cash_freed: 0,
      })
    }

    // Save decisions to database
    const decisionsToInsert = recommendations.map(rec => ({
      brand_id: brandId,
      product_id: rec.product_id,
      recommended_quantity: rec.recommended_quantity,
      current_inventory: rec.current_inventory,
      stockout_probability_before: rec.stockout_probability_before,
      stockout_probability_after: rec.stockout_probability_after,
      risk_category_before: rec.risk_category_before,
      risk_category_after: rec.risk_category_after,
      expected_overstock_cost: rec.expected_overstock_cost,
      expected_understock_cost: rec.expected_understock_cost,
      total_expected_loss: rec.total_expected_loss,
      cash_locked: rec.cash_locked,
      cash_freed: rec.cash_freed,
      status: 'PENDING',
      created_by_user_id: user.id,
    }))

    const { data: insertedDecisions, error: insertError } = await supabaseClient
      .from('reorder_decisions')
      .insert(decisionsToInsert)
      .select()

    if (insertError) {
      console.error('Error inserting decisions:', insertError)
    }

    return new Response(
      JSON.stringify({ recommendations, decisions: insertedDecisions || [] }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

