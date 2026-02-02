"""LLM / AI Assistant API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ... import schemas
from ...analytics import insights_payload
from ...llm.client import llm_chat, llm_insight
from ..deps import get_current_user, get_db_session

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/chat", response_model=schemas.LlmChatResponse)
def chat(
    body: schemas.LlmChatRequest,
    user=Depends(get_current_user),
):
    """Send a message to the AI assistant. Optional context (e.g. dashboard summary) improves answers."""
    reply, model = llm_chat(body.message, body.context)
    if reply is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM is not configured. Set LLM_API_KEY (OpenAI) or LLM_BASE_URL (e.g. Ollama).",
        )
    return schemas.LlmChatResponse(reply=reply, model=model)


@router.get("/insight", response_model=schemas.LlmInsightsResponse)
def insight(
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    """Generate one AI insight from the current user's analytics summary. Requires LLM configured."""
    payload = insights_payload(db, user_id=user.id)
    parts = []
    for i in payload.get("insights") or []:
        if isinstance(i, dict) and "message" in i:
            parts.append(i["message"])
        elif isinstance(i, str):
            parts.append(i)
    context = "\n".join(parts) if parts else "Нет достаточных данных для анализа."
    insight_text, model = llm_insight(context)
    if insight_text is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM is not configured. Set LLM_API_KEY or LLM_BASE_URL.",
        )
    return schemas.LlmInsightsResponse(insight=insight_text, model=model)
