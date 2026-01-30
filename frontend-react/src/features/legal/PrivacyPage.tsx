import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export const PrivacyPage = () => {
  const { t } = useTranslation()
  return (
    <div className="legal-page">
      <div className="legal-content">
        <h1>{t('legal.privacyTitle')}</h1>
        <p className="legal-updated">{t('legal.lastUpdated')}</p>
        <p>{t('legal.privacyIntro')}</p>
        <h2>{t('legal.privacySectionCollect')}</h2>
        <p>{t('legal.privacyCollect')}</p>
        <h2>{t('legal.privacySectionUse')}</h2>
        <p>{t('legal.privacyUse')}</p>
        <h2>{t('legal.privacySectionSecurity')}</h2>
        <p>{t('legal.privacySecurity')}</p>
        <p>{t('legal.contactUs')}</p>
        <Link to="/" className="legal-back">{t('legal.backToHome')}</Link>
      </div>
    </div>
  )
}
