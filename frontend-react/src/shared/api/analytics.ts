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

export type TrendThisMonthItem = {
  metric: string
  label: string
  value: number
  direction: 'up' | 'down' | 'neutral'
}

export const getTrendThisMonth = () =>
  api
    .get<{ metrics: TrendThisMonthItem[] }>('/analytics/trend-this-month')
    .then((res) => res.data)

export type InsightOfTheWeekResponse = { insight: string | null }

export const getInsightOfTheWeek = () =>
  api
    .get<InsightOfTheWeekResponse>('/analytics/insight-of-the-week')
    .then((res) => res.data)

export type BestWorstWeekdayItem = {
  metric: string
  best_weekday: string
  worst_weekday: string
  best_value: number
  worst_value: number
}

export type LinearTrendItem = {
  metric: string
  slope: number
  direction: string
  days: number
}

export type WeekdayTrendsResponse = {
  best_worst_weekday: BestWorstWeekdayItem[]
  trends_14: LinearTrendItem[]
  trends_30: LinearTrendItem[]
}

export const getWeekdayTrends = () =>
  api
    .get<WeekdayTrendsResponse>('/analytics/weekday-trends')
    .then((res) => res.data)

export type FocusByCategoryItem = {
  category: string
  hours: number
}

export type ProductivityDashboardResponse = {
  best_worst_weekday: BestWorstWeekdayItem[]
  trends_14: LinearTrendItem[]
  trends_30: LinearTrendItem[]
  session_deep_work_hours_total: number | null
  top_hours: number[] | null
  focus_by_category: FocusByCategoryItem[] | null
  insight: string | null
}

export const getProductivityDashboard = () =>
  api
    .get<ProductivityDashboardResponse>('/analytics/productivity-dashboard')
    .then((res) => res.data)
