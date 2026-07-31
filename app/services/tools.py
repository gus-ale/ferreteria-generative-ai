import json
from dataclasses import dataclass
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.repositories import products as product_repository
from app.schemas.chat import Citation, ToolExecution
from app.services.knowledge import KnowledgeService


class SearchProductsArguments(BaseModel):
    query: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=5, ge=1, le=10)


class GetStockArguments(BaseModel):
    product_id: int = Field(gt=0)


class SearchKnowledgeArguments(BaseModel):
    query: str = Field(min_length=2, max_length=1_000)
    top_k: int = Field(default=4, ge=1, le=8)


@dataclass
class ToolResult:
    output: dict
    execution: ToolExecution
    citations: list[Citation]


def decimal_to_number(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01")))


class ToolExecutor:
    ALLOWED_TOOLS = {
        "search_products",
        "get_stock",
        "search_knowledge",
    }

    def __init__(
        self,
        session: AsyncSession,
        knowledge_service: KnowledgeService,
    ) -> None:
        self.session = session
        self.knowledge_service = knowledge_service

    @property
    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "name": "search_products",
                "description": (
                    "Search active hardware-store products by name, SKU, "
                    "description, or category. Use before asking for a product ID."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                        },
                    },
                    "required": ["query", "limit"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "get_stock",
                "description": "Get the current stock for one product ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "integer", "minimum": 1},
                    },
                    "required": ["product_id"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
            {
                "type": "function",
                "name": "search_knowledge",
                "description": (
                    "Search indexed manuals, policies, warranties, and technical "
                    "documents. Answers must remain grounded in returned content."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "top_k": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 8,
                        },
                    },
                    "required": ["query", "top_k"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        ]

    async def execute(self, name: str, arguments: dict) -> ToolResult:
        if name not in self.ALLOWED_TOOLS:
            raise ValueError(f"Tool is not allowed: {name}")

        try:
            if name == "search_products":
                return await self._search_products(arguments)
            if name == "get_stock":
                return await self._get_stock(arguments)
            return await self._search_knowledge(arguments)
        except ValidationError as exc:
            raise ValueError(f"Invalid arguments for {name}: {exc}") from exc

    async def _search_products(self, raw: dict) -> ToolResult:
        arguments = SearchProductsArguments.model_validate(raw)
        products = await product_repository.search_products(
            self.session,
            arguments.query,
            limit=arguments.limit,
        )
        output = {
            "products": [
                {
                    "id": product.id,
                    "sku": product.sku,
                    "name": product.name,
                    "category": product.category,
                    "price_ars": decimal_to_number(product.price),
                    "stock": product.stock,
                }
                for product in products
            ]
        }
        return ToolResult(
            output=output,
            execution=ToolExecution(
                name="search_products",
                arguments=arguments.model_dump(),
                result_summary=f"{len(products)} product(s) found",
            ),
            citations=[],
        )

    async def _get_stock(self, raw: dict) -> ToolResult:
        arguments = GetStockArguments.model_validate(raw)
        product = await product_repository.get_product(
            self.session,
            arguments.product_id,
        )
        if product is None or not product.active:
            raise NotFoundError("Product not found")
        output = {
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "stock": product.stock,
        }
        return ToolResult(
            output=output,
            execution=ToolExecution(
                name="get_stock",
                arguments=arguments.model_dump(),
                result_summary=f"Current stock: {product.stock}",
            ),
            citations=[],
        )

    async def _search_knowledge(self, raw: dict) -> ToolResult:
        arguments = SearchKnowledgeArguments.model_validate(raw)
        results = await self.knowledge_service.search(
            arguments.query,
            top_k=arguments.top_k,
        )
        citations = [
            Citation(
                title=result.title,
                source=result.source,
                chunk_id=result.chunk_id,
                score=result.score,
            )
            for result in results
        ]
        output = {
            "matches": [
                {
                    "chunk_id": result.chunk_id,
                    "title": result.title,
                    "source": result.source,
                    "content": result.content,
                    "score": result.score,
                }
                for result in results
            ]
        }
        return ToolResult(
            output=output,
            execution=ToolExecution(
                name="search_knowledge",
                arguments=arguments.model_dump(),
                result_summary=f"{len(results)} grounded chunk(s) retrieved",
            ),
            citations=citations,
        )

    @staticmethod
    def serialize(result: ToolResult) -> str:
        return json.dumps(result.output, ensure_ascii=False, default=str)
