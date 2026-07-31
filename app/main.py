import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from prometheus_client import make_asgi_app

import app.models  # noqa: F401
from app.api.router import api_router
from app.core.config import settings
from app.core.errors import ConflictError, DomainError
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.middleware import RequestContextMiddleware
from app.repositories.products import seed_products
from app.schemas.knowledge import DocumentCreate
from app.services.embeddings import HashEmbeddingProvider, OpenAIEmbeddingProvider
from app.services.knowledge import KnowledgeService

logger = logging.getLogger("ferreteria.startup")

DEMO_MANUAL = """
El taladro percutor T700 posee una potencia nominal de 700 W y un mandril de
13 mm. Para trabajar sobre mampostería se debe usar el modo percutor y una mecha
apta para hormigón. Antes de cambiar la mecha, desconecte la herramienta.
La garantía comercial de demostración es de 12 meses para defectos de fabricación
y no cubre desgaste, uso profesional intensivo ni daños por humedad.
""".strip()


def build_openai_client() -> AsyncOpenAI | None:
    needs_openai = settings.ai_provider == "openai" or settings.embedding_provider == "openai"
    if not needs_openai:
        return None
    return AsyncOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        timeout=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    openai_client = build_openai_client()
    app.state.openai_client = openai_client
    app.state.embedding_provider = (
        OpenAIEmbeddingProvider(
            openai_client,
            settings.openai_embedding_model,
        )
        if settings.embedding_provider == "openai"
        else HashEmbeddingProvider(settings.local_embedding_dimensions)
    )

    if settings.auto_create_tables:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    if settings.seed_demo_data:
        async with AsyncSessionLocal() as session:
            await seed_products(session)
            knowledge_service = KnowledgeService(
                session,
                app.state.embedding_provider,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
            try:
                await knowledge_service.ingest(
                    DocumentCreate(
                        title="Manual de demostración del taladro T700",
                        source="demo/manual-taladro-t700",
                        content=DEMO_MANUAL,
                        metadata={"kind": "demo"},
                    )
                )
            except ConflictError:
                await session.rollback()

    logger.info(
        "application_started",
        extra={
            "environment": settings.app_env,
            "ai_provider": settings.ai_provider,
            "embedding_provider": settings.embedding_provider,
        },
    )
    yield

    if openai_client is not None:
        await openai_client.close()
    await engine.dispose()
    logger.info("application_stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Production-oriented portfolio API demonstrating RAG, Responses API "
        "function calling, conversational memory, guardrails, evaluations, "
        "observability, and Docker."
    ),
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Key", "X-Request-ID"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "unhandled_application_error",
        extra={"request_id": getattr(request.state, "request_id", None)},
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None),
            }
        },
    )


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "provider": settings.ai_provider,
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health/ready",
    }


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount("/metrics", make_asgi_app())
