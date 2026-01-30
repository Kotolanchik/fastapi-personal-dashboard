import { EntriesPage } from './EntriesPage'

export const HealthPage = () => (
  <EntriesPage
    title="Здоровье"
    resource="health"
    fields={[
      { name: 'sleep_hours', label: 'Сон (часы)', type: 'number', min: 0, max: 24 },
      { name: 'energy_level', label: 'Энергия (1-10)', type: 'int', min: 1, max: 10 },
      { name: 'supplements', label: 'Добавки', type: 'text', optional: true },
      { name: 'weight_kg', label: 'Вес (кг)', type: 'number', optional: true },
      { name: 'wellbeing', label: 'Самочувствие (1-10)', type: 'int', min: 1, max: 10 },
      { name: 'notes', label: 'Заметки', type: 'text', optional: true },
    ]}
  />
)
