import { useCallback, useEffect, useState } from 'react'

import { API_ERROR_EVENT } from '../api/client'

export const ApiErrorBanner = () => {
  const [message, setMessage] = useState<string | null>(null)

  const handleEvent = useCallback((e: Event) => {
    const detail = (e as CustomEvent<{ message?: string; clearSession?: boolean }>).detail
    if (detail?.message) setMessage(detail.message)
  }, [])

  useEffect(() => {
    window.addEventListener(API_ERROR_EVENT, handleEvent)
    return () => window.removeEventListener(API_ERROR_EVENT, handleEvent)
  }, [handleEvent])

  const dismiss = useCallback(() => setMessage(null), [])

  if (!message) return null

  return (
    <div className="api-error-banner" role="alert">
      <span>{message}</span>
      <button type="button" className="api-error-dismiss" onClick={dismiss} aria-label="Dismiss">
        ×
      </button>
    </div>
  )
}
