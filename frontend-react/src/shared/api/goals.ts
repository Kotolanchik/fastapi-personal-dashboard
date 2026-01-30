import api from './client'

export const GOAL_SPHERES = ['health', 'finance', 'productivity', 'learning'] as const
export type GoalSphere = (typeof GOAL_SPHERES)[number]

export const GOAL_PROGRESS_PERIODS = ['7d', 'month', 'deadline'] as const
export type GoalProgressPeriod = (typeof GOAL_PROGRESS_PERIODS)[number]

/** Metrics available per sphere for target_metric */
export const GOAL_METRICS_BY_SPHERE: Record<string, string[]> = {
  health: ['sleep_hours', 'energy_level', 'wellbeing'],
  finance: ['income', 'expense_total'],
  productivity: ['deep_work_hours', 'tasks_completed', 'focus_level'],
  learning: ['study_hours'],
}

export type Goal = {
  id: number
  user_id: number
  sphere: string
  title: string
  target_value?: number | null
  target_metric?: string | null
  deadline?: string | null
  archived?: boolean
  created_at: string
}

export type GoalProgress = {
  goal_id: number
  title: string
  sphere: string
  target_value?: number | null
  target_metric?: string | null
  current_value?: number | null
  progress_pct?: number | null
  deadline?: string | null
  period_start?: string | null
  period_end?: string | null
}

export type GoalsProgressResponse = {
  goals: Goal[]
  progress: GoalProgress[]
}

export const getGoals = (params?: { period?: GoalProgressPeriod; include_archived?: boolean }) =>
  api
    .get<GoalsProgressResponse>('/goals', { params: params ?? {} })
    .then((res) => res.data)

export const createGoal = (payload: {
  sphere: string
  title: string
  target_value?: number | null
  target_metric?: string | null
  deadline?: string | null
}) => api.post<Goal>('/goals', payload).then((res) => res.data)

export const updateGoal = (
  goalId: number,
  payload: Partial<{
    sphere: string
    title: string
    target_value: number | null
    target_metric: string | null
    deadline: string | null
    archived: boolean
  }>,
) => api.patch<Goal>(`/goals/${goalId}`, payload).then((res) => res.data)

export const deleteGoal = (goalId: number) =>
  api.delete(`/goals/${goalId}`)
