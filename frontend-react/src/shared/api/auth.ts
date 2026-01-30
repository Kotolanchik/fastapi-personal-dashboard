import api from './client'

export type User = {
  id: number
  email: string
  full_name?: string | null
  role: string
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
