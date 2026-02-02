import type { FormEvent } from 'react'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import {
  getGoals,
  updateGoal,
  deleteGoal,
  GOAL_SPHERES,
  GOAL_PROGRESS_PERIODS,
  GOAL_METRICS_BY_SPHERE,
  type Goal,
  type GoalProgress,
  type GoalProgressPeriod,
} from '../../shared/api/goals'
import { usePageTitle } from '../../shared/hooks/usePageTitle'
import { useToast } from '../../shared/components/Toast'
import { getErrorMessage } from '../../shared/utils/validation'

const GOAL_MAX_ACTIVE = 5

function daysUntil(deadlineStr: string | null | undefined): number | null {
  if (!deadlineStr) return null
  const end = new Date(deadlineStr)
  const now = new Date()
  end.setHours(0, 0, 0, 0)
  now.setHours(0, 0, 0, 0)
  return Math.ceil((end.getTime() - now.getTime()) / (24 * 60 * 60 * 1000))
}

type EditGoalModalProps = {
  goal: Goal
  progress: GoalProgress | undefined
  onClose: () => void
  onSaved: () => void
  onDelete: (goal: Goal) => void
}

function EditGoalModal({ goal, progress, onClose, onSaved, onDelete }: EditGoalModalProps) {
  const { t } = useTranslation()
  const toast = useToast()
  const [title, setTitle] = useState(goal.title)
  const [sphere, setSphere] = useState(goal.sphere)
  const [targetValue, setTargetValue] = useState(
    goal.target_value != null ? String(goal.target_value) : '',
  )
  const metricsForSphere = GOAL_METRICS_BY_SPHERE[goal.sphere] ?? []
  const initialMetric =
    goal.target_metric && metricsForSphere.includes(goal.target_metric)
      ? goal.target_metric
      : metricsForSphere[0] ?? ''
  const [targetMetric, setTargetMetric] = useState(initialMetric)
  const [deadline, setDeadline] = useState(
    goal.deadline ? goal.deadline.slice(0, 10) : '',
  )
  const [saving, setSaving] = useState(false)

  const metrics = GOAL_METRICS_BY_SPHERE[sphere] ?? []

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setSaving(true)
    try {
      await updateGoal(goal.id, {
        title: title.trim(),
        sphere,
        target_value: targetValue ? parseFloat(targetValue) : null,
        target_metric: targetMetric || null,
        deadline: deadline ? deadline : null,
      })
      toast.success(t('goals.updated'))
      onSaved()
      onClose()
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div className="modal card" onClick={(e) => e.stopPropagation()}>
        <div className="flex-between" style={{ marginBottom: '1rem' }}>
          <h3>{t('goals.editGoal')}</h3>
          <button type="button" className="secondary small" onClick={onClose} aria-label={t('common.close')}>
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            {t('settings.goalTitle')}
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t('settings.goalTitlePlaceholder')}
              maxLength={255}
              required
            />
          </label>
          <label>
            {t('settings.sphere')}
            <select
              value={sphere}
              onChange={(e) => {
                setSphere(e.target.value)
                setTargetMetric((GOAL_METRICS_BY_SPHERE[e.target.value] ?? [])[0] ?? '')
              }}
            >
              {GOAL_SPHERES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('goals.targetMetric')}
            <select
              value={targetMetric}
              onChange={(e) => setTargetMetric(e.target.value)}
            >
              <option value="">—</option>
              {metrics.map((m) => (
                <option key={m} value={m}>
                  {t(`entries.labels.${sphere}.${m}`) || m}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('settings.targetValueOptional')}
            <input
              type="number"
              step="any"
              value={targetValue}
              onChange={(e) => setTargetValue(e.target.value)}
              placeholder={t('settings.targetValuePlaceholder')}
            />
          </label>
          <label>
            {t('goals.deadline')}
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
            />
          </label>
          <div className="form-actions" style={{ flexWrap: 'wrap', gap: '0.5rem' }}>
            <button type="button" className="danger small" onClick={() => onDelete(goal)}>
              {t('common.remove')}
            </button>
            <div style={{ flex: 1, display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button type="button" className="secondary" onClick={onClose}>
                {t('common.cancel')}
              </button>
              <button type="submit" disabled={saving || !title.trim()}>
                {saving ? t('common.saving') : t('common.save')}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export const GoalsPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.goals'))
  const toast = useToast()
  const queryClient = useQueryClient()
  const [period, setPeriod] = useState<GoalProgressPeriod>('7d')
  const [includeArchived, setIncludeArchived] = useState(false)
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null)

  const { data, isLoading } = useQuery({
    queryKey: ['goals', period, includeArchived],
    queryFn: () => getGoals({ period, include_archived: includeArchived }),
  })

  const goals = data?.goals ?? []
  const progress = data?.progress ?? []
  const progressByGoalId = progress.reduce<Record<number, GoalProgress>>((acc, p) => {
    acc[p.goal_id] = p
    return acc
  }, {})

  const activeGoals = goals.filter((g) => !g.archived)
  const archivedGoals = goals.filter((g) => g.archived)

  const handleArchive = async (goal: Goal) => {
    try {
      await updateGoal(goal.id, { archived: true })
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      toast.success(t('goals.archived'))
    } catch {
      toast.error(t('goals.failedToArchive'))
    }
  }

  const handleUnarchive = async (goal: Goal) => {
    if (activeGoals.length >= GOAL_MAX_ACTIVE) {
      toast.error(t('goals.maxActiveReached', { max: GOAL_MAX_ACTIVE }))
      return
    }
    try {
      await updateGoal(goal.id, { archived: false })
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      toast.success(t('goals.unarchived'))
    } catch {
      toast.error(t('goals.failedToUnarchive'))
    }
  }

  const handleDelete = async (goal: Goal) => {
    if (!window.confirm(t('settings.deleteGoal', { title: goal.title }))) return
    try {
      await deleteGoal(goal.id)
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      setEditingGoal(null)
      toast.success(t('settings.goalRemoved'))
    } catch {
      toast.error(t('settings.failedToRemoveGoal'))
    }
  }

  const refreshGoals = () => queryClient.invalidateQueries({ queryKey: ['goals'] })

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
      <div className="card flex-between flex-wrap" style={{ gap: '1rem' }}>
        <div>
          <h3>{t('goals.title')}</h3>
          <p className="muted">{t('goals.subtitle')}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className="muted small">{t('goals.period')}</span>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as GoalProgressPeriod)}
              aria-label={t('goals.period')}
            >
              {GOAL_PROGRESS_PERIODS.map((p) => (
                <option key={p} value={p}>
                  {t(`goals.period_${p}`)}
                </option>
              ))}
            </select>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <input
              type="checkbox"
              checked={includeArchived}
              onChange={(e) => setIncludeArchived(e.target.checked)}
            />
            <span className="muted small">{t('goals.showArchived')}</span>
          </label>
          <Link to="/settings" className="primary">
            {t('goals.addGoal')}
          </Link>
        </div>
      </div>

      {goals.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <p className="empty-state-text">{t('goals.noGoalsYet')}</p>
            <p className="muted">{t('goals.noGoalsHint')}</p>
            <Link to="/settings" className="empty-state-cta">
              {t('goals.goToSettings')}
            </Link>
          </div>
        </div>
      ) : (
        <>
          <section className="grid cards">
            {(includeArchived ? goals : activeGoals).map((goal) => {
              const p = progressByGoalId[goal.id]
              const daysLeft = daysUntil(goal.deadline ?? undefined)
              const pct = p?.progress_pct
              const barClass =
                pct != null
                  ? pct >= 90
                    ? 'success'
                    : pct < 50
                      ? 'warning'
                      : ''
                  : ''

              return (
                <div key={goal.id} className={`card ${goal.archived ? 'nested' : ''}`}>
                  <div className="flex-between" style={{ marginBottom: '0.25rem' }}>
                    <h4>{p?.title ?? goal.title}</h4>
                    {!goal.archived && (
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          type="button"
                          className="secondary small"
                          onClick={() => setEditingGoal(goal)}
                          aria-label={t('goals.editGoal')}
                        >
                          {t('common.edit')}
                        </button>
                        <button
                          type="button"
                          className="secondary small"
                          onClick={() => handleArchive(goal)}
                          aria-label={t('goals.archive')}
                        >
                          {t('goals.archive')}
                        </button>
                      </div>
                    )}
                    {goal.archived && (
                      <button
                        type="button"
                        className="secondary small"
                        onClick={() => handleUnarchive(goal)}
                        aria-label={t('goals.unarchive')}
                      >
                        {t('goals.unarchive')}
                      </button>
                    )}
                  </div>
                  {goal.archived && (
                    <p className="muted small" style={{ marginBottom: '0.5rem' }}>
                      {t('goals.archivedLabel')}
                    </p>
                  )}
                  <p className="muted small capitalize">{p?.sphere ?? goal.sphere}</p>
                  {goal.deadline && (
                    <p className="muted small">
                      {t('goals.deadline')}: {goal.deadline}
                      {daysLeft != null && daysLeft <= 14 && daysLeft >= 0 && (
                        <span className="goal-deadline-near">
                          {' '}
                          — {t('goals.daysLeft', { count: daysLeft })}
                        </span>
                      )}
                      {daysLeft != null && daysLeft < 0 && (
                        <span className="muted"> — {t('goals.pastDeadline')}</span>
                      )}
                    </p>
                  )}
                  {pct != null ? (
                    <>
                      <div className="progress-bar-wrap">
                        <div
                          className={`progress-bar-fill ${barClass}`}
                          style={{ width: `${Math.min(100, pct)}%` }}
                        />
                      </div>
                      <p className="metric">{pct.toFixed(0)}%</p>
                      {p.current_value != null && p.target_value != null && (
                        <p className="muted">
                          {p.current_value.toFixed(1)} / {p.target_value}
                          {p.target_metric ? ` ${p.target_metric}` : ''}
                        </p>
                      )}
                    </>
                  ) : (
                    <p className="muted">
                      {p?.current_value != null
                        ? t('dashboard.currentValueTarget', {
                            current: p.current_value.toFixed(1),
                          })
                        : t('dashboard.addEntriesToProgress')}
                    </p>
                  )}
                </div>
              )
            })}
          </section>
        </>
      )}

      {editingGoal && (
        <EditGoalModal
          goal={editingGoal}
          progress={progressByGoalId[editingGoal.id]}
          onClose={() => setEditingGoal(null)}
          onSaved={refreshGoals}
          onDelete={(g) => {
            handleDelete(g)
            setEditingGoal(null)
          }}
        />
      )}
    </div>
  )
}
