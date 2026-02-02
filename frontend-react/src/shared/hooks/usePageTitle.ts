import { useEffect } from 'react'

const DEFAULT_TITLE = 'LifePulse'

export function usePageTitle(title: string | null) {
  useEffect(() => {
    const previous = document.title
    document.title = title ? `${title} · ${DEFAULT_TITLE}` : DEFAULT_TITLE
    return () => {
      document.title = previous
    }
  }, [title])
}
