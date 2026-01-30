import api from './client'

export type DataSource = {
  id: number
  user_id?: number
  provider: string
  status: string
  last_synced_at?: string | null
  last_error?: string | null
  sync_settings?: Record<string, unknown> | null
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

export const updateSource = (
  sourceId: number,
  payload: { sync_settings?: Record<string, unknown> | null; status?: string },
) =>
  api.put<DataSource>(`/integrations/${sourceId}`, payload).then((res) => res.data)

export const connectSource = (payload: {
  provider: string
  access_token?: string | null
  refresh_token?: string | null
}) => api.post<DataSource>('/integrations', payload).then((res) => res.data)

export const syncProvider = (provider: string) =>
  api.post<SyncJob>(`/integrations/${provider}/sync`).then((res) => res.data)

export const listSyncJobs = () =>
  api.get<SyncJob[]>('/integrations/sync-jobs').then((res) => res.data)

export type SourceStatusResponse = {
  source: DataSource
  last_job: SyncJob | null
  last_error: string | null
}

export const getSourceStatus = (sourceId: number) =>
  api
    .get<SourceStatusResponse>(`/integrations/sources/${sourceId}/status`)
    .then((res) => res.data)

export const getGoogleFitOAuthUrl = () =>
  api.get<{ url: string }>('/integrations/google_fit/oauth-url').then((res) => res.data)

export const postGoogleFitOAuthCallback = (code: string) =>
  api
    .post<DataSource>('/integrations/google_fit/oauth-callback', { code })
    .then((res) => res.data)

export type AppleHealthImportResponse = {
  status: string
  message?: string
  stats?: Record<string, unknown>
}

export const postAppleHealthImport = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api
    .post<AppleHealthImportResponse>('/integrations/apple-health/import', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((res) => res.data)
}
