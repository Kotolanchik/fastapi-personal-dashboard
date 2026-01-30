import { useTranslation } from 'react-i18next'

import { EntriesPage } from './EntriesPage'

export const ProductivityPage = () => {
  const { t } = useTranslation()
  return (
    <EntriesPage
      title={t('nav.productivity')}
      resource="productivity"
      fields={[
        { name: 'deep_work_hours', label: t('entries.labels.productivity.deep_work_hours'), type: 'number', min: 0, max: 24 },
        { name: 'tasks_completed', label: t('entries.labels.productivity.tasks_completed'), type: 'int', min: 0 },
        { name: 'focus_level', label: t('entries.labels.productivity.focus_level'), type: 'int', min: 1, max: 10 },
        { name: 'notes', label: t('entries.labels.productivity.notes'), type: 'text', optional: true },
      ]}
    />
  )
}
