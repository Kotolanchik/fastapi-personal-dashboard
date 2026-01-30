import { useState } from 'react'
import { useTranslation } from 'react-i18next'
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

const EXPORT_OPTIONS_KEYS: { value: ExportCategory; key: string }[] = [
  { value: 'daily', key: 'dashboard.dailySummary' },
  { value: 'all', key: 'dashboard.allData' },
  { value: 'health', key: 'nav.health' },
  { value: 'finance', key: 'nav.finance' },
  { value: 'productivity', key: 'nav.productivity' },
  { value: 'learning', key: 'nav.learning' },
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
  const { t } = useTranslation()
  usePageTitle(t('nav.dashboard'))
  const toast = useToast()
  const [exporting, setExporting] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(() => !isOnboardingCompleted())
  const [inactiveReminderDismissed, setInactiveReminderDismissed] = useState(false)
  const [exportCategory, setExportCategory] = useState<ExportCategory>('all')
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
    retry: false,
  })
  const insights = useQuery({
    queryKey: ['insights'],
    queryFn: getInsights,
    retry: false,
  })
  const recommendations = useQuery({
    queryKey: ['recommendations'],
    queryFn: getRecommendations,
    retry: false,
  })
  const goalsQuery = useQuery({ queryKey: ['goals'], queryFn: getGoals, retry: false })
  const trendThisMonth = useQuery({
    queryKey: ['trend-this-month'],
    queryFn: () => getTrendThisMonth().then((d: { metrics: TrendThisMonthItem[] }) => d.metrics),
    retry: false,
  })
  const insightOfTheWeek = useQuery({
    queryKey: ['insight-of-the-week'],
    queryFn: () => getInsightOfTheWeek().then((d: InsightOfTheWeekResponse) => d.insight),
    retry: false,
  })
  const weekdayTrends = useQuery({
    queryKey: ['weekday-trends'],
    queryFn: getWeekdayTrends,
    retry: false,
  })

  const handleDownloadCsv = async () => {
    setExporting(true)
    try {
      await downloadCsv(exportCategory)
      toast.success(t('dashboard.csvDownloaded'))
    } catch {
      toast.error(t('dashboard.downloadFailed'))
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
          <h3>{t('dashboard.goalsProgress')}</h3>
          <div className="grid cards" style={{ marginTop: '0.5rem' }}>
            {goalsProgress.map((p: GoalProgress) => {
              const daysLeft =
                p.deadline != null
                  ? Math.ceil(
                      (new Date(p.deadline).setHours(0, 0, 0, 0) - new Date().setHours(0, 0, 0, 0)) /
                        (24 * 60 * 60 * 1000),
                    )
                  : null
              const almostThere = p.progress_pct != null && p.progress_pct >= 90
              const fallingBehind =
                p.progress_pct != null &&
                p.progress_pct < 50 &&
                (daysLeft == null || daysLeft <= 14)
              return (
                <div key={p.goal_id} className="card">
                  <h4>{p.title}</h4>
                  {(almostThere || fallingBehind) && (
                    <p className="small" style={{ marginBottom: '0.25rem' }}>
                      {almostThere && (
                        <span className="goal-badge goal-badge-success">
                          {t('dashboard.goalAlmostThere')}
                        </span>
                      )}
                      {fallingBehind && !almostThere && (
                        <span className="goal-badge goal-badge-warning">
                          {t('dashboard.goalFallingBehind')}
                        </span>
                      )}
                    </p>
                  )}
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
                        ? t('dashboard.currentValueTarget', { current: p.current_value.toFixed(1) })
                        : t('dashboard.addEntriesToProgress')}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      )}
      <div className="card export-bar">
        <h3>{t('dashboard.exportData')}</h3>
        <p className="muted">{t('dashboard.exportSubtitle')}</p>
        <div className="export-actions">
          <select
            value={exportCategory}
            onChange={(e) => setExportCategory(e.target.value as ExportCategory)}
            aria-label={t('dashboard.exportCategory')}
          >
            {EXPORT_OPTIONS_KEYS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {t(opt.key)}
              </option>
            ))}
          </select>
          <button type="button" disabled={exporting} onClick={handleDownloadCsv}>
            {exporting ? '…' : t('dashboard.downloadCsv')}
          </button>
        </div>
      </div>
      <div className="card">
        <h3>{t('dashboard.lastWeekNumbers')}</h3>
        <p className="muted">{t('dashboard.lastWeekSubtitle')}</p>
        <Link to="/weekly-report" className="primary">
          {t('dashboard.viewLastWeek')}
        </Link>
      </div>
      {trendThisMonth.data && trendThisMonth.data.length > 0 && (
        <section className="card">
          <h3>{t('dashboard.trendThisMonth')}</h3>
          <p className="muted">{t('dashboard.trendThisMonthSubtitle')}</p>
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
          <h3>{t('dashboard.byWeekdayTrends')}</h3>
          {weekdayTrends.data.best_worst_weekday?.length > 0 && (
            <div style={{ marginBottom: '0.5rem' }}>
              {weekdayTrends.data.best_worst_weekday.map((b: BestWorstWeekdayItem) => (
                <p key={b.metric} className="muted" style={{ margin: '0.25rem 0' }}>
                  <strong>{b.metric.replace(/_/g, ' ')}:</strong> {t('common.best')} {b.best_weekday} ({b.best_value}), {t('common.worst')} {b.worst_weekday} ({b.worst_value})
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
          <h4>{t('dashboard.sleepAvg')}</h4>
          <p className="metric">
            {health.data?.length
              ? (health.data.reduce((sum, item) => sum + item.sleep_hours, 0) / health.data.length).toFixed(1)
              : '—'}
          </p>
        </div>
        <div className="card">
          <h4>{t('dashboard.totalIncome')}</h4>
          <p className="metric">
            {finance.data?.length
              ? finance.data.reduce((sum, item) => sum + item.income, 0).toFixed(0)
              : '—'}
          </p>
        </div>
        <div className="card">
          <h4>{t('dashboard.deepWorkHours')}</h4>
          <p className="metric">
            {productivity.data?.length
              ? productivity.data.reduce((sum, item) => sum + item.deep_work_hours, 0).toFixed(1)
              : '—'}
          </p>
        </div>
        <div className="card">
          <h4>{t('dashboard.studyHours')}</h4>
          <p className="metric">
            {learning.data?.length
              ? learning.data.reduce((sum, item) => sum + item.study_hours, 0).toFixed(1)
              : '—'}
          </p>
        </div>
      </section>

      <section className="grid charts">
        <div className="card">
          <h3>{t('dashboard.healthTrends')}</h3>
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
          <h3>{t('dashboard.financeTrends')}</h3>
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
          <h3>{t('dashboard.learningTrends')}</h3>
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
          <h3>{t('dashboard.correlations')}</h3>
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
            <p className="muted">{t('dashboard.noCorrelations')}</p>
          )}
        </div>
        <div className="card">
          <h3>{t('dashboard.insights')}</h3>
          {insightOfTheWeek.data && (
            <div className="insight-of-the-week" style={{ marginBottom: '0.75rem', padding: '0.5rem', background: 'var(--surface)', borderRadius: 4 }}>
              <strong>{t('dashboard.insightOfTheWeek')}</strong>
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
            !insightOfTheWeek.data && <p className="muted">{t('dashboard.noInsights')}</p>
          )}
        </div>
        <div className="card">
          <h3>{t('dashboard.recommendations')}</h3>
          {recommendations.data?.recommendations?.length ? (
            <ul className="list">
              {recommendations.data.recommendations.map((item, index) => (
                <li key={`${item.message}-${index}`}>{item.message}</li>
              ))}
            </ul>
          ) : (
            <p className="muted">{t('dashboard.noRecommendations')}</p>
          )}
        </div>
      </section>
    </div>
  )
}
