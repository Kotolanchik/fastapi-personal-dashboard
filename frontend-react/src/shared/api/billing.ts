import api from './client'

export type Plan = {
  id: number
  code: string
  name: string
  price_monthly: number
  currency: string
  is_active: boolean
  features?: Record<string, unknown> | null
}

export type Subscription = {
  id: number
  plan_id: number
  status: string
  started_at: string
  ends_at?: string | null
  cancel_at_period_end: boolean
  external_customer_id?: string | null
  external_subscription_id?: string | null
  created_at: string
}

export const listPlans = () =>
  api.get<Plan[]>('/billing/plans').then((res) => res.data)

export const subscribePlan = (planId: number) =>
  api.post<Subscription>('/billing/subscribe', { plan_id: planId }).then((res) => res.data)

export const getSubscription = () =>
  api.get<Subscription>('/billing/subscription').then((res) => res.data)
