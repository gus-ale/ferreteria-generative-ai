import re

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate


async def create_product(session: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def get_product(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


def product_search_statement(query: str, limit: int) -> Select[tuple[Product]]:
    normalized = query.strip().lower()
    terms = re.findall(r"[\wáéíóúüñ-]+", normalized)[:8]
    if not terms:
        terms = [normalized]
    term_conditions = []
    for term in terms:
        pattern = f"%{term}%"
        term_conditions.append(
            or_(
                func.lower(Product.name).like(pattern),
                func.lower(Product.description).like(pattern),
                func.lower(Product.category).like(pattern),
                func.lower(Product.sku).like(pattern),
            )
        )
    return (
        select(Product)
        .where(
            Product.active.is_(True),
            and_(*term_conditions),
        )
        .order_by(Product.name.asc())
        .limit(limit)
    )


async def search_products(
    session: AsyncSession,
    query: str = "",
    *,
    limit: int = 20,
) -> list[Product]:
    if query.strip():
        statement = product_search_statement(query, limit)
    else:
        statement = (
            select(Product)
            .where(Product.active.is_(True))
            .order_by(Product.name.asc())
            .limit(limit)
        )
    result = await session.scalars(statement)
    return list(result.all())


async def seed_products(session: AsyncSession) -> None:
    existing = await session.scalar(select(func.count(Product.id)))
    if existing:
        return

    products = [
        Product(
            sku="MAR-M20",
            name="Martillo carpintero M20",
            description="Martillo de acero forjado con mango antideslizante.",
            category="Herramientas manuales",
            price=18500,
            stock=18,
        ),
        Product(
            sku="TAL-T700",
            name="Taladro percutor T700",
            description="Taladro percutor de 700 W con mandril de 13 mm.",
            category="Herramientas eléctricas",
            price=98500,
            stock=6,
        ),
        Product(
            sku="PIN-EXT20",
            name="Pintura exterior 20 L",
            description="Pintura acrílica lavable para paredes exteriores.",
            category="Pinturas",
            price=74200,
            stock=9,
        ),
        Product(
            sku="TOR-6X40",
            name="Tornillo 6 x 40 mm",
            description="Tornillo zincado para madera. Caja de 100 unidades.",
            category="Fijaciones",
            price=8900,
            stock=45,
        ),
    ]
    session.add_all(products)
    await session.commit()
