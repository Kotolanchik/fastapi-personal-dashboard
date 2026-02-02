import api from './client'

export type LlmChatRequest = {
  message: string
  context?: string | null
}

export type LlmChatResponse = {
  reply: string
  model?: string | null
}

export type LlmInsightResponse = {
  insight: string
  model?: string | null
}

export const chat = (body: LlmChatRequest) =>
  api.post<LlmChatResponse>('/llm/chat', body).then((res) => res.data)

export const getInsight = () =>
  api.get<LlmInsightResponse>('/llm/insight').then((res) => res.data)
