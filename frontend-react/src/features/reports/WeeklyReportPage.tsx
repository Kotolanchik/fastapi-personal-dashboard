import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'

import { getWeeklyReport } from '../../shared/api/analytics'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

const formatDate = (s: string, locale: string) => {
  try {
    return new Date(s).toLocaleDateString(locale === 'ru' ? 'ru-RU' : 'en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  } catch {
    return s
  }
}

export const WeeklyReportPage = () => {
  const { t, i18n } = useTranslation()
  usePageTitle(t('nav.weeklyReport'))
  const { data, isLoading, error } = useQuery({
    queryKey: ['weekly-report'],
    queryFn: getWeeklyReport,
  })

  if (isLoading) {
    return (
      <div className="stack">
        <div className="card skeleton-card">
          <div className="skeleton chart-skeleton" style={{ height: 200 }} />
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="stack">
        <div className="card">
          <p className="muted">{t('reports.couldNotLoad')}</p>
        </div>
      </div>
    )
  }

  const spheres = Object.entries(data.summary)
  const locale = i18n.language?.startsWith('ru') ? 'ru' : 'en'
  const startStr = formatDate(data.period_start, locale)
  const endStr = formatDate(data.period_end, locale)

  return (
    <div className="stack">
      <div className="card">
        <h3>{t('reports.lastWeekNumbers')}</h3>
        <p className="muted">{t('reports.periodSubtitle', { start: startStr, end: endStr })}</p>
      </div>
      {spheres.length > 0 && (
        <section className="grid columns">
          {spheres.map(([sphere, metrics]) => (
            <div key={sphere} className="card">
              <h3 className="capitalize">{sphere}</h3>
              <ul className="list">
                {Object.entries(metrics).map(([key, value]) =>
                  value != null ? (
                    <li key={key}>
                      <strong>{key.replace(/_/g, ' ')}:</strong>{' '}
                      {typeof value === 'number'
                        ? Number.isInteger(value)
                          ? value
                          : value.toFixed(1)
                        : value}
                    </li>
                  ) : null,
                )}
              </ul>
            </div>
          ))}
        </section>
      )}
      {data.insight && (
        <div className="card">
          <h3>{t('reports.insight')}</h3>
          <p>{data.insight}</p>
        </div>
      )}
      {spheres.length === 0 && !data.insight && (
        <div className="card">
          <p className="muted">{t('reports.addEntriesHint')}</p>
        </div>
      )}
    </div>
  )
}
