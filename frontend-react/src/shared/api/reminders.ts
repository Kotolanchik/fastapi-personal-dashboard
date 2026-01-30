import api from './client'

export type ReminderItem = {
  type: string
  should_remind: boolean
  message: string
}

export type RemindersResponse = {
  reminders: ReminderItem[]
}

export const getReminders = () =>
  api.get<RemindersResponse>('/reminders').then((res) => res.data)
