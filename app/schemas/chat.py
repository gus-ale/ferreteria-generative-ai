from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    conversation_id: str | None = Field(default=None, min_length=36, max_length=36)


class ToolExecution(BaseModel):
    name: str
    arguments: dict
    result_summary: str


class Citation(BaseModel):
    title: str
    source: str
    chunk_id: int
    score: float


class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    provider: str
    trace_id: str
    tools_used: list[ToolExecution]
    citations: list[Citation]


class MessageRead(BaseModel):
    role: str
    content: str
    tool_name: str | None


class ConversationRead(BaseModel):
    id: str
    messages: list[MessageRead]
