import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

const STORAGE_KEY = 'lifepulse_inactive_reminder_dismissed'

export const wasInactiveReminderDismissed = (): boolean =>
  typeof window !== 'undefined' && Boolean(sessionStorage.getItem(STORAGE_KEY))

export const setInactiveReminderDismissed = (): void => {
  if (typeof window !== 'undefined') {
    sessionStorage.setItem(STORAGE_KEY, '1')
  }
}

type InactiveReminderModalProps = {
  daysInactive: number | null
  onDismiss: () => void
}

export const InactiveReminderModal = ({ daysInactive, onDismiss }: InactiveReminderModalProps) => {
  const { t } = useTranslation()
  const handleLater = () => {
    setInactiveReminderDismissed()
    onDismiss()
  }

  const message =
    daysInactive === null
      ? t('inactiveReminder.noEntriesYet')
      : t('inactiveReminder.daysInactive', { count: daysInactive })

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-labelledby="inactive-reminder-title">
      <div className="onboarding-modal card">
        <h2 id="inactive-reminder-title">{t('inactiveReminder.title')}</h2>
        <p>{message}</p>
        <div className="onboarding-actions">
          <Link to="/health" className="onboarding-btn primary" onClick={onDismiss}>
            {t('inactiveReminder.logToday')}
          </Link>
          <button type="button" className="secondary" onClick={handleLater}>
            {t('inactiveReminder.later')}
          </button>
        </div>
      </div>
    </div>
  )
}
