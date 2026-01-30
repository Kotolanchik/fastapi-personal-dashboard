import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export const NotFoundPage = () => {
  const { t } = useTranslation()
  return (
    <div className="not-found">
      <h1>{t('errors.notFound')}</h1>
      <p className="muted">{t('errors.notFoundSubtitle')}</p>
      <Link to="/" className="not-found-link">
        {t('common.backToHome')}
      </Link>
    </div>
  )
}
