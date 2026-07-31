from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=250)
    source: str = Field(default="manual", max_length=500)
    content: str = Field(min_length=20, max_length=200_000)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class DocumentCreated(BaseModel):
    id: str
    title: str
    chunks_created: int


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2_000)
    top_k: int = Field(default=4, ge=1, le=20)


class KnowledgeSearchResult(BaseModel):
    chunk_id: int
    document_id: str
    title: str
    source: str
    content: str
    score: float
    metadata: dict
