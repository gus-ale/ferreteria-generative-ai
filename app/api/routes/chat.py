from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_agent_service
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.repositories import conversations as conversation_repository
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationRead,
    MessageRead,
)
from app.services.agent import AgentService

router = APIRouter(prefix="/chat", tags=["Generative AI Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    service: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    result = await service.chat(data.message, data.conversation_id)
    return ChatResponse(
        answer=result.answer,
        conversation_id=result.conversation_id,
        provider=result.provider,
        trace_id=result.trace_id,
        tools_used=result.tools_used,
        citations=result.citations,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_db),
) -> ConversationRead:
    conversation = await conversation_repository.get_conversation(
        session,
        conversation_id,
    )
    if conversation is None:
        raise NotFoundError("Conversation not found")
    messages = await conversation_repository.all_messages(session, conversation.id)
    return ConversationRead(
        id=conversation.id,
        messages=[
            MessageRead(
                role=message.role,
                content=message.content,
                tool_name=message.tool_name,
            )
            for message in messages
        ],
    )
