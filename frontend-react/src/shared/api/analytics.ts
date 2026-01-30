import api from './client'

export type CorrelationItem = {
  metric_a: string
  metric_b: string
  correlation: number
  sample_size: number
}

export type InsightItem = {
  message: string
  severity: string
}

export const getCorrelations = () =>
  api.get<{ correlations: CorrelationItem[] }>('/analytics/correlations').then((res) => res.data)

export const getInsights = () =>
  api.get<{ generated_at: string; insights: InsightItem[] }>('/analytics/insights').then((res) => res.data)

export const getRecommendations = () =>
  api
    .get<{ generated_at: string; recommendations: InsightItem[] }>(
      '/analytics/recommendations',
    )
    .then((res) => res.data)

export type WeeklyReport = {
  period_start: string
  period_end: string
  summary: Record<
    string,
    Record<string, number | string | null | undefined>
  >
  insight: string | null
  generated_at: string
}

export const getWeeklyReport = () =>
  api
    .get<WeeklyReport>('/analytics/weekly-report')
    .then((res) => res.data)
