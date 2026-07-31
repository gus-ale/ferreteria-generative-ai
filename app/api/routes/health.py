from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
async def liveness() -> dict:
    return {"status": "alive"}


@router.get("/ready")
async def readiness(
    session: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready",
        ) from exc

    return {
        "status": "ready",
        "database": "available",
        "ai_provider": settings.ai_provider,
        "embedding_provider": settings.embedding_provider,
    }
