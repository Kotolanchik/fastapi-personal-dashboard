import api from './client'

export type LearningStreakResponse = {
  current_streak_days: number
  last_activity_date: string | null
}

export const getLearningStreak = () =>
  api.get<LearningStreakResponse>('/learning/streak').then((res) => res.data)

export type LearningCourse = {
  id: number
  user_id: number
  title: string
  kind: string | null
  created_at: string
  completed_at: string | null
}

export const listLearningCourses = () =>
  api.get<LearningCourse[]>('/learning/courses').then((res) => res.data)

export const getLearningCourse = (courseId: number) =>
  api.get<LearningCourse>(`/learning/courses/${courseId}`).then((res) => res.data)

export const createLearningCourse = (payload: { title: string; kind?: string | null }) =>
  api.post<LearningCourse>('/learning/courses', payload).then((res) => res.data)

export const updateLearningCourse = (
  courseId: number,
  payload: { title?: string; kind?: string | null; completed_at?: string | null },
) =>
  api.put<LearningCourse>(`/learning/courses/${courseId}`, payload).then((res) => res.data)

export const deleteLearningCourse = (courseId: number) =>
  api.delete(`/learning/courses/${courseId}`).then((res) => res.data)
