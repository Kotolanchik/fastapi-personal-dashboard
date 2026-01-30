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
  const handleDismiss = () => {
    setOnboardingCompleted()
    onDismiss()
  }

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="onboarding-title">
      <div className="onboarding-modal card">
        <h2 id="onboarding-title">Welcome to LifePulse</h2>
        <p>
          This is your personal dashboard. Track <strong>health</strong>, <strong>finance</strong>,{' '}
          <strong>productivity</strong>, and <strong>learning</strong> in one place. Your data builds
          trends, correlations, and insights over time.
        </p>
        <p>
          Add your first entry to get started — for example, log today&apos;s sleep and energy in Health.
        </p>
        <div className="onboarding-actions">
          <Link to="/health" className="onboarding-btn primary" onClick={handleDismiss}>
            Add first entry (Health)
          </Link>
          <button type="button" className="secondary" onClick={handleDismiss}>
            Explore dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
