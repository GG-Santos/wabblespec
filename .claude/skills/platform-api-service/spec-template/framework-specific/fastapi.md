# Framework-Specific Architecture: FastAPI

> **Applies when:** `fastapi` in requirements.txt / pyproject.toml + Python files detected.
> **Version authority:** FastAPI 0.110+. Pydantic v2. Python 3.11+. Async-first.

---

## Project Layout

```
src/
  main.py              ← Application factory (creates FastAPI app, includes routers)
  config.py            ← Settings via pydantic-settings (reads from env)
  dependencies.py      ← Shared Depends() functions (db session, auth, pagination)
  routers/
    products.py        ← APIRouter for /products
    orders.py          ← APIRouter for /orders
  schemas/
    product.py         ← Pydantic models (request/response shapes)
  models/
    product.py         ← SQLAlchemy / database models (separate from schemas)
  services/
    product_service.py ← Business logic — no HTTP concerns
  repositories/
    product_repo.py    ← Data access — no business logic
tests/
  conftest.py          ← Fixtures (test client, test DB session)
  test_products.py
```

**Schema vs model:** Pydantic schemas are the API contract (what enters/exits HTTP). SQLAlchemy models are the database shape. Never expose database models directly as response schemas — data leaks and coupling.

---

## Application Factory

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routers import products, orders
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB pool, connect to Redis, etc.
    await database.connect()
    yield
    # Shutdown: close connections cleanly
    await database.disconnect()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        # Disable docs in production if required by security policy:
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
    )
    app.include_router(products.router, prefix="/products", tags=["products"])
    app.include_router(orders.router, prefix="/orders", tags=["orders"])
    return app

app = create_app()
```

---

## Pydantic v2 Schemas

```python
# schemas/product.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    category_id: UUID

    @field_validator('name')
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('name cannot be blank')
        return v.strip()

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # replaces orm_mode=True in v2

    id: UUID
    name: str
    price: Decimal
    category_id: UUID
    created_at: datetime

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
```

**Pydantic v2 breaking changes from v1:**
- `orm_mode = True` → `model_config = ConfigDict(from_attributes=True)`
- `@validator` → `@field_validator` (classmethod)
- `schema()` → `model_json_schema()`
- Validators receive the value directly, not as a field

---

## Dependency Injection

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_session

security = HTTPBearer()

# DB session — injected per request, closed after
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Auth dependency — raises 401 if invalid
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    user = await verify_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                           detail="Invalid credentials")
    return user

# Pagination
class PaginationParams:
    def __init__(self, page: int = 1, page_size: int = Query(default=20, le=100)):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
```

```python
# routers/products.py
from fastapi import APIRouter, Depends, status
from ..dependencies import get_db, get_current_user, PaginationParams
from ..schemas.product import ProductCreate, ProductResponse, ProductListResponse
from ..services.product_service import ProductService

router = APIRouter()

@router.get("/", response_model=ProductListResponse)
async def list_products(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)  # enforces auth; user not needed in handler
):
    service = ProductService(db)
    return await service.list_products(pagination)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ProductService(db)
    return await service.create_product(data, created_by=current_user.id)
```

---

## `async def` vs `def` in Handlers

```python
# async def — for any handler that awaits I/O (DB, HTTP, cache)
@router.get("/{product_id}")
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    return await product_repo.get(db, product_id)

# def — for CPU-bound handlers with no I/O (rare in API services)
# FastAPI runs def handlers in a thread pool — they do not block the event loop
@router.post("/compute")
def compute_something(data: InputModel):
    return heavy_cpu_computation(data)  # sync OK here; runs in threadpool
```

**Rule:** Default to `async def`. Use `def` only when the handler is CPU-bound and has zero awaitable calls. Never call synchronous blocking I/O (e.g., `requests.get()`, `time.sleep()`) from an `async def` handler — it blocks the event loop. Use `httpx.AsyncClient` for outbound HTTP.

---

## Alembic Migrations

```python
# alembic/env.py — must import all models for autogenerate to detect changes
from app.models import product, order, user  # noqa: F401 — import for side effects

# Generate a migration
# alembic revision --autogenerate -m "add product table"

# Apply migrations
# alembic upgrade head

# Rollback one step
# alembic downgrade -1
```

**Rule:** Never run `Base.metadata.create_all()` in production. That bypasses migration history. All schema changes go through Alembic revisions — even in development.

---

## GWT Acceptance Scenarios

```
Given: a request body fails Pydantic validation
When: the endpoint receives the invalid payload
Then: FastAPI returns HTTP 422 Unprocessable Entity
      AND the response body lists every validation error with field path and message
      AND no exception propagates to the 500 handler

Given: the database session raises an exception during a request
When: get_db dependency catches the exception
Then: session.rollback() is called before the exception propagates
      AND the session is closed (context manager exit)
      AND the client receives an appropriate error response (not a hung connection)

Given: an endpoint requires authentication
When: a request arrives with no Authorization header or an invalid token
Then: the response is HTTP 401 with WWW-Authenticate header
      AND no data from the endpoint is returned
      AND the 401 is returned before any business logic executes
```
