from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message


async def get_or_create_conversation(
    session: AsyncSession,
    conversation_id: str | None,
) -> Conversation:
    if conversation_id:
        conversation = await session.get(Conversation, conversation_id)
        if conversation:
            return conversation

    conversation = Conversation()
    session.add(conversation)
    await session.flush()
    return conversation


async def add_message(
    session: AsyncSession,
    conversation_id: str,
    role: str,
    content: str,
    *,
    tool_name: str | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_name=tool_name,
    )
    session.add(message)
    await session.flush()
    return message


async def recent_messages(
    session: AsyncSession,
    conversation_id: str,
    *,
    limit: int,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(limit)
    )
    result = await session.scalars(statement)
    return list(reversed(result.all()))


async def get_conversation(
    session: AsyncSession,
    conversation_id: str,
) -> Conversation | None:
    return await session.get(Conversation, conversation_id)


async def all_messages(
    session: AsyncSession,
    conversation_id: str,
) -> list[Message]:
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
    )
    result = await session.scalars(statement)
    return list(result.all())
