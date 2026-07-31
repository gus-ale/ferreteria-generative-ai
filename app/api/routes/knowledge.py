from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_knowledge_service
from app.core.security import require_admin_key
from app.schemas.knowledge import (
    DocumentCreate,
    DocumentCreated,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
)
from app.services.knowledge import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["RAG Knowledge Base"])


@router.post(
    "/documents",
    response_model=DocumentCreated,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_key)],
)
async def ingest_document(
    data: DocumentCreate,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> DocumentCreated:
    result = await service.ingest(data)
    return DocumentCreated(
        id=result.id,
        title=result.title,
        chunks_created=result.chunks_created,
    )


@router.post("/search", response_model=list[KnowledgeSearchResult])
async def search_knowledge(
    data: KnowledgeSearchRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> list[KnowledgeSearchResult]:
    return await service.search(data.query, top_k=data.top_k)
