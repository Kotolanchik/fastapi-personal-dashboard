import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'

import { getSubscription, listPlans, subscribePlan } from '../../shared/api/billing'
import { useToast } from '../../shared/components/Toast'
import { usePageTitle } from '../../shared/hooks/usePageTitle'

export const BillingPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.billing'))
  const queryClient = useQueryClient()
  const toast = useToast()
  const plans = useQuery({ queryKey: ['plans'], queryFn: listPlans })
  const subscription = useQuery({
    queryKey: ['subscription'],
    queryFn: getSubscription,
    retry: false,
  })

  const subscribeMutation = useMutation({
    mutationFn: (planId: number) => subscribePlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] })
      toast.success(t('billing.subscribedSuccess'))
    },
  })

  const planFeatures: Record<string, string> = {
    free: t('billing.planFeatures.free'),
    Free: t('billing.planFeatures.free'),
    pro: t('billing.planFeatures.pro'),
    Pro: t('billing.planFeatures.pro'),
  }

  return (
    <div className="stack">
      <div className="card banner muted" role="status">
        {t('billing.demoMode')}
      </div>
      <div className="card">
        <h3>{t('billing.availablePlans')}</h3>
        {plans.data?.length ? (
          <div className="grid cards">
            {plans.data.map((plan) => (
              <div key={plan.id} className="card nested">
                <h4>{plan.name}</h4>
                <p className="metric">
                  {plan.price_monthly} {plan.currency}
                </p>
                <p className="muted small">
                  {planFeatures[plan.name] ?? t('billing.seePlanDetails')}
                </p>
                <button onClick={() => subscribeMutation.mutate(plan.id)}>
                  {t('billing.subscribe')}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">{t('billing.noPlans')}</p>
        )}
      </div>

      <div className="card">
        <h3>{t('billing.currentSubscription')}</h3>
        {subscription.data ? (
          <div className="list">
            <p>{t('billing.planId')}: {subscription.data.plan_id}</p>
            <p>{t('billing.status')}: {subscription.data.status}</p>
            <p>{t('billing.startedAt')}: {subscription.data.started_at}</p>
          </div>
        ) : (
          <p className="muted">{t('billing.noSubscription')}</p>
        )}
      </div>
    </div>
  )
}
