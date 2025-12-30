import React, { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token')
    if (token) {
      authAPI
        .getMe()
        .then((response) => {
          setUser(response.data)
          setIsAuthenticated(true)
        })
        .catch(() => {
          localStorage.removeItem('access_token')
          setIsAuthenticated(false)
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password })
      localStorage.setItem('access_token', response.data.access_token)
      const userResponse = await authAPI.getMe()
      setUser(userResponse.data)
      setIsAuthenticated(true)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }

  const register = async (email, password, fullName) => {
    try {
      await authAPI.register({ email, password, full_name: fullName })
      return await login(email, password)
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

