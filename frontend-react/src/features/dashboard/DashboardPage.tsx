import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { OnboardingModal, isOnboardingCompleted } from '../onboarding/OnboardingModal'
import { InactiveReminderModal, wasInactiveReminderDismissed } from './InactiveReminderModal'
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getCorrelations,
  getInsights,
  getRecommendations,
  getTrendThisMonth,
  getInsightOfTheWeek,
  getWeekdayTrends,
  type InsightOfTheWeekResponse,
  type TrendThisMonthItem,
  type BestWorstWeekdayItem,
  type LinearTrendItem,
} from '../../shared/api/analytics'
import { downloadCsv, type ExportCategory } from '../../shared/api/export'
import { useToast } from '../../shared/components/Toast'
import {
  type FinanceEntry,
  type HealthEntry,
  type LearningEntry,
  type ProductivityEntry,
  fetchEntries,
} from '../../shared/api/entries'
import { Link } from 'react-router-dom'
import { getGoals, type GoalProgress } from '../../shared/api/goals'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

const toChart = (data: HealthEntry[]) =>
  data.map((entry) => ({
    date: entry.local_date,
    sleep: entry.sleep_hours,
    energy: entry.energy_level,
    wellbeing: entry.wellbeing,
  }))

const toFinanceChart = (data: FinanceEntry[]) =>
  data.map((entry) => ({
    date: entry.local_date,
    income: entry.income,
    expense: entry.expense_food + entry.expense_transport + entry.expense_health + entry.expense_other,
  }))

const toProductivityChart = (data: ProductivityEntry[]) =>
  data.map((entry) => ({
    date: entry.local_date,
    deepWork: entry.deep_work_hours,
    focus: entry.focus_level,
  }))

const toLearningChart = (data: LearningEntry[]) =>
  data.map((entry) => ({
    date: entry.local_date,
    study: entry.study_hours,
  }))

const EXPORT_OPTIONS: { value: ExportCategory; label: string }[] = [
  { value: 'daily', label: 'Daily summary' },
  { value: 'all', label: 'All data' },
  { value: 'health', label: 'Health' },
  { value: 'finance', label: 'Finance' },
  { value: 'productivity', label: 'Productivity' },
  { value: 'learning', label: 'Learning' },
]

const INACTIVE_DAYS_THRESHOLD = 3

function getLastEntryDate(
  health: { local_date: string }[] | undefined,
  finance: { local_date: string }[] | undefined,
  productivity: { local_date: string }[] | undefined,
  learning: { local_date: string }[] | undefined,
): string | null {
  const dates: string[] = []
  for (const list of [health, finance, productivity, learning]) {
    if (list?.length) list.forEach((e) => dates.push(e.local_date))
  }
  if (dates.length === 0) return null
  return dates.sort()[dates.length - 1]
}

function daysSince(dateStr: string): number {
  const then = new Date(dateStr)
  const now = new Date()
  then.setHours(0, 0, 0, 0)
  now.setHours(0, 0, 0, 0)
  return Math.floor((now.getTime() - then.getTime()) / (24 * 60 * 60 * 1000))
}

