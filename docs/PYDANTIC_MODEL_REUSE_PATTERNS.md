# Pydantic Model Reuse Patterns

This guide demonstrates how to write Pydantic models **once** and reuse them across FastAPI, FastMCP, PydanticAI, and FastA2A.

**Key Principle:** Define domain models as pure Pydantic classes with zero framework dependencies. These models become your universal interface definitions.

---

## Table of Contents

1. [Core Concept](#core-concept)
2. [Pattern: Shared Models Directory](#pattern-shared-models-directory)
3. [Pattern: Domain-Driven Models](#pattern-domain-driven-models)
4. [Pattern: Nested Models](#pattern-nested-models)
5. [Pattern: Request/Response Pairs](#pattern-requestresponse-pairs)
6. [Pattern: Validation Rules](#pattern-validation-rules)
7. [Pattern: Schema Documentation](#pattern-schema-documentation)
8. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
9. [Real-World Example](#real-world-example)

---

## Core Concept

### The Universal Pydantic Model

```python
from pydantic import BaseModel, Field
from typing import Literal

class WeatherQuery(BaseModel):
    """
    Universal weather query model.

    This model has ZERO framework dependencies.
    It works identically in:
    - FastAPI (request body)
    - FastMCP (tool parameter)
    - PydanticAI (agent tool parameter)
    - FastA2A (task payload)
    """
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = "celsius"
    include_forecast: bool = False
```

### Usage Across Frameworks

```python
# FastAPI
@app.post("/weather")
async def get_weather(query: WeatherQuery) -> dict:
    ...

# FastMCP
@mcp.tool
async def get_weather(query: WeatherQuery) -> dict:
    ...

# PydanticAI
@agent.tool_plain
def get_weather(query: WeatherQuery) -> dict:
    ...

# FastA2A (same as PydanticAI)
@agent.tool_plain
def get_weather(query: WeatherQuery) -> dict:
    ...
```

**Observation:** The function body is IDENTICAL. Only the decorator changes.

---

## Pattern: Shared Models Directory

### Structure

```
project/
├── common/
│   ├── __init__.py
│   └── models.py          # Shared Pydantic models
├── fastapi_service.py     # Imports from common.models
├── fastmcp_server.py      # Imports from common.models
├── pydanticai_agent.py    # Imports from common.models
└── fasta2a_app.py         # Imports from common.models
```

### Implementation

**common/models.py:**
```python
"""
Shared Pydantic models with zero framework dependencies.
"""
from pydantic import BaseModel, Field
from typing import Literal

class UserQuery(BaseModel):
    """User lookup parameters."""
    user_id: int = Field(description="Unique user identifier", gt=0)
    include_profile: bool = Field(default=False, description="Include profile data")

class UserResponse(BaseModel):
    """User information response."""
    user_id: int
    username: str
    email: str
    profile: dict | None = None
```

**common/__init__.py:**
```python
from .models import UserQuery, UserResponse

__all__ = ["UserQuery", "UserResponse"]
```

**Usage in any framework:**
```python
from common.models import UserQuery, UserResponse

# Now use in FastAPI, FastMCP, PydanticAI, or FastA2A
```

---

## Pattern: Domain-Driven Models

### Principle

Models represent **business domains**, not framework concerns.

### Example: E-commerce Domain

```python
# common/models.py
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

# ============================================================================
# Product Domain
# ============================================================================

class ProductSearch(BaseModel):
    """Product search parameters."""
    query: str = Field(description="Search query", min_length=1)
    category: str | None = Field(default=None, description="Filter by category")
    min_price: float | None = Field(default=None, ge=0, description="Minimum price")
    max_price: float | None = Field(default=None, ge=0, description="Maximum price")
    limit: int = Field(default=10, ge=1, le=100, description="Results limit")

class Product(BaseModel):
    """Product model."""
    id: int
    name: str
    description: str
    price: float = Field(ge=0)
    category: str
    in_stock: bool

class ProductList(BaseModel):
    """Paginated product list."""
    products: list[Product]
    total: int
    page: int
    pages: int

# ============================================================================
# Order Domain
# ============================================================================

class OrderItem(BaseModel):
    """Single order item."""
    product_id: int
    quantity: int = Field(ge=1)
    price: float = Field(ge=0)

class CreateOrder(BaseModel):
    """Order creation request."""
    user_id: int
    items: list[OrderItem] = Field(min_length=1)
    shipping_address: str

class Order(BaseModel):
    """Order model."""
    id: int
    user_id: int
    items: list[OrderItem]
    total: float = Field(ge=0)
    status: Literal["pending", "paid", "shipped", "delivered"]
    created_at: datetime
```

### Cross-Framework Usage

```python
# FastAPI
@app.post("/products/search", response_model=ProductList)
async def search_products(search: ProductSearch) -> ProductList:
    ...

@app.post("/orders", response_model=Order)
async def create_order(order: CreateOrder) -> Order:
    ...

# FastMCP
@mcp.tool
async def search_products(search: ProductSearch) -> ProductList:
    ...

@mcp.tool
async def create_order(order: CreateOrder) -> Order:
    ...

# PydanticAI
@agent.tool_plain
def search_products(search: ProductSearch) -> ProductList:
    ...

@agent.tool_plain
def create_order(order: CreateOrder) -> Order:
    ...
```

---

## Pattern: Nested Models

### Principle

Use composition to build complex models from simple ones.

### Example: Weather with Forecast

```python
from pydantic import BaseModel, Field

class WeatherConditions(BaseModel):
    """Current weather conditions (reusable component)."""
    temp: float = Field(description="Temperature")
    humidity: int = Field(ge=0, le=100, description="Humidity percentage")
    wind_speed: float = Field(ge=0, description="Wind speed")
    conditions: str = Field(description="Weather description")

class ForecastDay(BaseModel):
    """Single day forecast (reusable component)."""
    day: str = Field(description="Day label")
    high: float
    low: float
    conditions: str

class WeatherResponse(BaseModel):
    """Complete weather response (composed from components)."""
    location: str
    current: WeatherConditions  # Nested model
    forecast: list[ForecastDay] | None = None  # List of nested models
```

### Usage

```python
# All frameworks use the same nested structure
def get_weather(location: str) -> WeatherResponse:
    return WeatherResponse(
        location=location,
        current=WeatherConditions(
            temp=22.2,
            humidity=65,
            wind_speed=5.5,
            conditions="Sunny"
        ),
        forecast=[
            ForecastDay(day="Tomorrow", high=24.0, low=18.0, conditions="Cloudy"),
            ForecastDay(day="Day 2", high=23.0, low=17.0, conditions="Rainy"),
        ]
    )
```

---

## Pattern: Request/Response Pairs

### Principle

Define matching request/response models for each operation.

### Example: User Service

```python
from pydantic import BaseModel, Field, EmailStr

# ============================================================================
# Create User Operation
# ============================================================================

class CreateUserRequest(BaseModel):
    """Request to create a new user."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

class CreateUserResponse(BaseModel):
    """Response after creating user."""
    user_id: int
    username: str
    email: str
    created_at: str

# ============================================================================
# Update User Operation
# ============================================================================

class UpdateUserRequest(BaseModel):
    """Request to update user profile."""
    user_id: int = Field(gt=0)
    username: str | None = None
    email: EmailStr | None = None

class UpdateUserResponse(BaseModel):
    """Response after updating user."""
    user_id: int
    username: str
    email: str
    updated_at: str

# ============================================================================
# Get User Operation
# ============================================================================

class GetUserRequest(BaseModel):
    """Request to get user by ID."""
    user_id: int = Field(gt=0)

class GetUserResponse(BaseModel):
    """User information response."""
    user_id: int
    username: str
    email: str
    created_at: str
    updated_at: str | None
```

### Usage Pattern

```python
# Consistent across all frameworks
def create_user(request: CreateUserRequest) -> CreateUserResponse:
    ...

def update_user(request: UpdateUserRequest) -> UpdateUserResponse:
    ...

def get_user(request: GetUserRequest) -> GetUserResponse:
    ...
```

---

## Pattern: Validation Rules

### Principle

Embed validation rules in Pydantic models using Field constraints.

### Example: Rich Validation

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal

class PaymentRequest(BaseModel):
    """Payment processing request with validation."""

    amount: float = Field(
        description="Payment amount in USD",
        gt=0,           # Greater than 0
        le=10000,       # Less than or equal to $10,000
    )

    card_number: str = Field(
        description="Credit card number",
        min_length=13,
        max_length=19,
        pattern=r"^\d{13,19}$"  # Digits only
    )

    card_type: Literal["visa", "mastercard", "amex"] = Field(
        description="Card type"
    )

    cvv: str = Field(
        description="CVV code",
        pattern=r"^\d{3,4}$"  # 3 or 4 digits
    )

    @field_validator('card_number')
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Luhn algorithm validation."""
        # Simplified example
        if not v.isdigit():
            raise ValueError("Card number must be digits only")
        return v

    @model_validator(mode='after')
    def validate_cvv_length(self) -> 'PaymentRequest':
        """CVV length depends on card type."""
        if self.card_type == 'amex' and len(self.cvv) != 4:
            raise ValueError("Amex CVV must be 4 digits")
        elif self.card_type in ('visa', 'mastercard') and len(self.cvv) != 3:
            raise ValueError("Visa/Mastercard CVV must be 3 digits")
        return self
```

### Validation Works Everywhere

```python
# FastAPI - automatic validation
@app.post("/payments")
async def process_payment(payment: PaymentRequest) -> dict:
    ...  # Validation already done by Pydantic

# FastMCP - same validation
@mcp.tool
async def process_payment(payment: PaymentRequest) -> dict:
    ...  # Validation already done by Pydantic

# PydanticAI - same validation
@agent.tool_plain
def process_payment(payment: PaymentRequest) -> dict:
    ...  # Validation already done by Pydantic
```

---

## Pattern: Schema Documentation

### Principle

Use Field descriptions, examples, and docstrings for automatic schema generation.

### Example: Well-Documented Model

```python
from pydantic import BaseModel, Field

class BlogPostSearch(BaseModel):
    """
    Search parameters for blog posts.

    This model provides comprehensive search capabilities with
    filtering, sorting, and pagination.
    """

    query: str = Field(
        description="Search query (searches title and content)",
        examples=["python tutorial", "machine learning", "fastapi"],
        min_length=1,
        max_length=200
    )

    author: str | None = Field(
        default=None,
        description="Filter by author username",
        examples=["john_doe", "jane_smith"]
    )

    tags: list[str] | None = Field(
        default=None,
        description="Filter by tags (OR logic)",
        examples=[["python", "tutorial"], ["ml", "ai"]]
    )

    published_after: str | None = Field(
        default=None,
        description="Filter posts published after this date (ISO 8601)",
        examples=["2025-01-01", "2025-10-01"]
    )

    sort_by: Literal["relevance", "date", "popularity"] = Field(
        default="relevance",
        description="Sort order for results"
    )

    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination"
    )

    page_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of results per page"
    )
```

### Generated Schemas

This model automatically generates documentation in:
- **FastAPI:** OpenAPI schema at `/docs`
- **FastMCP:** MCP tool schema (exposed via `list_tools()`)
- **PydanticAI:** Tool description for LLM
- **FastA2A:** Task parameter schema

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Framework-Specific Models

**Don't:**
```python
# Bad: FastAPI-specific model
from fastapi import UploadFile

class UploadRequest(BaseModel):
    file: UploadFile  # FastAPI-specific type!
    description: str
```

**Do:**
```python
# Good: Framework-agnostic model
class UploadRequest(BaseModel):
    filename: str
    content_type: str
    size: int
    description: str

# Handle file upload in framework-specific code, not models
```

### ❌ Anti-Pattern 2: Circular Dependencies

**Don't:**
```python
# Bad: Circular import
# models.py
from services import UserService

class User(BaseModel):
    id: int
    service: UserService  # Circular dependency!
```

**Do:**
```python
# Good: Models are pure data classes
class User(BaseModel):
    id: int
    username: str
    email: str

# Service layer uses models, not vice versa
```

### ❌ Anti-Pattern 3: Mixed Concerns

**Don't:**
```python
# Bad: Mixing data and behavior
class User(BaseModel):
    id: int
    username: str

    def save_to_database(self):  # Logic in model!
        ...

    def send_email(self):  # Logic in model!
        ...
```

**Do:**
```python
# Good: Pure data model
class User(BaseModel):
    id: int
    username: str

# Separate service layer for logic
class UserService:
    def save_user(self, user: User):
        ...

    def send_email(self, user: User):
        ...
```

---

## Real-World Example

### Project Structure

```
ecommerce/
├── common/
│   ├── __init__.py
│   └── models.py          # ALL Pydantic models
├── api/
│   └── fastapi_app.py     # FastAPI REST API
├── tools/
│   └── fastmcp_server.py  # FastMCP tools for LLMs
├── agents/
│   └── pydanticai_agent.py # PydanticAI agents
└── bots/
    └── fasta2a_chatbot.py # FastA2A chatbot
```

### common/models.py (Shared)

```python
"""
Shared Pydantic models for e-commerce system.
Used by FastAPI, FastMCP, PydanticAI, and FastA2A implementations.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import datetime

# ============================================================================
# User Models
# ============================================================================

class CreateUser(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

# ============================================================================
# Product Models
# ============================================================================

class ProductSearch(BaseModel):
    query: str = Field(min_length=1)
    category: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)

class Product(BaseModel):
    id: int
    name: str
    price: float = Field(ge=0)
    category: str
    in_stock: bool

# ============================================================================
# Order Models
# ============================================================================

class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

class CreateOrder(BaseModel):
    user_id: int
    items: list[OrderItem] = Field(min_length=1)

class Order(BaseModel):
    id: int
    user_id: int
    items: list[OrderItem]
    total: float
    status: Literal["pending", "paid", "shipped"]
    created_at: datetime
```

### FastAPI Usage (api/fastapi_app.py)

```python
from fastapi import FastAPI
from common.models import ProductSearch, Product, CreateOrder, Order

app = FastAPI()

@app.post("/products/search", response_model=list[Product])
async def search_products(search: ProductSearch) -> list[Product]:
    ...

@app.post("/orders", response_model=Order)
async def create_order(order: CreateOrder) -> Order:
    ...
```

### FastMCP Usage (tools/fastmcp_server.py)

```python
from mcp.server.fastmcp import FastMCP
from common.models import ProductSearch, Product, CreateOrder, Order

mcp = FastMCP("Ecommerce Tools")

@mcp.tool
async def search_products(search: ProductSearch) -> list[Product]:
    ...

@mcp.tool
async def create_order(order: CreateOrder) -> Order:
    ...
```

### PydanticAI Usage (agents/pydanticai_agent.py)

```python
from pydantic_ai import Agent
from common.models import ProductSearch, Product, CreateOrder, Order

agent = Agent('openai:gpt-4o-mini', system_prompt="You are a shopping assistant")

@agent.tool_plain
def search_products(search: ProductSearch) -> list[Product]:
    ...

@agent.tool_plain
def create_order(order: CreateOrder) -> Order:
    ...
```

### FastA2A Usage (bots/fasta2a_chatbot.py)

```python
from pydantic_ai import Agent
from common.models import ProductSearch, Product, CreateOrder, Order

agent = Agent('openai:gpt-4o-mini', system_prompt="You are a shopping chatbot")

@agent.tool_plain
def search_products(search: ProductSearch) -> list[Product]:
    ...

@agent.tool_plain
def create_order(order: CreateOrder) -> Order:
    ...

app = agent.to_a2a()  # Stateful chatbot
```

### Key Observations

1. **common/models.py** defines models ONCE
2. **ALL implementations** import the same models
3. **Business logic** can be shared (same function bodies)
4. **Only decorators** change between frameworks
5. **Validation** happens automatically in all frameworks

---

## Summary

### Key Takeaways

1. **Define models in a shared location** (`common/models.py`)
2. **Zero framework dependencies** in model definitions
3. **Use Pydantic features** (Field, validators, nested models)
4. **Document with descriptions and examples** for auto-generated schemas
5. **Separate data (models) from behavior (services)**

### Benefits

- **60-70% code reuse** across frameworks
- **Single source of truth** for data schemas
- **Consistent validation** everywhere
- **Easy framework switching** (just change decorators)
- **Automatic documentation** in all frameworks

### Best Practices

✅ **Do:**
- Put all models in `common/models.py`
- Use `Field()` for rich descriptions
- Add examples for documentation
- Use validators for complex rules
- Keep models framework-agnostic

❌ **Don't:**
- Import framework-specific types in models
- Mix logic with data in models
- Create circular dependencies
- Duplicate model definitions

---

## See Also

- [FastMCP/PydanticAI Comparison](FASTMCP_PYDANTICAI_COMPARISON.md) - Technical comparison
- [MCP vs A2A Decision Guide](MCP_VS_A2A_DECISION_GUIDE.md) - When to use which
- [Weather Service Examples](../examples/weather_service/README.md) - Real implementations

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Author:** AIE Cohort 8 Educational Materials
