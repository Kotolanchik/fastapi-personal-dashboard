import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  listExpenseCategoryMappings,
  createExpenseCategoryMapping,
  deleteExpenseCategoryMapping,
  FINANCE_TARGET_FIELDS,
  type ExpenseCategoryMapping,
} from '../../shared/api/expenseCategories'
import { useToast } from '../../shared/components/Toast'
import { EntriesPage } from './EntriesPage'

export const FinancePage = () => {
  const { t } = useTranslation()
  const toast = useToast()
  const queryClient = useQueryClient()
  const [newProviderCategory, setNewProviderCategory] = useState('')
  const [newTargetField, setNewTargetField] = useState('expense_other')

  const mappingsQuery = useQuery({
    queryKey: ['finance', 'category-mappings'],
    queryFn: listExpenseCategoryMappings,
  })
  const mappings = mappingsQuery.data ?? []

  const createMapping = useMutation({
    mutationFn: createExpenseCategoryMapping,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['finance', 'category-mappings'] })
      setNewProviderCategory('')
      toast.success(t('finance.categoryMappingAdded'))
    },
    onError: (err: { response?: { data?: { detail?: string } } }) => {
      toast.error(err?.response?.data?.detail ?? t('finance.categoryMappingFailed'))
    },
  })
  const deleteMapping = useMutation({
    mutationFn: deleteExpenseCategoryMapping,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['finance', 'category-mappings'] }),
  })

  return (
    <div className="stack">
      <section className="card">
        <h3>{t('finance.expenseCategoryMappings')}</h3>
        <p className="muted">{t('finance.expenseCategoryMappingsHint')}</p>
        {mappings.length > 0 && (
          <table style={{ marginBottom: '1rem' }}>
            <thead>
              <tr>
                <th>{t('finance.providerCategory')}</th>
                <th>{t('finance.targetField')}</th>
                <th>{t('entries.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {mappings.map((m: ExpenseCategoryMapping) => (
                <tr key={m.id}>
                  <td>{m.provider_category}</td>
                  <td>{m.target_field}</td>
                  <td>
                    <button
                      type="button"
                      className="secondary small"
                      onClick={() => deleteMapping.mutate(m.id)}
                      disabled={deleteMapping.isPending}
                    >
                      {t('common.remove')}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div className="form-grid" style={{ maxWidth: '32rem' }}>
          <label>
            {t('finance.providerCategory')}
            <input
              type="text"
              value={newProviderCategory}
              onChange={(e) => setNewProviderCategory(e.target.value)}
              placeholder="e.g. groceries"
            />
          </label>
          <label>
            {t('finance.targetField')}
            <select
              value={newTargetField}
              onChange={(e) => setNewTargetField(e.target.value)}
            >
              {FINANCE_TARGET_FIELDS.map((f) => (
                <option key={f} value={f}>
                  {t(`entries.labels.finance.${f}`)}
                </option>
              ))}
            </select>
          </label>
          <div className="form-actions">
            <button
              type="button"
              disabled={!newProviderCategory.trim() || createMapping.isPending}
              onClick={() => {
                if (!newProviderCategory.trim()) return
                createMapping.mutate({
                  provider_category: newProviderCategory.trim(),
                  target_field: newTargetField,
                })
              }}
            >
              {createMapping.isPending ? '…' : t('common.add')}
            </button>
          </div>
        </div>
      </section>

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
    </div>
  )
}
