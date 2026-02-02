import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams } from 'react-router-dom'

import { downloadHealthReport } from '../../shared/api/export'
import { useToast } from '../../shared/components/Toast'
import { EntriesPage } from './EntriesPage'

const ENTRY_TYPE_OPTIONS = [
  { value: 'day', label: 'Day' },
  { value: 'morning', label: 'Morning' },
  { value: 'evening', label: 'Evening' },
]

function yesterdayISO(): string {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toISOString().slice(0, 10)
}

function thirtyDaysAgoISO(): string {
  const d = new Date()
  d.setDate(d.getDate() - 30)
  return d.toISOString().slice(0, 10)
}

export const HealthPage = () => {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const toast = useToast()
  const [reportStart, setReportStart] = useState(thirtyDaysAgoISO())
  const [reportEnd, setReportEnd] = useState(yesterdayISO())
  const [reportDownloading, setReportDownloading] = useState(false)

  const initialDate = searchParams.get('date') ?? undefined

  const handleDownloadHealthReport = async () => {
    setReportDownloading(true)
    try {
      await downloadHealthReport(reportStart, reportEnd)
      toast.success(t('dashboard.csvDownloaded'))
    } catch {
      toast.error(t('dashboard.downloadFailed'))
    } finally {
      setReportDownloading(false)
    }
  }

  return (
    <div className="stack">
      <section className="card">
        <h3>{t('export.healthReport')}</h3>
        <p className="muted">{t('export.healthReportHint')}</p>
        <div className="form-grid">
          <label>
            {t('export.startDate')}
            <input
              type="date"
              value={reportStart}
              onChange={(e) => setReportStart(e.target.value)}
            />
          </label>
          <label>
            {t('export.endDate')}
            <input
              type="date"
              value={reportEnd}
              onChange={(e) => setReportEnd(e.target.value)}
            />
          </label>
          <button type="button" disabled={reportDownloading} onClick={handleDownloadHealthReport}>
            {reportDownloading ? t('common.loading') : t('dashboard.downloadCsv')}
          </button>
        </div>
      </section>
      <EntriesPage
        title={t('nav.health')}
        resource="health"
        initialDate={initialDate}
        fields={[
        { name: 'entry_type', label: t('entries.labels.health.entry_type'), type: 'select', options: ENTRY_TYPE_OPTIONS },
        { name: 'sleep_hours', label: t('entries.labels.health.sleep_hours'), type: 'number', min: 0, max: 24 },
        { name: 'energy_level', label: t('entries.labels.health.energy_level'), type: 'int', min: 1, max: 10 },
        { name: 'supplements', label: t('entries.labels.health.supplements'), type: 'text', optional: true },
        { name: 'weight_kg', label: t('entries.labels.health.weight_kg'), type: 'number', optional: true },
        { name: 'wellbeing', label: t('entries.labels.health.wellbeing'), type: 'int', min: 1, max: 10 },
        { name: 'steps', label: t('entries.labels.health.steps'), type: 'int', min: 0, optional: true },
        { name: 'heart_rate_avg', label: t('entries.labels.health.heart_rate_avg'), type: 'int', min: 30, max: 250, optional: true },
        { name: 'workout_minutes', label: t('entries.labels.health.workout_minutes'), type: 'int', min: 0, optional: true },
        { name: 'notes', label: t('entries.labels.health.notes'), type: 'text', optional: true },
        ]}
      />
    </div>
  )
}
