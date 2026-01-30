import { useTranslation } from 'react-i18next'

import { EntriesPage } from './EntriesPage'

export const LearningPage = () => {
  const { t } = useTranslation()
  return (
    <EntriesPage
      title={t('nav.learning')}
      resource="learning"
      fields={[
        { name: 'study_hours', label: t('entries.labels.learning.study_hours'), type: 'number', min: 0, max: 24 },
        { name: 'topics', label: t('entries.labels.learning.topics'), type: 'text', optional: true },
        { name: 'projects', label: t('entries.labels.learning.projects'), type: 'text', optional: true },
        { name: 'notes', label: t('entries.labels.learning.notes'), type: 'text', optional: true },
      ]}
    />
  )
}
