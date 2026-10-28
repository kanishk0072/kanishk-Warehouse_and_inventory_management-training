from pydantic import BaseModel, Field


class Category(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=50)
    description: str | None = None


class ProductCreate(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    in_stock: bool = True
    tags: list[str] = Field(default_factory=list)
    category: Category


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool
    tags: list[str]
    category: Category
