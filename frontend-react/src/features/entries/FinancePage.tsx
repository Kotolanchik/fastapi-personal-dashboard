import { EntriesPage } from './EntriesPage'

export const FinancePage = () => (
  <EntriesPage
    title="Finance"
    resource="finance"
    fields={[
      { name: 'income', label: 'Income', type: 'number', min: 0 },
      { name: 'expense_food', label: 'Food', type: 'number', min: 0 },
      { name: 'expense_transport', label: 'Transport', type: 'number', min: 0 },
      { name: 'expense_health', label: 'Health', type: 'number', min: 0 },
      { name: 'expense_other', label: 'Other', type: 'number', min: 0 },
      { name: 'notes', label: 'Notes', type: 'text', optional: true },
    ]}
  />
)
