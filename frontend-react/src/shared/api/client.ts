import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 10000,
})

export const setAuthToken = (token?: string | null) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export const API_ERROR_EVENT = 'api-error'

let onUnauthorized: (() => void) | null = null
export const setOnUnauthorized = (cb: (() => void) | null) => {
  onUnauthorized = cb
}

function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      const first = detail[0]
      return first?.msg ?? first?.loc?.join('. ') ?? err.message
    }
    if (detail && typeof detail === 'object' && 'msg' in detail) return String((detail as { msg: unknown }).msg)
    return err.response?.data?.message ?? err.message ?? 'Request failed'
  }
  return err instanceof Error ? err.message : 'Request failed'
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common.Authorization
      onUnauthorized?.()
      window.dispatchEvent(new CustomEvent(API_ERROR_EVENT, { detail: { clearSession: true } }))
      const loginPath = '/login'
      if (window.location.pathname !== loginPath) {
        window.location.href = loginPath
      }
      return Promise.reject(error)
    }
    // 422 validation errors are handled by forms (field-level messages)
    if (error.response?.status !== 422) {
      const message = getErrorMessage(error)
      window.dispatchEvent(new CustomEvent(API_ERROR_EVENT, { detail: { message } }))
    }
    return Promise.reject(error)
  },
)

export default api
