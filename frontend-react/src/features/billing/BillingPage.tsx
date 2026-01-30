import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getSubscription, listPlans, subscribePlan } from '../../shared/api/billing'
import { useToast } from '../../shared/components/Toast'

export const BillingPage = () => {
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
      toast.success('Subscribed successfully.')
    },
  })

  return (
    <div className="stack">
      <div className="card">
        <h3>Available plans</h3>
        {plans.data?.length ? (
          <div className="grid cards">
            {plans.data.map((plan) => (
              <div key={plan.id} className="card nested">
                <h4>{plan.name}</h4>
                <p className="metric">
                  {plan.price_monthly} {plan.currency}
                </p>
                <button onClick={() => subscribeMutation.mutate(plan.id)}>
                  Subscribe
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">No plans configured.</p>
        )}
      </div>

      <div className="card">
        <h3>Current subscription</h3>
        {subscription.data ? (
          <div className="list">
            <p>Plan ID: {subscription.data.plan_id}</p>
            <p>Status: {subscription.data.status}</p>
            <p>Started: {subscription.data.started_at}</p>
          </div>
        ) : (
          <p className="muted">No subscription found.</p>
        )}
      </div>
    </div>
  )
}
