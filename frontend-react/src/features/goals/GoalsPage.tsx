import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { getGoals, type GoalProgress } from '../../shared/api/goals'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

export const GoalsPage = () => {
  usePageTitle('Goals')
  const { data, isLoading } = useQuery({ queryKey: ['goals'], queryFn: getGoals })

  const goals = data?.goals ?? []
  const progress = data?.progress ?? []

  if (isLoading) {
    return (
      <div className="stack">
        <div className="card skeleton-card">
          <div className="skeleton list-skeleton" />
        </div>
      </div>
    )
  }

  return (
    <div className="stack">
      <div className="card flex-between">
        <div>
          <h3>Goals</h3>
          <p className="muted">Your personal goals and progress. Add or edit goals in Settings.</p>
        </div>
        <Link to="/settings" className="primary">
          Edit in Settings
        </Link>
      </div>

      {goals.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p className="empty-state-text">No goals yet</p>
            <p className="muted">Set 1–2 goals in Settings to track progress here and on the dashboard.</p>
            <Link to="/settings" className="empty-state-cta">
              Go to Settings
            </Link>
          </div>
        </div>
      ) : (
        <section className="grid cards">
          {progress.map((p: GoalProgress) => (
            <div key={p.goal_id} className="card">
              <h4>{p.title}</h4>
              <p className="muted small capitalize">{p.sphere}</p>
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
                    ? `Current: ${p.current_value.toFixed(1)} — add target in Settings`
                    : 'Add entries to see progress'}
                </p>
              )}
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
