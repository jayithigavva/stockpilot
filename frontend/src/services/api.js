/**
 * API service for communicating with backend
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
}

// Products endpoints
export const productsAPI = {
  list: () => api.get('/api/products'),
  get: (id) => api.get(`/api/products/${id}`),
  create: (data) => api.post('/api/products', data),
  update: (id, data) => api.put(`/api/products/${id}`, data),
}

// Inventory endpoints
export const inventoryAPI = {
  list: () => api.get('/api/inventory'),
  get: (productId) => api.get(`/api/inventory/${productId}`),
  update: (productId, data) => api.put(`/api/inventory/${productId}`, data),
}

// Sales endpoints
export const salesAPI = {
  upload: (data) => api.post('/api/sales/upload', data),
  getHistory: (productId) => api.get(`/api/sales/${productId}`),
}

// Decisions endpoints
export const decisionsAPI = {
  runAI: (data) => api.post('/api/ai/run', data),
  list: (status) => api.get('/api/decisions', { params: { status_filter: status } }),
  get: (id) => api.get(`/api/decisions/${id}`),
  accept: (id, data) => api.post(`/api/decisions/${id}/accept`, data),
  reject: (id, data) => api.post(`/api/decisions/${id}/reject`, data),
}

// Dashboard endpoint
export const dashboardAPI = {
  getSummary: () => api.get('/api/dashboard'),
}

export default api

