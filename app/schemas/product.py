from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(default="", max_length=2_000)
    category: str = Field(min_length=2, max_length=100)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    stock: int = Field(default=0, ge=0, le=1_000_000)


class ProductRead(ProductCreate):
    id: int
    active: bool

    model_config = ConfigDict(from_attributes=True)


class ProductSearchResult(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    price: Decimal
    stock: int
