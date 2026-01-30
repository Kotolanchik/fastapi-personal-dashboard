import api from './client'

export type DataSource = {
  id: number
  provider: string
  status: string
  last_synced_at?: string | null
  created_at: string
  updated_at: string
}

export type SyncJob = {
  id: number
  provider: string
  status: string
  started_at?: string | null
  finished_at?: string | null
  message?: string | null
  stats?: Record<string, unknown> | null
  created_at: string
}

export const listProviders = () =>
  api.get<{ providers: string[] }>('/integrations/providers').then((res) => res.data)

export const listSources = () =>
  api.get<DataSource[]>('/integrations').then((res) => res.data)

export const connectSource = (payload: {
  provider: string
  access_token?: string | null
  refresh_token?: string | null
}) => api.post<DataSource>('/integrations', payload).then((res) => res.data)

export const syncProvider = (provider: string) =>
  api.post<SyncJob>(`/integrations/${provider}/sync`).then((res) => res.data)

export const listSyncJobs = () =>
  api.get<SyncJob[]>('/integrations/sync-jobs').then((res) => res.data)
