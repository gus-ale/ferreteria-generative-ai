import hashlib
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError
from app.repositories import knowledge as knowledge_repository
from app.schemas.knowledge import DocumentCreate, KnowledgeSearchResult
from app.services.chunking import chunk_text
from app.services.embeddings import EmbeddingProvider
from app.services.vector_search import rank_vectors


@dataclass(frozen=True)
class IngestedDocument:
    id: str
    title: str
    chunks_created: int


class KnowledgeService:
    def __init__(
        self,
        session: AsyncSession,
        embedding_provider: EmbeddingProvider,
        *,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self.session = session
        self.embedding_provider = embedding_provider
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def ingest(self, data: DocumentCreate) -> IngestedDocument:
        content_hash = hashlib.sha256(data.content.encode("utf-8")).hexdigest()
        existing = await knowledge_repository.get_document_by_hash(
            self.session,
            content_hash,
        )
        if existing:
            raise ConflictError("This document content has already been indexed")

        chunks = chunk_text(
            data.content,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
        )
        embeddings = await self.embedding_provider.embed(chunks)
        document = await knowledge_repository.create_document(
            self.session,
            title=data.title,
            source=data.source,
            content_hash=content_hash,
        )
        await knowledge_repository.create_chunks(
            self.session,
            document.id,
            chunks,
            embeddings,
            data.metadata,
        )
        await self.session.commit()
        return IngestedDocument(
            id=document.id,
            title=document.title,
            chunks_created=len(chunks),
        )

    async def search(
        self,
        query: str,
        *,
        top_k: int,
    ) -> list[KnowledgeSearchResult]:
        query_vectors = await self.embedding_provider.embed([query])
        chunks = await knowledge_repository.list_chunks(self.session)
        if not query_vectors or not chunks:
            return []

        ranked = rank_vectors(
            query_vectors[0],
            [(chunk.id, chunk.embedding) for chunk in chunks],
            top_k=top_k,
        )
        chunk_by_id = {chunk.id: chunk for chunk in chunks}
        document_ids = {
            chunk_by_id[item.item_id].document_id for item in ranked if item.item_id in chunk_by_id
        }
        documents = await knowledge_repository.get_documents_by_ids(
            self.session,
            document_ids,
        )

        results: list[KnowledgeSearchResult] = []
        for item in ranked:
            chunk = chunk_by_id[item.item_id]
            document = documents[chunk.document_id]
            results.append(
                KnowledgeSearchResult(
                    chunk_id=chunk.id,
                    document_id=document.id,
                    title=document.title,
                    source=document.source,
                    content=chunk.content,
                    score=round(item.score, 6),
                    metadata=chunk.metadata_json,
                )
            )
        return results
