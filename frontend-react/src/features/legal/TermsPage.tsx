import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export const TermsPage = () => {
  const { t } = useTranslation()
  return (
    <div className="legal-page">
      <div className="legal-content">
        <h1>{t('legal.termsTitle')}</h1>
        <p className="legal-updated">{t('legal.lastUpdated')}</p>
        <p>{t('legal.termsIntro')}</p>
        <h2>{t('legal.termsSectionUse')}</h2>
        <p>{t('legal.termsUse')}</p>
        <h2>{t('legal.termsSectionAcceptable')}</h2>
        <p>{t('legal.termsAcceptable')}</p>
        <h2>{t('legal.termsSectionDisclaimer')}</h2>
        <p>{t('legal.termsDisclaimer')}</p>
        <p>{t('legal.contactUs')}</p>
        <Link to="/" className="legal-back">{t('legal.backToHome')}</Link>
      </div>
    </div>
  )
}
