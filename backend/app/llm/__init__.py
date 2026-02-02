"""LLM integration (OpenAI-compatible API: OpenAI, Ollama, etc.)."""

from .client import llm_chat, llm_insight

__all__ = ["llm_chat", "llm_insight"]
