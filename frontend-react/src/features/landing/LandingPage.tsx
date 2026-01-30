import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export const LandingPage = () => {
  const { t } = useTranslation()
  return (
    <div className="landing">
      <header className="landing-header">
        <h1 className="landing-logo">LifePulse</h1>
        <p className="landing-tagline">{t('landing.tagline')}</p>
        <nav className="landing-actions">
          <Link to="/login" className="landing-btn secondary">
            {t('landing.signIn')}
          </Link>
          <Link to="/register" className="landing-btn primary">
            {t('landing.getStarted')}
          </Link>
        </nav>
      </header>
      <section className="landing-hero">
        <h2>{t('landing.heroTitle')}</h2>
        <p>{t('landing.heroBody')}</p>
        <ul className="landing-features">
          <li>{t('landing.featureHealth')}</li>
          <li>{t('landing.featureFinance')}</li>
          <li>{t('landing.featureProductivity')}</li>
          <li>{t('landing.featureLearning')}</li>
        </ul>
        <Link to="/register" className="landing-cta">
          {t('landing.createAccount')}
        </Link>
        <p className="landing-free-note">{t('landing.freeNote')}</p>
      </section>
      <section className="landing-social">
        <p className="landing-social-text">{t('landing.socialText')}</p>
      </section>
      <footer className="landing-footer">
        <Link to="/privacy">{t('common.privacyPolicy')}</Link>
        <span className="sep">·</span>
        <Link to="/terms">{t('common.termsOfUse')}</Link>
      </footer>
    </div>
  )
}
