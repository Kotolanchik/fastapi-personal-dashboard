import type { FormEvent } from 'react'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'

import { getErrorMessage, parseValidationErrors } from '../../shared/utils/validation'
import { useAuth } from './AuthContext'

export const RegisterPage = () => {
  const { t } = useTranslation()
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
        setGeneralError(getErrorMessage(err) || t('auth.registerFailed'))
      }
    }
  }

  const clearFieldError = (field: string) => () =>
    setFieldErrors((prev) => ({ ...prev, [field]: '' }))

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{t('auth.signUp')}</h1>
        <p className="muted">{t('auth.signUpSubtitle')}</p>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            {t('common.name')}
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
            {t('common.email')}
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
            {t('common.password')}
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
            {t('auth.createAccount')}
          </button>
        </form>
        <p className="muted">
          {t('auth.hasAccount')} <Link to="/login">{t('auth.signIn')}</Link>
        </p>
      </div>
    </div>
  )
}
