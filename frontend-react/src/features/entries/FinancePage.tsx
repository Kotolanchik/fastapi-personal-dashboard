import { EntriesPage } from './EntriesPage'

export const FinancePage = () => (
  <EntriesPage
    title="Финансы"
    resource="finance"
    fields={[
      { name: 'income', label: 'Доход', type: 'number', min: 0 },
      { name: 'expense_food', label: 'Еда', type: 'number', min: 0 },
      { name: 'expense_transport', label: 'Транспорт', type: 'number', min: 0 },
      { name: 'expense_health', label: 'Здоровье', type: 'number', min: 0 },
      { name: 'expense_other', label: 'Другое', type: 'number', min: 0 },
      { name: 'notes', label: 'Заметки', type: 'text', optional: true },
    ]}
  />
)
