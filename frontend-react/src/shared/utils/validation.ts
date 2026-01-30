import axios from 'axios'

/** FastAPI 422 detail item: { loc: string[], msg: string, type: string } */
export function parseValidationErrors(err: unknown): Record<string, string> {
  const out: Record<string, string> = {}
  if (!axios.isAxiosError(err) || err.response?.status !== 422) return out
  const detail = err.response?.data?.detail
  if (!Array.isArray(detail)) return out
  for (const item of detail) {
    const loc = item?.loc
    const msg = item?.msg ?? ''
    if (Array.isArray(loc) && loc.length) {
      const field = loc[loc.length - 1] as string
      if (typeof field === 'string' && field) out[field] = msg
    }
  }
  return out
}

/** Single message from 422 or other API error */
export function getErrorMessage(err: unknown): string {
  if (!axios.isAxiosError(err)) return err instanceof Error ? err.message : 'Request failed'
  const detail = err.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]) return detail[0].msg ?? String(detail[0])
  if (detail && typeof detail === 'object' && 'msg' in detail) return String((detail as { msg: unknown }).msg)
  return err.response?.data?.message ?? err.message ?? 'Request failed'
}
