import api from './client'

export const GOAL_SPHERES = ['health', 'finance', 'productivity', 'learning'] as const
export type GoalSphere = (typeof GOAL_SPHERES)[number]

export type Goal = {
  id: number
  user_id: number
  sphere: string
  title: string
  target_value?: number | null
  target_metric?: string | null
  deadline?: string | null
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
}

export type GoalsProgressResponse = {
  goals: Goal[]
  progress: GoalProgress[]
}

export const getGoals = () =>
  api.get<GoalsProgressResponse>('/goals').then((res) => res.data)

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
  }>,
) => api.patch<Goal>(`/goals/${goalId}`, payload).then((res) => res.data)

export const deleteGoal = (goalId: number) =>
  api.delete(`/goals/${goalId}`)
