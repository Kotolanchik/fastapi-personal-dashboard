import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { getErrorMessage, parseValidationErrors } from '../../shared/utils/validation'
import { useAuth } from './AuthContext'

export const LoginPage = () => {
  const { login, isLoading, token } = useAuth()
  const navigate = useNavigate()
  useEffect(() => {
    if (token) navigate('/dashboard', { replace: true })
  }, [token, navigate])
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFieldErrors({})
    setGeneralError(null)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      const errors = parseValidationErrors(err)
      if (Object.keys(errors).length) {
        setFieldErrors(errors)
      } else {
        setGeneralError(getErrorMessage(err) || 'Login failed. Check your email and password.')
      }
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Sign in</h1>
        <p className="muted">Use your credentials to sign in.</p>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setFieldErrors((prev) => ({ ...prev, email: '' }))
              }}
              required
              aria-invalid={!!fieldErrors.email}
            />
            {fieldErrors.email ? <div className="field-error">{fieldErrors.email}</div> : null}
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setFieldErrors((prev) => ({ ...prev, password: '' }))
              }}
              required
              aria-invalid={!!fieldErrors.password}
            />
            {fieldErrors.password ? <div className="field-error">{fieldErrors.password}</div> : null}
          </label>
          {generalError ? <div className="error">{generalError}</div> : null}
          <button type="submit" disabled={isLoading}>
            Sign in
          </button>
        </form>
        <p className="muted">
          Don&apos;t have an account? <Link to="/register">Sign up</Link>
        </p>
      </div>
    </div>
  )
}
