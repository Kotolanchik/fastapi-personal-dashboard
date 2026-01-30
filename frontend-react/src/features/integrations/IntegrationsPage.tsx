import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useTranslation } from 'react-i18next'

import {
  connectSource,
  listProviders,
  listSources,
  listSyncJobs,
  syncProvider,
} from '../../shared/api/integrations'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

export const IntegrationsPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.integrations'))
  const queryClient = useQueryClient()
  const [provider, setProvider] = useState('')
  const [accessToken, setAccessToken] = useState('')
  const [refreshToken, setRefreshToken] = useState('')

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
    },
  })

  const providerOptions = providers.data?.providers ?? []

  return (
    <div className="stack">
      <div className="card banner muted" role="status">
        {t('integrations.banner')}
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
          <table>
            <thead>
              <tr>
                <th>{t('integrations.provider')}</th>
                <th>{t('billing.status')}</th>
                <th>{t('integrations.lastSynced')}</th>
                <th>{t('integrations.action')}</th>
              </tr>
            </thead>
            <tbody>
              {sources.data.map((source) => (
                <tr key={source.id}>
                  <td>{source.provider}</td>
                  <td>{source.status}</td>
                  <td>{source.last_synced_at ?? '—'}</td>
                  <td>
                    <button onClick={() => syncMutation.mutate(source.provider)}>
                      {t('integrations.sync')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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
                  <td>{job.finished_at ?? '—'}</td>
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
