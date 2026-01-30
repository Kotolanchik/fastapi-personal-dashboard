import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export const Footer = () => {
  const { t } = useTranslation()
  return (
    <footer className="app-footer">
      <Link to="/privacy">{t('common.privacyPolicy')}</Link>
      <span className="footer-sep">·</span>
      <Link to="/terms">{t('common.termsOfUse')}</Link>
    </footer>
  )
}
