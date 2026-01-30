import { EntriesPage } from './EntriesPage'

export const LearningPage = () => (
  <EntriesPage
    title="Обучение"
    resource="learning"
    fields={[
      { name: 'study_hours', label: 'Часы обучения', type: 'number', min: 0, max: 24 },
      { name: 'topics', label: 'Темы', type: 'text', optional: true },
      { name: 'projects', label: 'Проекты', type: 'text', optional: true },
      { name: 'notes', label: 'Заметки', type: 'text', optional: true },
    ]}
  />
)
