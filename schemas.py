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


class ProductUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)
    in_stock: bool
    tags: list[str]
    category: Category


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    price: float | None = Field(default=None, gt=0)
    in_stock: bool | None = None
    tags: list[str] | None = None
    category: Category | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool
    tags: list[str]
    category: Category
