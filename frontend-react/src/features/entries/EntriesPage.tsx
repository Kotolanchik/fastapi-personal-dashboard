import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { createEntry, deleteEntry, fetchEntries, updateEntry } from '../../shared/api/entries'

type FieldConfig = {
  name: string
  label: string
  type: 'number' | 'int' | 'text'
  min?: number
  max?: number
  step?: number
  optional?: boolean
}

type EntriesPageProps = {
  title: string
  resource: string
  fields: FieldConfig[]
}

export const EntriesPage = ({ title, resource, fields }: EntriesPageProps) => {
  const queryClient = useQueryClient()
  const { data = [] } = useQuery({
    queryKey: [resource],
    queryFn: () => fetchEntries<Record<string, unknown>>(resource),
  })

  const [editing, setEditing] = useState<Record<string, unknown> | null>(null)
  const [date, setDate] = useState('')
  const [time, setTime] = useState('08:00')
  const [timezone, setTimezone] = useState('UTC')
  const [form, setForm] = useState<Record<string, string>>({})

  const resetForm = () => {
    setEditing(null)
    setDate('')
    setTime('08:00')
    setTimezone('UTC')
    setForm({})
  }

  const mutation = useMutation({
    mutationFn: (payload: { id?: number; body: Record<string, unknown> }) => {
      if (payload.id) {
        return updateEntry(resource, payload.id, payload.body)
      }
      return createEntry(resource, payload.body)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [resource] })
      resetForm()
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
        <h3>{editing ? 'Обновить запись' : `Новая запись: ${title}`}</h3>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Дата
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
          </label>
          <label>
            Время
            <input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
          </label>
          <label>
            Таймзона
            <input value={timezone} onChange={(e) => setTimezone(e.target.value)} />
          </label>
          {fields.map((field) => (
            <label key={field.name}>
              {field.label}
              <input
                type={field.type === 'text' ? 'text' : 'number'}
                min={field.min}
                max={field.max}
                step={field.step ?? (field.type === 'int' ? 1 : 0.1)}
                value={form[field.name] ?? ''}
                onChange={(e) => setForm((prev) => ({ ...prev, [field.name]: e.target.value }))}
              />
            </label>
          ))}
          <div className="form-actions">
            <button type="submit" disabled={mutation.isPending}>
              {editing ? 'Сохранить' : 'Добавить'}
            </button>
            {editing ? (
              <button type="button" className="secondary" onClick={resetForm}>
                Отмена
              </button>
            ) : null}
          </div>
        </form>
      </div>

      <div className="card">
        <h3>Записи</h3>
        {data.length ? (
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.map((entry) => (
                <tr key={entry.id as number}>
                  {columns.map((column) => (
                    <td key={column}>{String(entry[column] ?? '')}</td>
                  ))}
                  <td className="actions">
                    <button onClick={() => startEdit(entry)}>Edit</button>
                    <button
                      className="danger"
                      onClick={() => deleteMutation.mutate(entry.id as number)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">Записей пока нет.</p>
        )}
      </div>
    </div>
  )
}
