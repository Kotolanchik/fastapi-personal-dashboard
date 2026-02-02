import { useState, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { useAuth } from '../auth/AuthContext'
import { updateProfile } from '../../shared/api/auth'
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
  getProductivityDashboard,
  getRecommendations,
  getTrendThisMonth,
  getInsightOfTheWeek,
  getWeekdayTrends,
  type InsightOfTheWeekResponse,
  type TrendThisMonthItem,
  type BestWorstWeekdayItem,
  type LinearTrendItem,
} from '../../shared/api/analytics'
import { getReminders } from '../../shared/api/reminders'
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

const DASHBOARD_BLOCK_IDS = [
  'reminderBanner',
  'goals',
  'export',
  'lastWeek',
  'trendThisMonth',
  'weekdayTrends',
  'productivityDashboard',
  'summaryCards',
  'healthChart',
  'financeChart',
  'productivityChart',
  'learningChart',
  'correlations',
  'insights',
  'recommendations',
] as const
type DashboardBlockId = (typeof DASHBOARD_BLOCK_IDS)[number]

const DEFAULT_ENABLED_BLOCKS: string[] = [...DASHBOARD_BLOCK_IDS]

function getEnabledBlocks(userSettings: { enabled_blocks?: string[] } | null | undefined, localStorageKey: string): string[] {
  const fromUser = userSettings?.enabled_blocks
  if (fromUser && Array.isArray(fromUser) && fromUser.length > 0) return fromUser
  try {
    const stored = localStorage.getItem(localStorageKey)
    if (stored) {
      const parsed = JSON.parse(stored) as string[]
      if (Array.isArray(parsed)) return parsed
    }
  } catch {
    // ignore
  }
  return DEFAULT_ENABLED_BLOCKS
}

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

function yesterdayISO(): string {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().slice(0, 10)
}

const DASHBOARD_STORAGE_KEY = 'lifepulse_dashboard_blocks'