export const DashboardPage = () => {
  usePageTitle('Dashboard')
  const toast = useToast()
  const [exporting, setExporting] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(() => !isOnboardingCompleted())
  const [inactiveReminderDismissed, setInactiveReminderDismissed] = useState(false)
  const health = useQuery({
    queryKey: ['health'],
    queryFn: () => fetchEntries<HealthEntry>('health'),
  })
  const finance = useQuery({
    queryKey: ['finance'],
    queryFn: () => fetchEntries<FinanceEntry>('finance'),
  })
  const productivity = useQuery({
    queryKey: ['productivity'],
    queryFn: () => fetchEntries<ProductivityEntry>('productivity'),
  })
  const learning = useQuery({
    queryKey: ['learning'],
    queryFn: () => fetchEntries<LearningEntry>('learning'),
  })
  const correlations = useQuery({
    queryKey: ['correlations'],
    queryFn: getCorrelations,
  })
  const insights = useQuery({
    queryKey: ['insights'],
    queryFn: getInsights,
  })
  const recommendations = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations,
  })
  const goalsQuery = useQuery({ queryKey: ['goals'], queryFn: getGoals })
  const trendThisMonth = useQuery({
    queryKey: ['trend-this-month'],
    queryFn: () => getTrendThisMonth().then((d: { metrics: TrendThisMonthItem[] }) => d.metrics),
  })
  const insightOfTheWeek = useQuery({
    queryKey: ['insight-of-the-week'],
    queryFn: () => getInsightOfTheWeek().then((d: InsightOfTheWeekResponse) => d.insight),
  })
  const weekdayTrends = useQuery({
    queryKey: ['weekday-trends'],
    queryFn: getWeekdayTrends,
  })

  const isLoading =
    health.isLoading ||
    finance.isLoading ||
    productivity.isLoading ||
    learning.isLoading ||
    correlations.isLoading ||
    insights.isLoading ||
    recommendations.isLoading ||
    goalsQuery.isLoading ||
    trendThisMonth.isLoading ||
    insightOfTheWeek.isLoading ||
    weekdayTrends.isLoading

  if (isLoading) {
    return (
      <div className="stack">
        <section className="grid cards">
          <div className="card skeleton-card"><div className="skeleton metric-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton metric-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton metric-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton metric-skeleton" /></div>
        </section>
        <section className="grid charts">
          <div className="card skeleton-card"><div className="skeleton chart-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton chart-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton chart-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton chart-skeleton" /></div>
        </section>
        <section className="grid columns">
          <div className="card skeleton-card"><div className="skeleton list-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton list-skeleton" /></div>
          <div className="card skeleton-card"><div className="skeleton list-skeleton" /></div>
        </section>
      </div>
    )
  }

  const [exportCategory, setExportCategory] = useState<ExportCategory>('all')
  const handleDownloadCsv = async () => {
    setExporting(true)
    try {
      await downloadCsv(exportCategory)
      toast.success('CSV downloaded.')
    } catch {
      toast.error('Download failed.')
    } finally {
      setExporting(false)
    }
  }

  const goalsProgress = goalsQuery.data?.progress ?? []
  const lastEntryDate = getLastEntryDate(
    health.data,
    finance.data,
    productivity.data,
    learning.data,
  )
  const daysSinceLast = lastEntryDate === null ? null : daysSince(lastEntryDate)
  const showInactiveReminder =
    !showOnboarding &&
    !inactiveReminderDismissed &&
    !wasInactiveReminderDismissed() &&
    (lastEntryDate === null || (daysSinceLast !== null && daysSinceLast > INACTIVE_DAYS_THRESHOLD))

  return (
    <div className="stack">
      {showOnboarding && (
        <OnboardingModal onDismiss={() => setShowOnboarding(false)} />
      )}
      {showInactiveReminder && (
        <InactiveReminderModal
          daysInactive={lastEntryDate === null ? null : daysSinceLast}
          onDismiss={() => setInactiveReminderDismissed(true)}
        />
      )}
      {goalsProgress.length > 0 && (
        <section className="card">
          <h3>Goals progress</h3>
          <div className="grid cards" style={{ marginTop: '0.5rem' }}>
            {goalsProgress.map((p: GoalProgress) => (
              <div key={p.goal_id} className="card">
                <h4>{p.title}</h4>
                {p.progress_pct != null ? (
                  <>
                    <p className="metric">{p.progress_pct.toFixed(0)}%</p>
                    {p.current_value != null && p.target_value != null && (
                      <p className="muted">
                        {p.current_value.toFixed(1)} / {p.target_value}
                        {p.target_metric ? ` ${p.target_metric}` : ''}
                      </p>
                    )}
                  </>
                ) : (
                  <p className="muted">
                    {p.current_value != null
                      ? `Current: ${p.current_value.toFixed(1)} (add target in Settings)`
                      : 'Add entries to see progress'}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
      <div className="card export-bar">
        <h3>Export data</h3>
        <p className="muted">Download your entries as CSV.</p>
        <div className="export-actions">
          <select
            value={exportCategory}
            onChange={(e) => setExportCategory(e.target.value as ExportCategory)}
            aria-label="Export category"
          >
            {EXPORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <button type="button" disabled={exporting} onClick={handleDownloadCsv}>
            {exporting ? '…' : 'Download CSV'}
          </button>
        </div>
      </div>
      <div className="card">
        <h3>Last week in numbers</h3>
        <p className="muted">Sums, averages, and one insight for the past 7 days.</p>
        <Link to="/weekly-report" className="primary">
          View last week →
        </Link>
      </div>
      {trendThisMonth.data && trendThisMonth.data.length > 0 && (
        <section className="card">
          <h3>Trend this month</h3>
          <p className="muted">This month vs previous month (↑ up, ↓ down).</p>
          <div className="grid cards" style={{ marginTop: '0.5rem' }}>
            {trendThisMonth.data.map((m: TrendThisMonthItem) => (
              <div key={m.metric} className="card">
                <h4>{m.label}</h4>
                <p className="metric">
                  {typeof m.value === 'number' && !Number.isInteger(m.value) ? m.value.toFixed(1) : m.value}
                  {m.direction === 'up' && ' ↑'}
                  {m.direction === 'down' && ' ↓'}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
      {weekdayTrends.data && (weekdayTrends.data.best_worst_weekday?.length > 0 || weekdayTrends.data.trends_14?.length > 0 || weekdayTrends.data.trends_30?.length > 0) && (
        <section className="card">
          <h3>By weekday & recent trends</h3>
          {weekdayTrends.data.best_worst_weekday?.length > 0 && (
            <div style={{ marginBottom: '0.5rem' }}>
              {weekdayTrends.data.best_worst_weekday.map((b: BestWorstWeekdayItem) => (
                <p key={b.metric} className="muted" style={{ margin: '0.25rem 0' }}>
                  <strong>{b.metric.replace(/_/g, ' ')}:</strong> best {b.best_weekday} ({b.best_value}), worst {b.worst_weekday} ({b.worst_value})
                </p>
              ))}
            </div>
          )}
          {(weekdayTrends.data.trends_14?.length > 0 || weekdayTrends.data.trends_30?.length > 0) && (
            <p className="muted" style={{ margin: 0 }}>
              Last 14/30 days: {[...(weekdayTrends.data.trends_14 || []), ...(weekdayTrends.data.trends_30 || [])]
                .filter((t: LinearTrendItem, i: number, a: LinearTrendItem[]) => a.findIndex(x => x.metric === t.metric) === i)
                .map((t: LinearTrendItem) => `${t.metric} ${t.direction === 'up' ? '↑' : t.direction === 'down' ? '↓' : '→'}`)
                .join(', ')}
            </p>
          )}
        </section>
      )}
      <section className="grid cards">
        <div className="card">
          <h4>Sleep avg</h4>
          <p className="metric">
            {health.data?.length
              ? (health.data.reduce((sum, item) => sum + item.sleep_hours, 0) / health.data.length).toFixed(1)
              : '—'}
          </p>
        </div>
        <div className="card">
          <h4>Total income</h4>
          <p className="metric">
            {finance.data?.length
              ? finance.data.reduce((sum, item) => sum + item.income, 0).toFixed(0)
              : '—'}
          </p>
        </div>
        <div className="card">
          <h4>Deep work hours</h4>
          <p className="metric">
            {productivity.data?.length
              ? productivity.data.reduce((sum, item) => sum + item.deep_work_hours, 0).toFixed(1)
              : '—'}
          </p>
        </div>
        <div className="card">
          <h4>Study hours</h4>
          <p className="metric">
            {learning.data?.length
              ? learning.data.reduce((sum, item) => sum + item.study_hours, 0).toFixed(1)
              : '—'}
          </p>
        </div>
      </section>

      <section className="grid charts">
        <div className="card">
          <h3>Health trends</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={health.data ? toChart(health.data) : []}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="sleep" stroke="#3b82f6" />
              <Line type="monotone" dataKey="energy" stroke="#10b981" />
              <Line type="monotone" dataKey="wellbeing" stroke="#f59e0b" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Finance trends</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={finance.data ? toFinanceChart(finance.data) : []}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="income" stroke="#3b82f6" />
              <Line type="monotone" dataKey="expense" stroke="#ef4444" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Productivity</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={productivity.data ? toProductivityChart(productivity.data) : []}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="deepWork" stroke="#3b82f6" />
              <Line type="monotone" dataKey="focus" stroke="#f59e0b" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Learning</h3>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={learning.data ? toLearningChart(learning.data) : []}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="study" stroke="#10b981" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="grid columns">
        <div className="card">
          <h3>Correlations</h3>
          {correlations.data?.correlations?.length ? (
            <ul className="list">
              {correlations.data.correlations.map((item) => (
                <li key={`${item.metric_a}-${item.metric_b}`}>
                  {item.metric_a} ↔ {item.metric_b}: {item.correlation.toFixed(2)} (n=
                  {item.sample_size})
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted">No data for correlations yet.</p>
          )}
        </div>
        <div className="card">
          <h3>Insights</h3>
          {insightOfTheWeek.data && (
            <div className="insight-of-the-week" style={{ marginBottom: '0.75rem', padding: '0.5rem', background: 'var(--surface)', borderRadius: 4 }}>
              <strong>Insight of the week</strong>
              <p style={{ margin: '0.25rem 0 0' }}>{insightOfTheWeek.data}</p>
            </div>
          )}
          {insights.data?.insights?.length ? (
            <ul className="list">
              {insights.data.insights.map((item, index) => (
                <li key={`${item.message}-${index}`}>{item.message}</li>
              ))}
            </ul>
          ) : (
            !insightOfTheWeek.data && <p className="muted">No insights yet.</p>
          )}
        </div>
        <div className="card">
          <h3>Recommendations</h3>
          {recommendations.data?.recommendations?.length ? (
            <ul className="list">
              {recommendations.data.recommendations.map((item, index) => (
                <li key={`${item.message}-${index}`}>{item.message}</li>
              ))}
            </ul>
          ) : (
            <p className="muted">No recommendations yet.</p>
          )}
        </div>
      </section>
    </div>
  )
}
