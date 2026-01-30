import { Navigate, Route, Routes } from 'react-router-dom'

import { LoginPage } from '../features/auth/LoginPage'
import { RegisterPage } from '../features/auth/RegisterPage'
import { RequireAuth } from '../features/auth/RequireAuth'
import { BillingPage } from '../features/billing/BillingPage'
import { DashboardPage } from '../features/dashboard/DashboardPage'
import { FinancePage } from '../features/entries/FinancePage'
import { HealthPage } from '../features/entries/HealthPage'
import { LearningPage } from '../features/entries/LearningPage'
import { ProductivityPage } from '../features/entries/ProductivityPage'
import { IntegrationsPage } from '../features/integrations/IntegrationsPage'
import { Layout } from '../shared/components/Layout'

export const App = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route element={<RequireAuth />}>
      <Route element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="health" element={<HealthPage />} />
        <Route path="finance" element={<FinancePage />} />
        <Route path="productivity" element={<ProductivityPage />} />
        <Route path="learning" element={<LearningPage />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="billing" element={<BillingPage />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
)
