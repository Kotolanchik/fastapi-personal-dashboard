import { EntriesPage } from './EntriesPage'

export const HealthPage = () => (
  <EntriesPage
    title="Health"
    resource="health"
    fields={[
      { name: 'sleep_hours', label: 'Sleep (hours)', type: 'number', min: 0, max: 24 },
      { name: 'energy_level', label: 'Energy (1–10)', type: 'int', min: 1, max: 10 },
      { name: 'supplements', label: 'Supplements', type: 'text', optional: true },
      { name: 'weight_kg', label: 'Weight (kg)', type: 'number', optional: true },
      { name: 'wellbeing', label: 'Wellbeing (1–10)', type: 'int', min: 1, max: 10 },
      { name: 'notes', label: 'Notes', type: 'text', optional: true },
    ]}
  />
)
