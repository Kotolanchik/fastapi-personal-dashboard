"""OpenAI-compatible LLM client (OpenAI, Ollama, or any compatible API)."""

from __future__ import annotations

from typing import Any

from ..core.config import get_settings

# Optional: openai package for OpenAI-compatible APIs
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[misc, assignment]

SYSTEM_PROMPT = """Ты — помощник в личном дашборде LifePulse. Отвечай кратко и по делу.
Темы: здоровье, финансы, продуктивность, обучение, цели. Язык ответа — тот же, что у пользователя."""

INSIGHT_SYSTEM = """Ты — аналитик личных данных. На основе краткой сводки данных пользователя 
сформулируй один лаконичный инсайт или рекомендацию (1–3 предложения). Язык — тот же, что в данных."""


def _client() -> Any:
    if OpenAI is None:
        return None
    s = get_settings()
    if s.llm_base_url:
        return OpenAI(base_url=s.llm_base_url, api_key=s.llm_api_key or "ollama")
    if s.llm_api_key:
        return OpenAI(api_key=s.llm_api_key)
    return None


def llm_chat(message: str, context: str | None = None) -> tuple[str | None, str | None]:
    """
    Send user message to LLM, optionally with context. Returns (reply_text, model_name) or (None, None) if disabled.
    """
    client = _client()
    if not client:
        return None, None

    s = get_settings()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "user", "content": f"Контекст данных:\n{context}\n\nВопрос пользователя: {message}"})
    else:
        messages.append({"role": "user", "content": message})

    try:
        resp = client.chat.completions.create(
            model=s.llm_model,
            messages=messages,
            max_tokens=1024,
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and choice.message and choice.message.content:
            return choice.message.content.strip(), getattr(resp, "model", None) or s.llm_model
    except Exception:
        pass
    return None, None


def llm_insight(context: str) -> tuple[str | None, str | None]:
    """
    Generate one short insight from user data context. Returns (insight_text, model_name) or (None, None).
    """
    client = _client()
    if not client:
        return None, None

    s = get_settings()
    messages = [
        {"role": "system", "content": INSIGHT_SYSTEM},
        {"role": "user", "content": f"Сводка данных:\n{context}\n\nДай один инсайт или рекомендацию."},
    ]
    try:
        resp = client.chat.completions.create(
            model=s.llm_model,
            messages=messages,
            max_tokens=256,
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and choice.message and choice.message.content:
            return choice.message.content.strip(), getattr(resp, "model", None) or s.llm_model
    except Exception:
        pass
    return None, None
