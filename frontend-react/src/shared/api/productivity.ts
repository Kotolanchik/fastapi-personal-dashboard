import api from './client'

export type ProductivityTask = {
  id: number
  user_id: number
  title: string
  status: string
  due_at: string | null
  completed_at: string | null
  created_at: string
}

export const listProductivityTasks = (status?: string) =>
  api
    .get<ProductivityTask[]>('/productivity/tasks', { params: status ? { status } : undefined })
    .then((res) => res.data)

export const getProductivityTask = (taskId: number) =>
  api.get<ProductivityTask>(`/productivity/tasks/${taskId}`).then((res) => res.data)

export const createProductivityTask = (payload: {
  title: string
  status?: string
  due_at?: string | null
}) => api.post<ProductivityTask>('/productivity/tasks', payload).then((res) => res.data)

export const updateProductivityTask = (
  taskId: number,
  payload: { title?: string; status?: string; due_at?: string | null },
) =>
  api.put<ProductivityTask>(`/productivity/tasks/${taskId}`, payload).then((res) => res.data)

export const deleteProductivityTask = (taskId: number) =>
  api.delete(`/productivity/tasks/${taskId}`).then((res) => res.data)

export type FocusSession = {
  id: number
  user_id: number
  recorded_at: string
  local_date: string
  duration_minutes: number
  session_type: string | null
  notes: string | null
}

export const listFocusSessions = (params?: { start_date?: string; end_date?: string; limit?: number }) =>
  api.get<FocusSession[]>('/productivity/sessions', { params }).then((res) => res.data)

export const createFocusSession = (payload: {
  recorded_at?: string | null
  timezone?: string
  duration_minutes: number
  session_type?: string | null
  notes?: string | null
}) => api.post<FocusSession>('/productivity/sessions', payload).then((res) => res.data)
