import { FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { getErrorMessage, parseValidationErrors } from '../../shared/utils/validation'
import { useAuth } from './AuthContext'

export const RegisterPage = () => {
  const { register, isLoading, token } = useAuth()
  const navigate = useNavigate()
  useEffect(() => {
    if (token) navigate('/dashboard', { replace: true })
  }, [token, navigate])
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFieldErrors({})
    setGeneralError(null)
    try {
      await register(email, password, fullName)
      navigate('/dashboard')
    } catch (err) {
      const errors = parseValidationErrors(err)
      if (Object.keys(errors).length) {
        setFieldErrors(errors)
      } else {
        setGeneralError(getErrorMessage(err) || 'Could not create account. Please try again.')
      }
    }
  }

  const clearFieldError = (field: string) => () =>
    setFieldErrors((prev) => ({ ...prev, [field]: undefined }))

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Sign up</h1>
        <p className="muted">Create an account for personal tracking.</p>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Name
            <input
              type="text"
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value)
                clearFieldError('full_name')()
              }}
              aria-invalid={!!fieldErrors.full_name}
            />
            {fieldErrors.full_name ? <div className="field-error">{fieldErrors.full_name}</div> : null}
          </label>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                clearFieldError('email')()
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
                clearFieldError('password')()
              }}
              required
              minLength={8}
              aria-invalid={!!fieldErrors.password}
            />
            {fieldErrors.password ? <div className="field-error">{fieldErrors.password}</div> : null}
          </label>
          {generalError ? <div className="error">{generalError}</div> : null}
          <button type="submit" disabled={isLoading}>
            Create account
          </button>
        </form>
        <p className="muted">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
