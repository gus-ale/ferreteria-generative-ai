from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError
from app.core.security import require_admin_key
from app.db.session import get_db
from app.repositories import products as product_repository
from app.schemas.product import ProductCreate, ProductRead

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductRead])
async def list_products(
    query: str = Query(default="", max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> list:
    return await product_repository.search_products(
        session,
        query,
        limit=limit,
    )


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_key)],
)
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await product_repository.create_product(session, data)
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("A product with this SKU already exists") from exc
