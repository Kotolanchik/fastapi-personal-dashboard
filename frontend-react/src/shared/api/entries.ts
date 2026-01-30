import api from './client'

export type BaseEntry = {
  id: number
  recorded_at: string
  local_date: string
  timezone: string
  user_id: number
}

export type HealthEntry = BaseEntry & {
  sleep_hours: number
  energy_level: number
  supplements?: string | null
  weight_kg?: number | null
  wellbeing: number
  notes?: string | null
}

export type FinanceEntry = BaseEntry & {
  income: number
  expense_food: number
  expense_transport: number
  expense_health: number
  expense_other: number
  notes?: string | null
}

export type ProductivityEntry = BaseEntry & {
  deep_work_hours: number
  tasks_completed: number
  focus_level: number
  notes?: string | null
}

export type LearningEntry = BaseEntry & {
  study_hours: number
  topics?: string | null
  projects?: string | null
  notes?: string | null
}

export const fetchEntries = <T>(resource: string) =>
  api.get<T[]>(`/${resource}`).then((res) => res.data)

export const createEntry = (resource: string, payload: Record<string, unknown>) =>
  api.post(`/${resource}`, payload).then((res) => res.data)

export const updateEntry = (
  resource: string,
  id: number,
  payload: Record<string, unknown>,
) => api.put(`/${resource}/${id}`, payload).then((res) => res.data)

export const deleteEntry = (resource: string, id: number) =>
  api.delete(`/${resource}/${id}`).then((res) => res.data)
