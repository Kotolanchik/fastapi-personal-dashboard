import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createEntry, deleteEntry, fetchEntries, updateEntry } from '../../shared/api/entries'
import { useToast } from '../../shared/components/Toast'
import { usePageTitle } from '../../shared/hooks/usePageTitle'
import { parseValidationErrors } from '../../shared/utils/validation'

type SelectOption = { value: string; label: string }

type FieldConfig = {
  name: string
  label: string
  type: 'number' | 'int' | 'text' | 'select' | 'multiselect'
  min?: number
  max?: number
  step?: number
  optional?: boolean
  /** For type 'select' / 'multiselect': list of options. */
  options?: SelectOption[]
  /** For type 'select': submit value as number (e.g. course_id). For 'multiselect': 'number[]'. */
  valueType?: 'string' | 'number' | 'number[]'
}

type EntriesPageProps = {
  title: string
  resource: string
  fields: FieldConfig[]
  /** Optional initial date (YYYY-MM-DD) e.g. from /health?date=... */
  initialDate?: string
}

export const EntriesPage = ({ title, resource, fields, initialDate }: EntriesPageProps) => {
  usePageTitle(title)
  const queryClient = useQueryClient()
  const toast = useToast()
  const { data = [], isLoading } = useQuery({
    queryKey: [resource],
    queryFn: () => fetchEntries<Record<string, unknown>>(resource),
  })

  const [editing, setEditing] = useState<Record<string, unknown> | null>(null)
  const [date, setDate] = useState('')
  useEffect(() => {
    if (initialDate) setDate(initialDate)
  }, [initialDate])
  const [time, setTime] = useState('08:00')
  const [timezone, setTimezone] = useState('UTC')
  const [form, setForm] = useState<Record<string, string>>({})
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const resetForm = () => {
    setEditing(null)
    setDate('')
    setTime('08:00')
    setTimezone('UTC')
    setForm({})
    setFieldErrors({})
  }

  const mutation = useMutation({
    mutationFn: (payload: { id?: number; body: Record<string, unknown> }) => {
      if (payload.id) {
        return updateEntry(resource, payload.id, payload.body)
      }
      return createEntry(resource, payload.body)
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: [resource] })
      resetForm()
      toast.success(variables.id ? t('entries.saved') : t('entries.added'))
    },
    onError: (err) => {
      setFieldErrors(parseValidationErrors(err))
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteEntry(resource, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: [resource] }),
  })

  const startEdit = (entry: Record<string, unknown>) => {
    setEditing(entry)
    const recordedAt = (entry.recorded_at as string) || ''
    if (recordedAt) {
      const dateObj = new Date(recordedAt)
      setDate(dateObj.toISOString().slice(0, 10))
      setTime(dateObj.toISOString().slice(11, 16))
    } else {
      setDate(entry.local_date as string)
    }
    setTimezone((entry.timezone as string) || 'UTC')
    const nextForm: Record<string, string> = {}
    fields.forEach((field) => {
      const value = entry[field.name]
      if (field.type === 'multiselect' && Array.isArray(value)) {
        nextForm[field.name] = value.map(String).join(',')
        return
      }
      nextForm[field.name] = value === null || value === undefined ? '' : String(value)
    })
    setForm(nextForm)
  }

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const payload: Record<string, unknown> = {
      timezone,
    }
    if (date) {
      const recorded = time ? `${date}T${time}:00` : `${date}T00:00:00`
      payload.recorded_at = new Date(recorded).toISOString()
    }

    fields.forEach((field) => {
      const rawValue = form[field.name]
      if (field.type === 'multiselect') {
        const ids = rawValue
          ? rawValue.split(',').map((s) => Number.parseInt(s.trim(), 10)).filter((n) => !Number.isNaN(n))
          : []
        payload[field.name] = field.optional && ids.length === 0 ? null : ids
        return
      }
      if (field.type === 'select') {
        const value = rawValue || (field.options?.[0]?.value ?? null)
        if (!value && (field.optional || field.valueType === 'number')) {
          payload[field.name] = null
          return
        }
        if (field.valueType === 'number') {
          payload[field.name] = value ? Number.parseInt(value, 10) : null
        } else {
          payload[field.name] = value
        }
        return
      }
      if (field.type === 'text') {
        payload[field.name] = rawValue || null
        return
      }
      if (!rawValue && field.optional) {
        payload[field.name] = null
        return
      }
      if (field.type === 'int') {
        payload[field.name] = rawValue ? Number.parseInt(rawValue, 10) : 0
      } else {
        payload[field.name] = rawValue ? Number.parseFloat(rawValue) : 0
      }
    })

    mutation.mutate({ id: editing?.id as number | undefined, body: payload })
  }

  const columns = useMemo(() => {
    return ['id', 'local_date', ...fields.map((field) => field.name)]
  }, [fields])

  return (
    <div className="stack">
      <div className="card">
        <h3>{editing ? 'Update entry' : `New entry: ${title}`}</h3>
        <form id="entry-form" onSubmit={handleSubmit} className="form-grid">
          <label>
            Date
            <input
              type="date"
              value={date}
              onChange={(e) => {
                setDate(e.target.value)
                setFieldErrors((prev) => ({ ...prev, recorded_at: '' }))
              }}
              required
              aria-invalid={!!fieldErrors.recorded_at}
            />
            {fieldErrors.recorded_at ? <div className="field-error">{fieldErrors.recorded_at}</div> : null}
          </label>
          <label>
            {t('entries.time')}
            <input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
          </label>
          <label>
            {t('entries.timezone')}
            <input
              value={timezone}
              onChange={(e) => {
                setTimezone(e.target.value)
                setFieldErrors((prev) => ({ ...prev, timezone: '' }))
              }}
              aria-invalid={!!fieldErrors.timezone}
            />
            {fieldErrors.timezone ? <div className="field-error">{fieldErrors.timezone}</div> : null}
          </label>
          {fields.map((field) =>
            field.type === 'multiselect' ? (
              <div key={field.name} className="form-group">
                <span className="label">{field.label}</span>
                <div className="checkbox-group">
                  {(field.options ?? []).map((opt) => {
                    const selected = (form[field.name] ?? '').split(',').map((s) => s.trim()).includes(opt.value)
                    return (
                      <label key={opt.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={(e) => {
                            const current = (form[field.name] ?? '').split(',').map((s) => s.trim()).filter(Boolean)
                            const next = e.target.checked
                              ? [...current, opt.value]
                              : current.filter((v) => v !== opt.value)
                            setForm((prev) => ({ ...prev, [field.name]: next.join(',') }))
                            setFieldErrors((prev) => ({ ...prev, [field.name]: '' }))
                          }}
                        />
                        {opt.label}
                      </label>
                    )
                  })}
                </div>
                {fieldErrors[field.name] ? <div className="field-error">{fieldErrors[field.name]}</div> : null}
              </div>
            ) : field.type === 'select' ? (
              <label key={field.name}>
                {field.label}
                <select
                  value={form[field.name] ?? ''}
                  onChange={(e) => {
                    setForm((prev) => ({ ...prev, [field.name]: e.target.value }))
                    setFieldErrors((prev) => ({ ...prev, [field.name]: '' }))
                  }}
                  aria-invalid={!!fieldErrors[field.name]}
                >
                  <option value="">{t('common.select')}</option>
                  {(field.options ?? []).map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                {fieldErrors[field.name] ? <div className="field-error">{fieldErrors[field.name]}</div> : null}
              </label>
            ) : (
              <label key={field.name}>
                {field.label}
                <input
                  type={field.type === 'text' ? 'text' : 'number'}
                  min={field.min}
                  max={field.max}
                  step={field.step ?? (field.type === 'int' ? 1 : 0.1)}
                  value={form[field.name] ?? ''}
                  onChange={(e) => {
                    setForm((prev) => ({ ...prev, [field.name]: e.target.value }))
                    setFieldErrors((prev) => ({ ...prev, [field.name]: '' }))
                  }}
                  aria-invalid={!!fieldErrors[field.name]}
                />
                {fieldErrors[field.name] ? <div className="field-error">{fieldErrors[field.name]}</div> : null}
              </label>
            ),
          )}
          <div className="form-actions">
            <button type="submit" disabled={mutation.isPending}>
              {editing ? t('common.save') : t('common.add')}
            </button>
            {editing ? (
              <button type="button" className="secondary" onClick={resetForm}>
                {t('entries.cancel')}
              </button>
            ) : null}
          </div>
        </form>
      </div>

      <div className="card">
        <h3>{t('entries.entriesList')}</h3>
        {isLoading ? (
          <div className="skeleton-list" aria-busy="true">
            <div className="skeleton-row" />
            <div className="skeleton-row" />
            <div className="skeleton-row" />
            <div className="skeleton-row" />
            <div className="skeleton-row" />
          </div>
        ) : data.length ? (
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
                <th>{t('entries.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.id as number}>
                  {columns.map((column) => (
                    <td key={column}>{String(entry[column] ?? '')}</td>
                  ))}
                  <td className="actions">
                    <button onClick={() => startEdit(entry)}>{t('entries.editEntry')}</button>
                    <button
                      className="danger"
                      onClick={() => deleteMutation.mutate(entry.id as number)}
                    >
                      {t('entries.delete')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <p className="empty-state-text">{t('entries.noEntriesYet')}</p>
            <p className="muted">{t('entries.addFirstHint')}</p>
            <a href="#entry-form" className="empty-state-cta">
              {t('entries.addFirstEntry')}
            </a>
          </div>
        )}
      </div>
    </div>
  )
}
