import { useEffect, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import { postGoogleFitOAuthCallback } from '../../shared/api/integrations'
import { useToast } from '../../shared/components/Toast'

/** Handles OAuth callback: ?code=... from Google Fit redirect. Exchanges code and redirects to /integrations. */
export const IntegrationsOAuthCallbackPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const toast = useToast()
  const [status, setStatus] = useState<'pending' | 'success' | 'error'>('pending')
  const ran = useRef(false)

  useEffect(() => {
    if (ran.current) return
    ran.current = true
    const code = searchParams.get('code')
    if (!code) {
      setStatus('error')
      toast.error(t('integrations.oauthCallbackMissingCode'))
      navigate('/integrations', { replace: true })
      return
    }
    postGoogleFitOAuthCallback(code)
      .then(() => {
        setStatus('success')
        toast.success(t('integrations.oauthCallbackSuccess'))
        navigate('/integrations', { replace: true })
      })
      .catch(() => {
        setStatus('error')
        toast.error(t('integrations.oauthCallbackError'))
        navigate('/integrations', { replace: true })
      })
  }, [searchParams, navigate, toast, t])

  return (
    <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
      {status === 'pending' && <p>{t('integrations.oauthCallbackConnecting')}</p>}
      {status === 'success' && <p>{t('integrations.oauthCallbackSuccess')}</p>}
      {status === 'error' && <p>{t('integrations.oauthCallbackError')}</p>}
    </div>
  )
}
