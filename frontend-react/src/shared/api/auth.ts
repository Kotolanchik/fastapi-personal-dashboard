import api from './client'

export type User = {
  id: number
  email: string
  full_name?: string | null
  default_timezone?: string | null
  role: string
  dashboard_settings?: { enabled_blocks?: string[]; order?: string[] } | null
  notification_email?: string | null
  notification_preferences?: { email_reminders?: boolean } | null
}

export type LoginResponse = {
  access_token: string
  token_type: string
}

export const registerUser = (payload: {
  email: string
  password: string
  full_name?: string | null
}) => api.post<User>('/auth/register', payload).then((res) => res.data)

export const loginUser = (payload: { email: string; password: string }) =>
  api.post<LoginResponse>('/auth/login', payload).then((res) => res.data)

export const getCurrentUser = () => api.get<User>('/auth/me').then((res) => res.data)

export const updateProfile = (payload: {
  full_name?: string | null
  default_timezone?: string | null
  dashboard_settings?: { enabled_blocks?: string[]; order?: string[] } | null
  notification_email?: string | null
  notification_preferences?: { email_reminders?: boolean } | null
}) => api.patch<User>('/auth/me', payload).then((res) => res.data)

export const changePassword = (payload: {
  current_password: string
  new_password: string
}) => api.post('/auth/change-password', payload)
