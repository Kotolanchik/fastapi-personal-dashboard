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

  const planFeatures: Record<string, string> = {
    free: 'Unlimited entries, CSV export, basic insights',
    Free: 'Unlimited entries, CSV export, basic insights',
    pro: 'Advanced analytics, integrations, priority support',
    Pro: 'Advanced analytics, integrations, priority support',
  }

  return (
    <div className="stack">
      <div className="card banner muted" role="status">
        <strong>Billing is in demo mode.</strong> No real charges. Subscriptions are stored in the
        database only; payment integration is not connected.
      </div>
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
                <p className="muted small">
                  {planFeatures[plan.name] ?? 'See plan details'}
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
