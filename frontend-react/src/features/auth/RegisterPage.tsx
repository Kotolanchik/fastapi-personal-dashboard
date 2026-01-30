import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from './AuthContext'

export const RegisterPage = () => {
  const { register, isLoading } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    try {
      await register(email, password, fullName)
      navigate('/')
    } catch (err) {
      setError('Не удалось создать аккаунт. Попробуйте позже.')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Регистрация</h1>
        <p className="muted">Создайте аккаунт для персонального трекинга.</p>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Имя
            <input
              type="text"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
            />
          </label>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            Пароль
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={8}
            />
          </label>
          {error ? <div className="error">{error}</div> : null}
          <button type="submit" disabled={isLoading}>
            Создать аккаунт
          </button>
        </form>
        <p className="muted">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}