export const DashboardPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.dashboard'))
  const { user, refreshUser } = useAuth()
  const queryClient = useQueryClient()
  const toast = useToast()
  const [exporting, setExporting] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(() => !isOnboardingCompleted())
  const [inactiveReminderDismissed, setInactiveReminderDismissed] = useState(false)
  const [exportCategory, setExportCategory] = useState<ExportCategory>('all')
  const [showWidgetSettings, setShowWidgetSettings] = useState(false)

  const enabledBlocks = useMemo(
    () => getEnabledBlocks(user?.dashboard_settings ?? null, DASHBOARD_STORAGE_KEY),
    [user?.dashboard_settings],
  )

  const isBlockEnabled = (id: DashboardBlockId) => enabledBlocks.includes(id)

  const setBlockEnabled = async (id: DashboardBlockId, enabled: boolean) => {
    const next = enabled
      ? [...enabledBlocks, id]
      : enabledBlocks.filter((b) => b !== id)
    if (next.length === 0) return
    try {
      localStorage.setItem(DASHBOARD_STORAGE_KEY, JSON.stringify(next))
      await updateProfile({ dashboard_settings: { enabled_blocks: next } })
      await refreshUser()
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
      toast.success(t('dashboard.widgetSaved'))
    } catch {
      toast.error(t('dashboard.widgetSaveFailed'))
    }
  }
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
  const reminders = useQuery({
    queryKey: ['reminders'],
    queryFn: getReminders,
    retry: false,
  })
  const productivityDashboard = useQuery({
    queryKey: ['productivity-dashboard'],
    queryFn: getProductivityDashboard,
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

  const healthYesterdayReminder = reminders.data?.reminders?.find(
    (r) => r.type === 'health_yesterday' && r.should_remind,
  )

  const isDashboardLoading =
    health.isLoading ||
    finance.isLoading ||
    productivity.isLoading ||
    learning.isLoading

  if (isDashboardLoading) {
    return (
      <div className="stack">
        <div className="card skeleton-card">
          <div className="skeleton chart-skeleton" style={{ height: 120 }} />
        </div>
        <div className="grid cards">
          <div className="card skeleton-card">
            <div className="skeleton metric-skeleton" />
          </div>
          <div className="card skeleton-card">
            <div className="skeleton metric-skeleton" />
          </div>
          <div className="card skeleton-card">
            <div className="skeleton metric-skeleton" />
          </div>
          <div className="card skeleton-card">
            <div className="skeleton metric-skeleton" />
          </div>
        </div>
        <div className="card skeleton-card">
          <div className="skeleton list-skeleton" />
        </div>
      </div>
    )
  }

  return (
    <div className="stack">
      {showOnboarding && (
        <OnboardingModal onDismiss={() => setShowOnboarding(false)} />
      )}
      <div className="card export-bar" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <button
          type="button"
          className="secondary"
          onClick={() => setShowWidgetSettings(!showWidgetSettings)}
          aria-label={t('dashboard.customizeWidgets')}
        >
          {showWidgetSettings ? t('dashboard.hideWidgetSettings') : t('dashboard.customizeWidgets')}
        </button>
        {showWidgetSettings && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
            {DASHBOARD_BLOCK_IDS.map((id) => (
              <label key={id} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.9rem' }}>
                <input
                  type="checkbox"
                  checked={isBlockEnabled(id)}
                  onChange={(e) => setBlockEnabled(id, e.target.checked)}
                />
                <span>{t(`dashboard.widgets.${id}`)}</span>
              </label>
            ))}
          </div>
        )}
      </div>
      {isBlockEnabled('reminderBanner') && healthYesterdayReminder && (
        <div className="card banner" role="status">
          <p style={{ margin: 0 }}>
            {healthYesterdayReminder.message}{' '}
            <Link to={`/health?date=${yesterdayISO()}`} className="primary">
              {t('reminders.fillHealth')}
            </Link>
          </p>
        </div>
      )}
      {showInactiveReminder && (
        <InactiveReminderModal
          daysInactive={lastEntryDate === null ? null : daysSinceLast}
          onDismiss={() => setInactiveReminderDismissed(true)}
        />
      )}
      {isBlockEnabled('goals') && goalsProgress.length > 0 && (
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
      {isBlockEnabled('export') && (
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
      )}
      {isBlockEnabled('lastWeek') && (
      <div className="card">
        <h3>{t('dashboard.lastWeekNumbers')}</h3>
        <p className="muted">{t('dashboard.lastWeekSubtitle')}</p>
        <Link to="/weekly-report" className="primary">
          {t('dashboard.viewLastWeek')}
        </Link>
      </div>
      )}
      {isBlockEnabled('trendThisMonth') && trendThisMonth.data && trendThisMonth.data.length > 0 && (
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
      {isBlockEnabled('weekdayTrends') && weekdayTrends.data && (weekdayTrends.data.best_worst_weekday?.length > 0 || weekdayTrends.data.trends_14?.length > 0 || weekdayTrends.data.trends_30?.length > 0) && (
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
      {isBlockEnabled('productivityDashboard') && productivityDashboard.data && (
        <section className="card">
          <h3>{t('dashboard.productivityDashboard')}</h3>
          <p className="muted">{t('dashboard.productivityDashboardSubtitle')}</p>
          <div className="stack" style={{ marginTop: '0.5rem' }}>
            {productivityDashboard.data.best_worst_weekday?.length > 0 && (
              <div>
                <h4 className="small">{t('dashboard.byWeekdayTrends')}</h4>
                {productivityDashboard.data.best_worst_weekday.map((b: BestWorstWeekdayItem) => (
                  <p key={b.metric} className="muted" style={{ margin: '0.25rem 0' }}>
                    <strong>{b.metric.replace(/_/g, ' ')}:</strong> {t('common.best')} {b.best_weekday} ({b.best_value}), {t('common.worst')} {b.worst_weekday} ({b.worst_value})
                  </p>
                ))}
              </div>
            )}
            {(productivityDashboard.data.trends_14?.length > 0 || productivityDashboard.data.trends_30?.length > 0) && (
              <p className="muted" style={{ margin: 0 }}>
                {[...(productivityDashboard.data.trends_14 || []), ...(productivityDashboard.data.trends_30 || [])]
                  .filter((tr: LinearTrendItem, i: number, a: LinearTrendItem[]) => a.findIndex((x) => x.metric === tr.metric) === i)
                  .map((tr: LinearTrendItem) => `${tr.metric} ${tr.direction === 'up' ? '↑' : tr.direction === 'down' ? '↓' : '→'}`)
                  .join(', ')}
              </p>
            )}
            {productivityDashboard.data.session_deep_work_hours_total != null && (
              <p className="muted">
                {t('dashboard.sessionDeepWorkTotal')}: {productivityDashboard.data.session_deep_work_hours_total} h
              </p>
            )}
            {productivityDashboard.data.top_hours?.length > 0 && (
              <p className="muted">
                {t('dashboard.topHoursForFocus')}: {productivityDashboard.data.top_hours.join(', ')}
              </p>
            )}
            {productivityDashboard.data.focus_by_category?.length > 0 && (
              <div>
                <h4 className="small">{t('dashboard.focusByCategory')}</h4>
                <ul className="muted" style={{ margin: '0.25rem 0', paddingLeft: '1.25rem' }}>
                  {productivityDashboard.data.focus_by_category.map((f) => (
                    <li key={f.category}>
                      {f.category}: {f.hours} h
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {productivityDashboard.data.insight && (
              <p className="muted" style={{ marginTop: '0.5rem', fontStyle: 'italic' }}>
                {productivityDashboard.data.insight}
              </p>
            )}
          </div>
        </section>
      )}
      {isBlockEnabled('summaryCards') && (
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
      )}
      <section className="grid charts">
        {isBlockEnabled('healthChart') && (
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
        )}
        {isBlockEnabled('financeChart') && (
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
        )}
        {isBlockEnabled('productivityChart') && (
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
        )}
        {isBlockEnabled('learningChart') && (
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
        )}
      </section>

      <section className="grid columns">
        {isBlockEnabled('correlations') && (
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
        )}
        {isBlockEnabled('insights') && (
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
        )}
        {isBlockEnabled('recommendations') && (
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
        )}
      </section>
    </div>
  )
}
