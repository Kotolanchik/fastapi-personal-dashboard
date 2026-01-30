import { EntriesPage } from './EntriesPage'

export const LearningPage = () => (
  <EntriesPage
    title="Learning"
    resource="learning"
    fields={[
      { name: 'study_hours', label: 'Study hours', type: 'number', min: 0, max: 24 },
      { name: 'topics', label: 'Topics', type: 'text', optional: true },
      { name: 'projects', label: 'Projects', type: 'text', optional: true },
      { name: 'notes', label: 'Notes', type: 'text', optional: true },
    ]}
  />
)
