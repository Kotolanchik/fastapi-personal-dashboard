import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'

import { chat, getInsight, type LlmChatResponse } from '../../shared/api/llm'
import { getInsights } from '../../shared/api/analytics'
import { usePageTitle } from '../../shared/hooks/usePageTitle'
import { useToast } from '../../shared/components/Toast'

type Message = { role: 'user' | 'assistant'; content: string }

export const AssistantPage = () => {
  const { t } = useTranslation()
  usePageTitle(t('nav.assistant'))
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const { error: showError } = useToast()

  const { data: insightsData } = useQuery({
    queryKey: ['analytics', 'insights'],
    queryFn: getInsights,
    staleTime: 60_000,
  })
  const context = insightsData?.insights?.map((i) => i.message).join('\n') ?? undefined

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res: LlmChatResponse = await chat({
        message: text,
        context: context || undefined,
      })
      setMessages((prev) => [...prev, { role: 'assistant', content: res.reply }])
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        t('assistant.errorNotConfigured')
      showError(message)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `${t('common.error')}: ${message}` },
      ])
    } finally {
      setLoading(false)
    }
  }

  const [insightLoading, setInsightLoading] = useState(false)
  const [aiInsight, setAiInsight] = useState<string | null>(null)
  const fetchAiInsight = async () => {
    setInsightLoading(true)
    setAiInsight(null)
    try {
      const res = await getInsight()
      setAiInsight(res.insight)
    } catch {
      showError(t('assistant.errorUnavailable'))
    } finally {
      setInsightLoading(false)
    }
  }

  return (
    <div className="stack">
      <div className="card flex-between">
        <div>
          <h3>{t('assistant.title')}</h3>
          <p className="muted">{t('assistant.subtitle')}</p>
        </div>
        <button
          type="button"
          className="secondary"
          onClick={fetchAiInsight}
          disabled={insightLoading}
        >
          {insightLoading ? t('assistant.generating') : t('assistant.oneInsight')}
        </button>
      </div>

      {aiInsight && (
        <div className="card">
          <h4>{t('assistant.insightFromData')}</h4>
          <p className="muted">{aiInsight}</p>
        </div>
      )}

      <div className="card" style={{ display: 'flex', flexDirection: 'column', minHeight: 320 }}>
        <h4>{t('assistant.chat')}</h4>
        <div
          className="stack"
          style={{ flex: 1, overflowY: 'auto', marginBottom: '1rem', gap: '0.75rem' }}
        >
          {messages.length === 0 && (
            <p className="muted">{t('assistant.hint')}</p>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                padding: '0.75rem 1rem',
                borderRadius: 12,
                background: m.role === 'user' ? '#2563eb' : '#e2e8f0',
                color: m.role === 'user' ? '#fff' : '#0f172a',
              }}
            >
              {m.content}
            </div>
          ))}
          {loading && (
            <div style={{ padding: '0.75rem', color: 'var(--muted)', fontStyle: 'italic' }}>
              {t('assistant.thinking')}
            </div>
          )}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            sendMessage()
          }}
          style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end' }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t('assistant.placeholder')}
            disabled={loading}
            style={{ flex: 1 }}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            {t('assistant.send')}
          </button>
        </form>
      </div>
    </div>
  )
}
