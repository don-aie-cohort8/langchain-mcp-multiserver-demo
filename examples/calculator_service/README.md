# Calculator Service - Implementation Comparison

This directory demonstrates the **SAME calculator service** implemented four different ways using shared Pydantic models. This reinforces the patterns from the weather service, showing consistency across different business domains.

## Quick Start

```bash
# Run FastAPI version (REST API on port 8000)
python examples/calculator_service/fastapi_impl.py

# Run FastMCP version (MCP server on port 8100)
python examples/calculator_service/fastmcp_impl.py

# Run PydanticAI version (Interactive agent)
python examples/calculator_service/pydanticai_impl.py --mode interactive

# Run FastA2A version (Stateful agent on port 8300)
python examples/calculator_service/fasta2a_impl.py
```

## Shared Foundation

All four implementations use the **SAME Pydantic models** from `../common/models.py`:

```python
from common.models import CalculationRequest, CalculationResponse
```

### CalculationRequest (Input)
```python
class CalculationRequest(BaseModel):
    operation: Literal["add", "subtract", "multiply", "divide"]
    a: float              # First operand
    b: float              # Second operand
```

### CalculationResponse (Output)
```python
class CalculationResponse(BaseModel):
    operation: str
    operands: list[float]
    result: float | None   # None if error (e.g., division by zero)
    error: str | None      # Error message if operation failed
```

## Implementation Comparison

| Aspect | FastAPI | FastMCP | PydanticAI | FastA2A |
|--------|---------|---------|------------|---------|
| **Initialization** | `FastAPI()` | `FastMCP()` | `Agent()` | `agent.to_a2a()` |
| **Function Decorator** | `@app.post()` | `@mcp.tool` | `@agent.tool_plain` | Same as PydanticAI |
| **Error Handling** | `HTTPException` | `ToolError` | `ValueError` | `ValueError` |
| **Transport** | HTTP REST | MCP (stdio/HTTP/SSE) | Direct calls | A2A (task queue) |
| **State** | Stateless | Stateless | Stateless | **✓ Stateful** |
| **Best For** | Web APIs | LLM tool integration | Agent tasks | Math tutoring bots |
| **Default Port** | 8000 | 8100 | N/A (interactive) | 8300 |

## What's IDENTICAL: Business Logic

The calculation code is **100% identical** across all implementations:

```python
result = None
error = None

try:
    if request.operation == "add":
        result = request.a + request.b
    elif request.operation == "subtract":
        result = request.a - request.b
    elif request.operation == "multiply":
        result = request.a * request.b
    elif request.operation == "divide":
        if request.b == 0:
            error = "Division by zero is not allowed"
        else:
            result = request.a / request.b
except Exception as e:
    error = f"Calculation error: {str(e)}"

return CalculationResponse(
    operation=request.operation,
    operands=[request.a, request.b],
    result=result,
    error=error
)
```

## Key Takeaways

1. **65-70% code reuse** through shared Pydantic models
2. **Only decorators change** between implementations
3. **Business logic is portable** across all frameworks
4. **Pattern is domain-independent** (works for weather, calculator, any service)

## See Also

- [Weather Service](../weather_service/README.md) - First example with same pattern
- [Examples Overview](../README.md) - Learning path
- [Common Models](../common/models.py) - Shared Pydantic definitions
