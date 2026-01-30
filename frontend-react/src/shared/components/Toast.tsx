import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'

type ToastItem = { id: number; message: string; type: 'success' | 'error' }

type ToastContextValue = {
  success: (message: string) => void
  error: (message: string) => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

let id = 0
const AUTO_HIDE_MS = 4000

export const ToastProvider = ({ children }: { children: React.ReactNode }) => {
  const [toasts, setToasts] = useState<ToastItem[]>([])

  const remove = useCallback((toastId: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== toastId))
  }, [])

  const add = useCallback((message: string, type: 'success' | 'error') => {
    const toastId = ++id
    setToasts((prev) => [...prev, { id: toastId, message, type }])
    setTimeout(() => remove(toastId), AUTO_HIDE_MS)
  }, [remove])

  const success = useCallback((message: string) => add(message, 'success'), [add])
  const error = useCallback((message: string) => add(message, 'error'), [add])

  const value = useMemo(() => ({ success, error }), [success, error])

  const container = (
    <div className="toast-container" role="region" aria-label="Notifications">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`toast toast-${t.type}`}
          role="alert"
          onAnimationEnd={() => {}}
        >
          {t.message}
        </div>
      ))}
    </div>
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      {typeof document !== 'undefined' && createPortal(container, document.body)}
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
