import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getSubscription, listPlans, subscribePlan } from '../../shared/api/billing'

export const BillingPage = () => {
  const queryClient = useQueryClient()
  const plans = useQuery({ queryKey: ['plans'], queryFn: listPlans })
  const subscription = useQuery({
    queryKey: ['subscription'],
    queryFn: getSubscription,
    retry: false,
  })

  const subscribeMutation = useMutation({
    mutationFn: (planId: number) => subscribePlan(planId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['subscription'] }),
  })

  return (
    <div className="stack">
      <div className="card">
        <h3>Доступные планы</h3>
        {plans.data?.length ? (
          <div className="grid cards">
            {plans.data.map((plan) => (
              <div key={plan.id} className="card nested">
                <h4>{plan.name}</h4>
                <p className="metric">
                  {plan.price_monthly} {plan.currency}
                </p>
                <button onClick={() => subscribeMutation.mutate(plan.id)}>
                  Подписаться
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">Планы не настроены.</p>
        )}
      </div>

      <div className="card">
        <h3>Текущая подписка</h3>
        {subscription.data ? (
          <div className="list">
            <p>Plan ID: {subscription.data.plan_id}</p>
            <p>Status: {subscription.data.status}</p>
            <p>Started: {subscription.data.started_at}</p>
          </div>
        ) : (
          <p className="muted">Подписка не найдена.</p>
        )}
      </div>
    </div>
  )
}
