import { EntriesPage } from './EntriesPage'

export const ProductivityPage = () => (
  <EntriesPage
    title="Productivity"
    resource="productivity"
    fields={[
      { name: 'deep_work_hours', label: 'Deep work (hours)', type: 'number', min: 0, max: 24 },
      { name: 'tasks_completed', label: 'Tasks completed', type: 'int', min: 0 },
      { name: 'focus_level', label: 'Focus (1–10)', type: 'int', min: 1, max: 10 },
      { name: 'notes', label: 'Notes', type: 'text', optional: true },
    ]}
  />
)
