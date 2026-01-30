import { useTranslation } from 'react-i18next'

import { EntriesPage } from './EntriesPage'

export const FinancePage = () => {
  const { t } = useTranslation()
  return (
    <EntriesPage
      title={t('nav.finance')}
      resource="finance"
      fields={[
        { name: 'income', label: t('entries.labels.finance.income'), type: 'number', min: 0 },
        { name: 'expense_food', label: t('entries.labels.finance.expense_food'), type: 'number', min: 0 },
        { name: 'expense_transport', label: t('entries.labels.finance.expense_transport'), type: 'number', min: 0 },
        { name: 'expense_health', label: t('entries.labels.finance.expense_health'), type: 'number', min: 0 },
        { name: 'expense_other', label: t('entries.labels.finance.expense_other'), type: 'number', min: 0 },
        { name: 'notes', label: t('entries.labels.finance.notes'), type: 'text', optional: true },
      ]}
    />
  )
}
