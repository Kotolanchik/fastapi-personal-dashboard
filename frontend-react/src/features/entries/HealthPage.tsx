import { useTranslation } from 'react-i18next'

import { EntriesPage } from './EntriesPage'

export const HealthPage = () => {
  const { t } = useTranslation()
  return (
    <EntriesPage
      title={t('nav.health')}
      resource="health"
      fields={[
        { name: 'sleep_hours', label: t('entries.labels.health.sleep_hours'), type: 'number', min: 0, max: 24 },
        { name: 'energy_level', label: t('entries.labels.health.energy_level'), type: 'int', min: 1, max: 10 },
        { name: 'supplements', label: t('entries.labels.health.supplements'), type: 'text', optional: true },
        { name: 'weight_kg', label: t('entries.labels.health.weight_kg'), type: 'number', optional: true },
        { name: 'wellbeing', label: t('entries.labels.health.wellbeing'), type: 'int', min: 1, max: 10 },
        { name: 'notes', label: t('entries.labels.health.notes'), type: 'text', optional: true },
      ]}
    />
  )
}
