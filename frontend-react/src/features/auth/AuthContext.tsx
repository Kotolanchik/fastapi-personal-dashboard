import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { getCurrentUser, loginUser, registerUser, type User } from '../../shared/api/auth'
import { setAuthToken } from '../../shared/api/client'

type AuthContextValue = {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const loadUser = useCallback(async (authToken: string) => {
    setAuthToken(authToken)
    const profile = await getCurrentUser()
    setUser(profile)
  }, [])

  useEffect(() => {
    if (!token) {
      setAuthToken(null)
      setUser(null)
      return
    }
    loadUser(token).catch(() => {
      setToken(null)
      localStorage.removeItem('token')
      setUser(null)
    })
  }, [token, loadUser])

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

  const value = useMemo(
    () => ({ user, token, isLoading, login, register, logout }),
    [user, token, isLoading, login, register, logout],
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
