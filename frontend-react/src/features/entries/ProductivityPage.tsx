import { useCallback, useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createFocusSession,
  createProductivityTask,
  deleteProductivityTask,
  listFocusSessions,
  listProductivityTasks,
  updateProductivityTask,
  type ProductivityTask,
} from '../../shared/api/productivity'
import { EntriesPage } from './EntriesPage'
import { useToast } from '../../shared/components/Toast'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

const FOCUS_CATEGORY_OPTIONS = [
  { value: 'code', label: 'Code' },
  { value: 'writing', label: 'Writing' },
  { value: 'meetings', label: 'Meetings' },
  { value: 'other', label: 'Other' },
]

const SESSION_TYPE_OPTIONS = [
  { value: 'pomodoro', label: 'Pomodoro' },
  { value: 'deep_work', label: 'Deep work' },
]

const TASK_STATUS_OPTIONS = [
  { value: 'open', label: 'Open' },
  { value: 'done', label: 'Done' },
  { value: 'cancelled', label: 'Cancelled' },
]

export const ProductivityPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.productivity'))
  const toast = useToast()
  const queryClient = useQueryClient()
  const [taskTitle, setTaskTitle] = useState('')
  const [taskDueAt, setTaskDueAt] = useState('')
  const [sessionDuration, setSessionDuration] = useState(25)
  const [sessionType, setSessionType] = useState('pomodoro')
  const [timerSeconds, setTimerSeconds] = useState(25 * 60)
  const [timerRunning, setTimerRunning] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!timerRunning) return
    timerRef.current = setInterval(() => {
      setTimerSeconds((s) => (s <= 0 ? 0 : s - 1))
    }, 1000)
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [timerRunning])

  const startPomodoro = useCallback(() => {
    setTimerSeconds(sessionDuration * 60)
    setTimerRunning(true)
  }, [sessionDuration])
  const finishPomodoroSession = useCallback(() => {
    const elapsedMin = Math.ceil((sessionDuration * 60 - timerSeconds) / 60) || sessionDuration
    addSession.mutate(
      {
        duration_minutes: elapsedMin,
        session_type: 'pomodoro',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
      {
        onSuccess: () => {
          setTimerRunning(false)
          setTimerSeconds(sessionDuration * 60)
        },
      },
    )
  }, [sessionDuration, timerSeconds, addSession])

  const tasks = useQuery({
    queryKey: ['productivity', 'tasks'],
    queryFn: () => listProductivityTasks(),
  })
  const sessions = useQuery({
    queryKey: ['productivity', 'sessions'],
    queryFn: () => listFocusSessions({ limit: 50 }),
  })

  const createTask = useMutation({
    mutationFn: createProductivityTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productivity', 'tasks'] })
      setTaskTitle('')
      setTaskDueAt('')
      toast.success(t('productivity.taskAdded'))
    },
  })
  const updateTask = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { status?: string } }) =>
      updateProductivityTask(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['productivity', 'tasks'] }),
  })
  const deleteTask = useMutation({
    mutationFn: deleteProductivityTask,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['productivity', 'tasks'] }),
  })
  const addSession = useMutation({
    mutationFn: createFocusSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productivity', 'sessions'] })
      toast.success(t('productivity.sessionAdded'))
    },
  })

  const openTasks = tasks.data?.filter((t) => t.status === 'open') ?? []
  const doneTasks = tasks.data?.filter((t) => t.status === 'done') ?? []
  const taskOptionsForEntry = (tasks.data ?? [])
    .filter((t) => t.status === 'open' || t.status === 'done')
    .map((t) => ({ value: String(t.id), label: t.title }))

  const timerMin = Math.floor(timerSeconds / 60)
  const timerSec = timerSeconds % 60

  return (
    <div className="stack">
      <section className="card">
        <h3>{t('productivity.pomodoroTimer')}</h3>
        <p className="muted">{t('productivity.pomodoroTimerHint')}</p>
        <div className="form-grid" style={{ alignItems: 'center', marginBottom: '0.5rem' }}>
          <span className="metric" style={{ fontSize: '1.5rem' }}>
            {String(timerMin).padStart(2, '0')}:{String(timerSec).padStart(2, '0')}
          </span>
          {!timerRunning ? (
            <button type="button" onClick={startPomodoro}>
              {t('productivity.startTimer')}
            </button>
          ) : (
            <>
              <button type="button" className="secondary" onClick={() => setTimerRunning(false)}>
                {t('productivity.pauseTimer')}
              </button>
              <button type="button" onClick={() => finishPomodoroSession()} disabled={addSession.isPending}>
                {t('productivity.finishSession')}
              </button>
            </>
          )}
        </div>
      </section>
      <section className="card">
        <h3>{t('productivity.tasks')}</h3>
        <p className="muted">{t('productivity.tasksHint')}</p>
        <div className="form-grid" style={{ marginBottom: '1rem' }}>
          <label>
            {t('productivity.taskTitle')}
            <input
              type="text"
              value={taskTitle}
              onChange={(e) => setTaskTitle(e.target.value)}
              placeholder={t('productivity.taskTitlePlaceholder')}
            />
          </label>
          <label>
            {t('productivity.dueAt')}
            <input
              type="date"
              value={taskDueAt}
              onChange={(e) => setTaskDueAt(e.target.value)}
            />
          </label>
          <button
            type="button"
            onClick={() => {
              if (!taskTitle.trim()) return
              createTask.mutate({
                title: taskTitle.trim(),
                due_at: taskDueAt || undefined,
              })
            }}
            disabled={!taskTitle.trim() || createTask.isPending}
          >
            {t('common.add')}
          </button>
        </div>
        {tasks.data && tasks.data.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>{t('productivity.taskTitle')}</th>
                <th>{t('billing.status')}</th>
                <th>{t('productivity.dueAt')}</th>
                <th>{t('entries.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {[...openTasks, ...doneTasks].map((task: ProductivityTask) => (
                <tr key={task.id}>
                  <td>{task.title}</td>
                  <td>{task.status}</td>
                  <td>{task.due_at ? new Date(task.due_at).toLocaleDateString() : '—'}</td>
                  <td className="actions">
                    {task.status === 'open' && (
                      <button
                        type="button"
                        onClick={() => updateTask.mutate({ id: task.id, payload: { status: 'done' } })}
                        disabled={updateTask.isPending}
                      >
                        {t('productivity.markDone')}
                      </button>
                    )}
                    <button
                      type="button"
                      className="danger"
                      onClick={() => deleteTask.mutate(task.id)}
                    >
                      {t('common.remove')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">{t('productivity.noTasksYet')}</p>
        )}
      </section>

      <section className="card">
        <h3>{t('productivity.focusSessions')}</h3>
        <p className="muted">{t('productivity.focusSessionsHint')}</p>
        <div className="form-grid" style={{ marginBottom: '1rem' }}>
          <label>
            {t('productivity.durationMinutes')}
            <input
              type="number"
              min={1}
              max={480}
              value={sessionDuration}
              onChange={(e) => setSessionDuration(Number(e.target.value) || 25)}
            />
          </label>
          <label>
            {t('productivity.sessionType')}
            <select value={sessionType} onChange={(e) => setSessionType(e.target.value)}>
              {SESSION_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() =>
              addSession.mutate({
                duration_minutes: sessionDuration,
                session_type: sessionType,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
              })
            }
            disabled={addSession.isPending}
          >
            {t('productivity.addSession')}
          </button>
        </div>
        {sessions.data && sessions.data.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>{t('productivity.localDate')}</th>
                <th>{t('productivity.durationMinutes')}</th>
                <th>{t('productivity.sessionType')}</th>
              </tr>
            </thead>
            <tbody>
              {sessions.data.slice(0, 20).map((s) => (
                <tr key={s.id}>
                  <td>{s.local_date}</td>
                  <td>{s.duration_minutes} min</td>
                  <td>{s.session_type ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">{t('productivity.noSessionsYet')}</p>
        )}
      </section>

      <EntriesPage
        title={t('nav.productivity')}
        resource="productivity"
        fields={[
          { name: 'deep_work_hours', label: t('entries.labels.productivity.deep_work_hours'), type: 'number', min: 0, max: 24 },
          { name: 'tasks_completed', label: t('entries.labels.productivity.tasks_completed'), type: 'int', min: 0 },
          { name: 'completed_task_ids', label: t('productivity.completedTasks'), type: 'multiselect', options: taskOptionsForEntry, optional: true, valueType: 'number[]' },
          { name: 'focus_level', label: t('entries.labels.productivity.focus_level'), type: 'int', min: 1, max: 10 },
          { name: 'focus_category', label: t('entries.labels.productivity.focus_category'), type: 'select', options: FOCUS_CATEGORY_OPTIONS, optional: true },
          { name: 'notes', label: t('entries.labels.productivity.notes'), type: 'text', optional: true },
        ]}
      />
    </div>
  )
}
