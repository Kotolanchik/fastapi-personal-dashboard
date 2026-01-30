import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from './AuthContext'

export const RequireAuth = () => {
  const { token, isInitializing } = useAuth()
  if (!token) {
    return <Navigate to="/login" replace />
  }
  if (isInitializing) {
    return (
      <div className="auth-loading" aria-busy="true">
        <div className="auth-loading-spinner" aria-hidden />
        <p>Loading…</p>
      </div>
    )
  }
  return <Outlet />
}
