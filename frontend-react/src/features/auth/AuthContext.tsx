import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { getCurrentUser, loginUser, registerUser, type User } from '../../shared/api/auth'
import { setAuthToken, setOnUnauthorized } from '../../shared/api/client'

type AuthContextValue = {
  user: User | null
  token: string | null
  isLoading: boolean
  isInitializing: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isInitializing, setIsInitializing] = useState(true)

  const loadUser = useCallback(async (authToken: string) => {
    setAuthToken(authToken)
    const profile = await getCurrentUser()
    setUser(profile)
  }, [])

  useEffect(() => {
    if (!token) {
      setAuthToken(null)
      setUser(null)
      setIsInitializing(false)
      return
    }
    let cancelled = false
    setAuthToken(token)
    getCurrentUser()
      .then((profile) => {
        if (!cancelled) setUser(profile)
      })
      .catch(() => {
        if (!cancelled) {
          setToken(null)
          localStorage.removeItem('token')
          setUser(null)
        }
      })
      .finally(() => {
        if (!cancelled) setIsInitializing(false)
      })
    return () => {
      cancelled = true
    }
  }, [token])

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const data = await loginUser({ email, password })
      setToken(data.access_token)
      localStorage.setItem('token', data.access_token)
      await loadUser(data.access_token)
    } finally {
      setIsLoading(false)
    }
  }, [loadUser])

  const register = useCallback(
    async (email: string, password: string, fullName?: string) => {
      setIsLoading(true)
      try {
        await registerUser({ email, password, full_name: fullName })
        await login(email, password)
      } finally {
        setIsLoading(false)
      }
    },
    [login],
  )

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    setAuthToken(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const t = token ?? localStorage.getItem('token')
    if (t) await loadUser(t)
  }, [token, loadUser])

  useEffect(() => {
    setOnUnauthorized(logout)
    return () => setOnUnauthorized(null)
  }, [logout])

  const value = useMemo(
    () => ({ user, token, isLoading, isInitializing, login, register, logout, refreshUser }),
    [user, token, isLoading, isInitializing, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
