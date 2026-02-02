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

/** Download health report CSV for date range (e.g. for doctor). */
export async function downloadHealthReport(
  startDate?: string,
  endDate?: string,
): Promise<void> {
  const { data } = await api.get<Blob>('/export/health-report', {
    params: { start_date: startDate, end_date: endDate },
    responseType: 'blob',
  })
  const end = endDate || new Date().toISOString().slice(0, 10)
  const start = startDate || end
  const filename = `health_report_${start}_${end}.csv`
  const a = document.createElement('a')
  a.href = URL.createObjectURL(data)
  a.download = filename
  a.click()
  URL.revokeObjectURL(a.href)
}
