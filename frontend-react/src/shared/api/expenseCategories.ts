import api from './client'

export const FINANCE_TARGET_FIELDS = [
  'income',
  'expense_food',
  'expense_transport',
  'expense_health',
  'expense_other',
] as const

export type ExpenseCategoryMapping = {
  id: number
  user_id: number
  provider_category: string
  target_field: string
}

export const listExpenseCategoryMappings = () =>
  api.get<ExpenseCategoryMapping[]>('/finance/category-mappings').then((res) => res.data)

export const createExpenseCategoryMapping = (payload: {
  provider_category: string
  target_field: string
}) =>
  api
    .post<ExpenseCategoryMapping>('/finance/category-mappings', payload)
    .then((res) => res.data)

export const updateExpenseCategoryMapping = (
  mappingId: number,
  payload: { target_field?: string },
) =>
  api
    .patch<ExpenseCategoryMapping>(`/finance/category-mappings/${mappingId}`, payload)
    .then((res) => res.data)

export const deleteExpenseCategoryMapping = (mappingId: number) =>
  api.delete(`/finance/category-mappings/${mappingId}`)
