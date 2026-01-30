import { useQuery } from '@tanstack/react-query'

import { getWeeklyReport } from '../../shared/api/analytics'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

const formatDate = (s: string) => {
  try {
    return new Date(s).toLocaleDateString(undefined, {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    })
  }
  return s
}

export const WeeklyReportPage = () => {
  usePageTitle('Weekly report')
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
          <p className="muted">Could not load weekly report.</p>
        </div>
      </div>
    )
  }

  const spheres = Object.entries(data.summary)
  const periodLabel = `${formatDate(data.period_start)} – ${formatDate(data.period_end)}`

  return (
    <div className="stack">
      <div className="card">
        <h3>Last week in numbers</h3>
        <p className="muted">{periodLabel} — sums, averages, and one insight.</p>
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
          <h3>Insight</h3>
          <p>{data.insight}</p>
        </div>
      )}
      {spheres.length === 0 && !data.insight && (
        <div className="card">
          <p className="muted">Add entries to see your weekly summary and insights.</p>
        </div>
      )}
    </div>
  )
}
