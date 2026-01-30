import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

const ONBOARDING_STORAGE_KEY = 'lifepulse_onboarding_completed'

export const isOnboardingCompleted = (): boolean =>
  typeof window !== 'undefined' && Boolean(localStorage.getItem(ONBOARDING_STORAGE_KEY))

export const setOnboardingCompleted = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, '1')
  }
}

type OnboardingModalProps = {
  onDismiss: () => void
}

export const OnboardingModal = ({ onDismiss }: OnboardingModalProps) => {
  const { t } = useTranslation()
  const handleDismiss = () => {
    setOnboardingCompleted()
    onDismiss()
  }

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
      <div className="onboarding-modal card">
        <h2 id="onboarding-title">{t('onboarding.welcome')}</h2>
        <p dangerouslySetInnerHTML={{ __html: t('onboarding.body1') }} />
        <p>{t('onboarding.body2')}</p>
        <div className="onboarding-actions">
          <Link to="/health" className="onboarding-btn primary" onClick={handleDismiss}>
            {t('onboarding.addFirstEntry')}
          </Link>
          <button type="button" className="secondary" onClick={handleDismiss}>
            {t('onboarding.exploreDashboard')}
          </button>
        </div>
      </div>
    </div>
  )
}
