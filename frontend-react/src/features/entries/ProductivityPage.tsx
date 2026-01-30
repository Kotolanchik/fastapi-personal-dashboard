import { EntriesPage } from './EntriesPage'

export const ProductivityPage = () => (
  <EntriesPage
    title="Эффективность"
    resource="productivity"
    fields={[
      { name: 'deep_work_hours', label: 'Deep work (часы)', type: 'number', min: 0, max: 24 },
      { name: 'tasks_completed', label: 'Задач выполнено', type: 'int', min: 0 },
      { name: 'focus_level', label: 'Фокус (1-10)', type: 'int', min: 1, max: 10 },
      { name: 'notes', label: 'Заметки', type: 'text', optional: true },
    ]}
  />
)
