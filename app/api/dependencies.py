from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.services.agent import AgentService
from app.services.knowledge import KnowledgeService
from app.services.tools import ToolExecutor


def get_knowledge_service(
    request: Request,
    session: AsyncSession = Depends(get_db),
) -> KnowledgeService:
    return KnowledgeService(
        session,
        request.app.state.embedding_provider,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def get_agent_service(
    request: Request,
    session: AsyncSession = Depends(get_db),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> AgentService:
    tool_executor = ToolExecutor(session, knowledge_service)
    return AgentService(
        session,
        tool_executor,
        settings,
        request.app.state.openai_client,
    )
