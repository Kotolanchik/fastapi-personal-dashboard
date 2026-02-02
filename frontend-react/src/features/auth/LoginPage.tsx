import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'

import { getErrorMessage, parseValidationErrors } from '../../shared/utils/validation'
import { useAuth } from './AuthContext'

export const LoginPage = () => {
  const { t } = useTranslation()
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
        setGeneralError(getErrorMessage(err) || t('auth.loginFailed'))
      }
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{t('auth.signIn')}</h1>
        <p className="muted">{t('auth.signInSubtitle')}</p>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            {t('common.email')}
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
            {t('common.password')}
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
            {t('auth.signIn')}
          </button>
        </form>
        <p className="muted">
          {t('auth.noAccount')} <Link to="/register">{t('auth.signUp')}</Link>
        </p>
      </div>
    </div>
  )
}
