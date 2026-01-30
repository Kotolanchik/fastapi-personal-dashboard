import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Fragment, useState } from 'react'
import { useTranslation } from 'react-i18next'

import {
  connectSource,
  getGoogleFitOAuthUrl,
  listProviders,
  listSources,
  listSyncJobs,
  postAppleHealthImport,
  syncProvider,
  updateSource,
} from '../../shared/api/integrations'
import type { DataSource } from '../../shared/api/integrations'
import { usePageTitle } from '../../shared/hooks/usePageTitle'
import { useToast } from '../../shared/components/Toast'

export const IntegrationsPage = () => {
  const { t } = useTranslation()
  const toast = useToast()
  usePageTitle(t('nav.integrations'))
  const queryClient = useQueryClient()
  const [provider, setProvider] = useState('')
  const [accessToken, setAccessToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('')
  const [appleFile, setAppleFile] = useState<File | null>(null)
  const [editingSyncSettings, setEditingSyncSettings] = useState<number | null>(null)
  const [syncSettingsJson, setSyncSettingsJson] = useState('')

  const providers = useQuery({ queryKey: ['providers'], queryFn: listProviders })
  const sources = useQuery({ queryKey: ['sources'], queryFn: listSources })
  const jobs = useQuery({ queryKey: ['syncJobs'], queryFn: listSyncJobs })

  const connectMutation = useMutation({
    mutationFn: () =>
      connectSource({
        provider,
        access_token: accessToken || undefined,
        refresh_token: refreshToken || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const syncMutation = useMutation({
    mutationFn: (name: string) => syncProvider(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['syncJobs'] })
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      toast.success(t('integrations.syncStarted'))
    },
    onError: () => toast.error(t('integrations.syncError')),
  })

  const googleFitMutation = useMutation({
    mutationFn: getGoogleFitOAuthUrl,
    onSuccess: (data) => {
      window.location.href = data.url
    },
    onError: () => toast.error(t('integrations.googleFitNotConfigured')),
  })

  const appleImportMutation = useMutation({
    mutationFn: (file: File) => postAppleHealthImport(file),
    onSuccess: (data) => {
      toast.success(
        t('integrations.importSuccess', {
          count: (data.stats as { imported_records?: number })?.imported_records ?? data.message ?? '',
        }),
      )
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      setAppleFile(null)
    },
    onError: (err: Error & { response?: { data?: { detail?: string } } }) => {
      toast.error(err.response?.data?.detail ?? err.message ?? t('integrations.importError'))
    },
  })

  const updateSettingsMutation = useMutation({
    mutationFn: ({ sourceId, sync_settings }: { sourceId: number; sync_settings: Record<string, unknown> | null }) =>
      updateSource(sourceId, { sync_settings }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      setEditingSyncSettings(null)
      setSyncSettingsJson('')
      toast.success(t('integrations.syncSettingsSaved'))
    },
    onError: () => toast.error(t('integrations.syncSettingsError')),
  })

  const providerOptions = providers.data?.providers ?? []

  const startEditSyncSettings = (source: DataSource) => {
    setEditingSyncSettings(source.id)
    setSyncSettingsJson(
      source.sync_settings ? JSON.stringify(source.sync_settings, null, 2) : '{\n  "health": ["steps", "sleep"],\n  "finance": ["*"]\n}',
    )
  }

  const saveSyncSettings = (sourceId: number) => {
    let parsed: Record<string, unknown> | null = null
    try {
      if (syncSettingsJson.trim()) parsed = JSON.parse(syncSettingsJson) as Record<string, unknown>
    } catch {
      toast.error(t('integrations.syncSettingsInvalidJson'))
      return
    }
    updateSettingsMutation.mutate({ sourceId, sync_settings: parsed })
  }

  if (sources.isLoading || providers.isLoading) {
    return (
      <div className="stack">
        <div className="card skeleton-card">
          <div className="skeleton list-skeleton" />
        </div>
        <div className="card skeleton-card">
          <div className="skeleton list-skeleton" style={{ height: 200 }} />
        </div>
      </div>
    )
  }

  return (
    <div className="stack">
      <div className="card banner muted" role="status">
        {t('integrations.banner')}
      </div>

      <div className="card">
        <h3>{t('integrations.connectGoogleFit')}</h3>
        <p className="muted">{t('integrations.connectGoogleFitHint')}</p>
        <button
          type="button"
          onClick={() => googleFitMutation.mutate()}
          disabled={googleFitMutation.isPending}
        >
          {googleFitMutation.isPending ? t('common.loading') : t('integrations.connectWithGoogleFit')}
        </button>
      </div>

      <div className="card">
        <h3>{t('integrations.uploadAppleHealth')}</h3>
        <p className="muted">{t('integrations.uploadAppleHealthHint')}</p>
        <div className="form-grid">
          <label>
            {t('integrations.selectFile')}
            <input
              type="file"
              accept=".xml,.zip"
              onChange={(e) => setAppleFile(e.target.files?.[0] ?? null)}
            />
          </label>
          <button
            type="button"
            onClick={() => appleFile && appleImportMutation.mutate(appleFile)}
            disabled={!appleFile || appleImportMutation.isPending}
          >
            {appleImportMutation.isPending ? t('common.loading') : t('integrations.upload')}
          </button>
        </div>
      </div>

      <div className="card">
        <h3>{t('integrations.connectIntegration')}</h3>
        <div className="form-grid">
          <label>
            {t('integrations.provider')}
            <select value={provider} onChange={(e) => setProvider(e.target.value)}>
              <option value="">{t('common.select')}</option>
              {providerOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('integrations.accessToken')}
            <input
              type="password"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
            />
          </label>
          <label>
            {t('integrations.refreshToken')}
            <input
              type="password"
              value={refreshToken}
              onChange={(e) => setRefreshToken(e.target.value)}
            />
          </label>
          <button
            onClick={() => connectMutation.mutate()}
            disabled={!provider || connectMutation.isPending}
          >
            {t('common.save')}
          </button>
        </div>
      </div>

      <div className="card">
        <h3>{t('integrations.dataSources')}</h3>
        {sources.data?.length ? (
          <div className="stack">
            <table>
              <thead>
                <tr>
                  <th>{t('integrations.provider')}</th>
                  <th>{t('billing.status')}</th>
                  <th>{t('integrations.lastSynced')}</th>
                  <th>{t('integrations.lastError')}</th>
                  <th>{t('integrations.action')}</th>
                </tr>
              </thead>
              <tbody>
                {sources.data.map((source) => (
                  <Fragment key={source.id}>
                    <tr>
                      <td>{source.provider}</td>
                      <td>{source.status}</td>
                      <td>{source.last_synced_at ? new Date(source.last_synced_at).toLocaleString() : '—'}</td>
                      <td>
                        {source.last_error ? (
                          <span className="field-error" title={source.last_error}>
                            {source.last_error.slice(0, 50)}
                            {source.last_error.length > 50 ? '…' : ''}
                          </span>
                        ) : (
                          '—'
                        )}
                      </td>
                      <td className="actions">
                        <button
                          onClick={() => syncMutation.mutate(source.provider)}
                          disabled={syncMutation.isPending}
                        >
                          {t('integrations.updateNow')}
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          onClick={() => startEditSyncSettings(source)}
                        >
                          {t('integrations.syncSettings')}
                        </button>
                      </td>
                    </tr>
                    {editingSyncSettings === source.id ? (
                      <tr>
                        <td colSpan={5}>
                          <div className="card muted" style={{ marginTop: 0 }}>
                            <label>
                              {t('integrations.syncSettingsJson')}
                              <textarea
                                rows={4}
                                value={syncSettingsJson}
                                onChange={(e) => setSyncSettingsJson(e.target.value)}
                                style={{ fontFamily: 'monospace', width: '100%' }}
                              />
                            </label>
                            <div className="form-actions">
                              <button
                                type="button"
                                onClick={() => saveSyncSettings(source.id)}
                                disabled={updateSettingsMutation.isPending}
                              >
                                {t('common.save')}
                              </button>
                              <button
                                type="button"
                                className="secondary"
                                onClick={() => {
                                  setEditingSyncSettings(null)
                                  setSyncSettingsJson('')
                                }}
                              >
                                {t('common.cancel')}
                              </button>
                            </div>
                          </div>
                        </td>
                      </tr>
                    ) : null}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="muted">{t('integrations.noSources')}</p>
        )}
      </div>

      <div className="card">
        <h3>{t('integrations.syncHistory')}</h3>
        {jobs.data?.length ? (
          <table>
            <thead>
              <tr>
                <th>{t('integrations.provider')}</th>
                <th>{t('billing.status')}</th>
                <th>{t('integrations.message')}</th>
                <th>{t('integrations.finished')}</th>
              </tr>
            </thead>
            <tbody>
              {jobs.data.map((job) => (
                <tr key={job.id}>
                  <td>{job.provider}</td>
                  <td>{job.status}</td>
                  <td>{job.message ?? '—'}</td>
                  <td>{job.finished_at ? new Date(job.finished_at).toLocaleString() : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">{t('integrations.noSyncHistory')}</p>
        )}
      </div>
    </div>
  )
}
