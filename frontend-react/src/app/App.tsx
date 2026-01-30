import { Navigate, Route, Routes } from 'react-router-dom'

import { LoginPage } from '../features/auth/LoginPage'
import { RegisterPage } from '../features/auth/RegisterPage'
import { RequireAuth } from '../features/auth/RequireAuth'
import { useAuth } from '../features/auth/AuthContext'
import { BillingPage } from '../features/billing/BillingPage'
import { DashboardPage } from '../features/dashboard/DashboardPage'
import { GoalsPage } from '../features/goals/GoalsPage'
import { SettingsPage } from '../features/settings/SettingsPage'
import { WeeklyReportPage } from '../features/reports/WeeklyReportPage'
import { FinancePage } from '../features/entries/FinancePage'
import { HealthPage } from '../features/entries/HealthPage'
import { LearningPage } from '../features/entries/LearningPage'
import { ProductivityPage } from '../features/entries/ProductivityPage'
import { AssistantPage } from '../features/assistant/AssistantPage'
import { IntegrationsPage } from '../features/integrations/IntegrationsPage'
import { LandingPage } from '../features/landing/LandingPage'
import { NotFoundPage } from '../features/errors/NotFoundPage'
import { PrivacyPage } from '../features/legal/PrivacyPage'
import { TermsPage } from '../features/legal/TermsPage'
import { ApiErrorBanner } from '../shared/components/ApiErrorBanner'
import { Layout } from '../shared/components/Layout'

const LandingOrRedirect = () => {
  const { token } = useAuth()
  if (token) return <Navigate to="/dashboard" replace />
  return <LandingPage />
}

export const App = () => (
  <>
    <ApiErrorBanner />
    <Routes>
      <Route path="/" element={<LandingOrRedirect />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/privacy" element={<PrivacyPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<Layout />}>
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="assistant" element={<AssistantPage />} />
          <Route path="weekly-report" element={<WeeklyReportPage />} />
          <Route path="goals" element={<GoalsPage />} />
          <Route path="health" element={<HealthPage />} />
          <Route path="finance" element={<FinancePage />} />
          <Route path="productivity" element={<ProductivityPage />} />
          <Route path="learning" element={<LearningPage />} />
          <Route path="integrations" element={<IntegrationsPage />} />
          <Route path="billing" element={<BillingPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  </>
)
