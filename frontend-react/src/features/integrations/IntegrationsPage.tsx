import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import {
  connectSource,
  listProviders,
  listSources,
  listSyncJobs,
  syncProvider,
} from '../../shared/api/integrations'

export const IntegrationsPage = () => {
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
        OAuth for Google Fit / Apple Health coming soon. For now you can connect sources using
        tokens below.
      </div>
      <div className="card">
        <h3>Connect integration</h3>
        <div className="form-grid">
          <label>
            Provider
            <select value={provider} onChange={(e) => setProvider(e.target.value)}>
              <option value="">Select...</option>
              {providerOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            Access token
            <input
              type="password"
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
            />
          </label>
          <label>
            Refresh token
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
            Save
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Data sources</h3>
        {sources.data?.length ? (
          <table>
            <thead>
              <tr>
                <th>Provider</th>
                <th>Status</th>
                <th>Last synced</th>
                <th>Action</th>
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
                      Sync
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="muted">No connected sources.</p>
        )}
      </div>

      <div className="card">
        <h3>Sync history</h3>
        {jobs.data?.length ? (
          <table>
            <thead>
              <tr>
                <th>Provider</th>
                <th>Status</th>
                <th>Message</th>
                <th>Finished</th>
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
          <p className="muted">No sync history.</p>
        )}
      </div>
    </div>
  )
}
