import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchEntries } from '../../shared/api/entries'
import type { LearningEntry } from '../../shared/api/entries'
import {
  createLearningCourse,
  deleteLearningCourse,
  getLearningStreak,
  listLearningCourses,
  updateLearningCourse,
  type LearningCourse,
} from '../../shared/api/learning'
import { EntriesPage } from './EntriesPage'
import { useToast } from '../../shared/components/Toast'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

const SOURCE_TYPE_OPTIONS = [
  { value: 'book', label: 'Book' },
  { value: 'course', label: 'Course' },
  { value: 'podcast', label: 'Podcast' },
  { value: 'other', label: 'Other' },
]

const COURSE_KIND_OPTIONS = [
  { value: '', label: '—' },
  { value: 'course', label: 'Course' },
  { value: 'book', label: 'Book' },
  { value: 'topic', label: 'Topic' },
]

export const LearningPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.learning'))
  const toast = useToast()
  const queryClient = useQueryClient()
  const [newTitle, setNewTitle] = useState('')
  const [newKind, setNewKind] = useState('')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editKind, setEditKind] = useState('')

  const { data: courses = [] } = useQuery({
    queryKey: ['learning', 'courses'],
    queryFn: listLearningCourses,
  })
  const streakQuery = useQuery({
    queryKey: ['learning', 'streak'],
    queryFn: getLearningStreak,
  })
  const entriesQuery = useQuery({
    queryKey: ['learning'],
    queryFn: () => fetchEntries<LearningEntry>('learning', { limit: 100 }),
  })
  const byDate = (entriesQuery.data ?? []).reduce<Record<string, { hours: number; count: number }>>((acc, e) => {
    const d = e.local_date
    if (!acc[d]) acc[d] = { hours: 0, count: 0 }
    acc[d].hours += e.study_hours
    acc[d].count += 1
    return acc
  }, {})
  const sortedDates = Object.keys(byDate).sort().reverse().slice(0, 14)
  const courseOptions = courses.map((c) => ({ value: String(c.id), label: c.title }))
  const fields = [
    { name: 'study_hours', label: t('entries.labels.learning.study_hours'), type: 'number' as const, min: 0, max: 24 },
    { name: 'topics', label: t('entries.labels.learning.topics'), type: 'text' as const, optional: true },
    { name: 'projects', label: t('entries.labels.learning.projects'), type: 'text' as const, optional: true },
    { name: 'course_id', label: t('entries.labels.learning.course'), type: 'select' as const, options: courseOptions, optional: true, valueType: 'number' as const },
    { name: 'source_type', label: t('entries.labels.learning.source_type'), type: 'select' as const, options: SOURCE_TYPE_OPTIONS, optional: true },
    { name: 'notes', label: t('entries.labels.learning.notes'), type: 'text' as const, optional: true },
  ]

  const createCourse = useMutation({
    mutationFn: (payload: { title: string; kind?: string | null }) => createLearningCourse(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning', 'courses'] })
      setNewTitle('')
      setNewKind('')
      toast.success(t('learning.courseAdded'))
    },
  })
  const updateCourse = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number
      payload: { title?: string; kind?: string | null; completed_at?: string | null }
    }) => updateLearningCourse(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning', 'courses'] })
      queryClient.invalidateQueries({ queryKey: ['goals'] })
      setEditingId(null)
      toast.success(t('learning.courseUpdated'))
    },
  })
  const deleteCourse = useMutation({
    mutationFn: deleteLearningCourse,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['learning', 'courses'] }),
  })

  const startEdit = (c: LearningCourse) => {
    setEditingId(c.id)
    setEditTitle(c.title)
    setEditKind(c.kind ?? '')
  }

  const streak = streakQuery.data

  return (
    <div className="stack">
      {streak && (
        <section className="card">
          <h3>{t('learning.streak')}</h3>
          <p className="muted">
            {t('learning.streakDays', { count: streak.current_streak_days })}
            {streak.last_activity_date != null && (
              <> · {t('learning.lastActivity')}: {streak.last_activity_date}</>
            )}
          </p>
        </section>
      )}
      {sortedDates.length > 0 && (
        <section className="card">
          <h3>{t('learning.byDate')}</h3>
          <p className="muted">{t('learning.byDateHint')}</p>
          <table>
            <thead>
              <tr>
                <th>{t('entries.date')}</th>
                <th>{t('entries.labels.learning.study_hours')}</th>
                <th>{t('learning.entriesCount')}</th>
              </tr>
            </thead>
            <tbody>
              {sortedDates.map((d) => (
                <tr key={d}>
                  <td>{d}</td>
                  <td>{byDate[d].hours.toFixed(1)}</td>
                  <td>{byDate[d].count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
      <section className="card">
        <h3>{t('learning.myCourses')}</h3>
        <p className="muted">{t('learning.myCoursesHint')}</p>
        <div className="form-grid" style={{ marginBottom: '1rem' }}>
          <label>
            {t('learning.courseTitle')}
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder={t('learning.courseTitlePlaceholder')}
            />
          </label>
          <label>
            {t('learning.kind')}
            <select value={newKind} onChange={(e) => setNewKind(e.target.value)}>
              {COURSE_KIND_OPTIONS.map((opt) => (
                <option key={opt.value || 'empty'} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={() => {
              if (!newTitle.trim()) return
              createCourse.mutate({ title: newTitle.trim(), kind: newKind || null })
            }}
            disabled={!newTitle.trim() || createCourse.isPending}
          >
            {t('common.add')}
          </button>
        </div>
        {courses.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>{t('learning.courseTitle')}</th>
                <th>{t('learning.kind')}</th>
                <th>{t('learning.status')}</th>
                <th>{t('entries.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((c) =>
                editingId === c.id ? (
                  <tr key={c.id}>
                    <td>
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        size={30}
                      />
                    </td>
                    <td>
                      <select value={editKind} onChange={(e) => setEditKind(e.target.value)}>
                        {COURSE_KIND_OPTIONS.map((opt) => (
                          <option key={opt.value || 'e'} value={opt.value}>
                            {opt.label}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>{c.completed_at ? t('learning.completed') : '—'}</td>
                    <td className="actions">
                      <button
                        type="button"
                        onClick={() =>
                          updateCourse.mutate({
                            id: c.id,
                            payload: { title: editTitle.trim() || undefined, kind: editKind || null },
                          })
                        }
                        disabled={updateCourse.isPending}
                      >
                        {t('common.save')}
                      </button>
                      <button type="button" className="secondary" onClick={() => setEditingId(null)}>
                        {t('entries.cancel')}
                      </button>
                    </td>
                  </tr>
                ) : (
                  <tr key={c.id}>
                    <td>{c.title}</td>
                    <td>{c.kind ?? '—'}</td>
                    <td>
                      {c.completed_at ? (
                        <span className="muted">{t('learning.completed')}</span>
                      ) : (
                        <button
                          type="button"
                          className="secondary small"
                          onClick={() =>
                            updateCourse.mutate({
                              id: c.id,
                              payload: { completed_at: new Date().toISOString() },
                            })
                          }
                          disabled={updateCourse.isPending}
                        >
                          {t('learning.markComplete')}
                        </button>
                      )}
                      {c.completed_at && (
                        <button
                          type="button"
                          className="secondary small"
                          style={{ marginLeft: '0.25rem' }}
                          onClick={() =>
                            updateCourse.mutate({
                              id: c.id,
                              payload: { completed_at: null },
                            })
                          }
                          disabled={updateCourse.isPending}
                        >
                          {t('learning.markIncomplete')}
                        </button>
                      )}
                    </td>
                    <td className="actions">
                      <button type="button" onClick={() => startEdit(c)}>
                        {t('common.edit')}
                      </button>
                      <button
                        type="button"
                        className="danger"
                        onClick={() => deleteCourse.mutate(c.id)}
                      >
                        {t('common.remove')}
                      </button>
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        ) : (
          <p className="muted">{t('learning.noCoursesYet')}</p>
        )}
      </section>

      <EntriesPage title={t('nav.learning')} resource="learning" fields={fields} />
    </div>
  )
}
