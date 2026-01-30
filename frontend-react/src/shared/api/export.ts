import api from './client'

const EXPORT_CATEGORIES = ['daily', 'all', 'health', 'finance', 'productivity', 'learning'] as const
export type ExportCategory = (typeof EXPORT_CATEGORIES)[number]

/** Download CSV (triggers browser download). */
export async function downloadCsv(category: ExportCategory = 'daily'): Promise<void> {
  const { data } = await api.get<Blob>('/export', {
    params: { category },
    responseType: 'blob',
  })
  const filename = `${category}.csv`
  const a = document.createElement('a')
  a.href = URL.createObjectURL(data)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}
