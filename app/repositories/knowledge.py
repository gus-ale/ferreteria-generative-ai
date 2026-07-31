from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import KnowledgeChunk, KnowledgeDocument


async def get_document_by_hash(
    session: AsyncSession,
    content_hash: str,
) -> KnowledgeDocument | None:
    statement = select(KnowledgeDocument).where(KnowledgeDocument.content_hash == content_hash)
    return await session.scalar(statement)


async def create_document(
    session: AsyncSession,
    *,
    title: str,
    source: str,
    content_hash: str,
) -> KnowledgeDocument:
    document = KnowledgeDocument(
        title=title,
        source=source,
        content_hash=content_hash,
    )
    session.add(document)
    await session.flush()
    return document


async def create_chunks(
    session: AsyncSession,
    document_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    metadata: dict,
) -> list[KnowledgeChunk]:
    entities = [
        KnowledgeChunk(
            document_id=document_id,
            position=position,
            content=content,
            embedding=embedding,
            metadata_json=metadata,
        )
        for position, (content, embedding) in enumerate(zip(chunks, embeddings, strict=True))
    ]
    session.add_all(entities)
    await session.flush()
    return entities


async def list_chunks(session: AsyncSession) -> list[KnowledgeChunk]:
    result = await session.scalars(
        select(KnowledgeChunk).order_by(
            KnowledgeChunk.document_id,
            KnowledgeChunk.position,
        )
    )
    return list(result.all())


async def get_documents_by_ids(
    session: AsyncSession,
    document_ids: set[str],
) -> dict[str, KnowledgeDocument]:
    if not document_ids:
        return {}
    result = await session.scalars(
        select(KnowledgeDocument).where(KnowledgeDocument.id.in_(document_ids))
    )
    return {document.id: document for document in result.all()}
