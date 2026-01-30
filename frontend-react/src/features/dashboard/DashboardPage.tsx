import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { getCorrelations, getInsights, getRecommendations } from '../../shared/api/analytics'
import { downloadCsv, type ExportCategory } from '../../shared/api/export'
import { useToast } from '../../shared/components/Toast'
import {
  type FinanceEntry,
  type HealthEntry,
  type LearningEntry,
  type ProductivityEntry,
  fetchEntries,
} from '../../shared/api/entries'

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

export const DashboardPage = () => {
  const toast = useToast()
  const [exporting, setExporting] = useState(false)
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

  const isLoading =
    health.isLoading ||
    finance.isLoading ||
    productivity.isLoading ||
    learning.isLoading ||
    correlations.isLoading ||
    insights.isLoading ||
    recommendations.isLoading

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

  return (
    <div className="stack">
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
          {insights.data?.insights?.length ? (
            <ul className="list">
              {insights.data.insights.map((item, index) => (
                <li key={`${item.message}-${index}`}>{item.message}</li>
              ))}
            </ul>
          ) : (
            <p className="muted">No insights yet.</p>
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
