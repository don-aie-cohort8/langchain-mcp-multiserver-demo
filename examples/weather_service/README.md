# Weather Service - Implementation Comparison

This directory demonstrates the **SAME weather service** implemented four different ways using shared Pydantic models. This is an educational example showing how familiar FastAPI patterns transfer to FastMCP, PydanticAI, and FastA2A.

## Quick Start

```bash
# Run FastAPI version (REST API on port 8000)
python examples/weather_service/fastapi_impl.py

# Run FastMCP version (MCP server on port 8100)
python examples/weather_service/fastmcp_impl.py

# Run PydanticAI version (Interactive agent)
python examples/weather_service/pydanticai_impl.py --mode interactive

# Run FastA2A version (Stateful agent on port 8300)
python examples/weather_service/fasta2a_impl.py
```

## Shared Foundation

All four implementations use the **SAME Pydantic models** from `../common/models.py`:

```python
from common.models import WeatherQuery, WeatherResponse, WeatherForecast
```

### WeatherQuery (Input)
```python
class WeatherQuery(BaseModel):
    location: str              # City name or coordinates
    units: Literal["celsius", "fahrenheit"] = "celsius"
    include_forecast: bool = False
```

### WeatherResponse (Output)
```python
class WeatherResponse(BaseModel):
    location: str
    current_temp: float
    units: str
    conditions: str
    forecast: list[WeatherForecast] | None = None
```

## Implementation Comparison

| Aspect | FastAPI | FastMCP | PydanticAI | FastA2A |
|--------|---------|---------|------------|---------|
| **File** | [fastapi_impl.py](fastapi_impl.py:1) | [fastmcp_impl.py](fastmcp_impl.py:1) | [pydanticai_impl.py](pydanticai_impl.py:1) | [fasta2a_impl.py](fasta2a_impl.py:1) |
| **Initialization** | `FastAPI()` | `FastMCP()` | `Agent()` | `agent.to_a2a()` |
| **Function Decorator** | `@app.post()` | `@mcp.tool` | `@agent.tool_plain` | Same as PydanticAI |
| **Error Handling** | `HTTPException` | `ToolError` | `ValueError` | `ValueError` |
| **Transport** | HTTP REST | MCP (stdio/HTTP/SSE) | Direct calls | A2A (task queue) |
| **State** | Stateless | Stateless | Stateless | **✓ Stateful** |
| **Execution** | Sync request/response | Sync request/response | Sync request/response | **Async task queue** |
| **Context Memory** | None | None | Per-call only | **✓ Persistent** |
| **Multi-turn Conversations** | ✗ | ✗ | ✗ | **✓ Yes** |
| **Best For** | Web APIs | LLM tool integration | Agent workflows | Chatbots |
| **Default Port** | 8000 | 8100 | N/A (interactive) | 8300 |
| **OpenAPI Docs** | ✓ `/docs` | MCP protocol discovery | N/A | A2A protocol |

## What's IDENTICAL Across All Implementations

The following elements are **100% identical** in all four implementations:

### 1. Pydantic Models
```python
# ALL implementations import the same models
from common.models import WeatherQuery, WeatherResponse, WeatherForecast
```

### 2. Function Signature (except decorator)
```python
# All versions use same signature
def get_weather(query: WeatherQuery) -> WeatherResponse:
```

### 3. Business Logic (weather lookup)
```python
# This code is IDENTICAL in all 4 files
temp = 72.0 if query.units == "fahrenheit" else 22.2

forecast = None
if query.include_forecast:
    forecast = [
        WeatherForecast(day="Tomorrow", temp=temp + 2, conditions="Partly Cloudy"),
        WeatherForecast(day="Day 2", temp=temp + 1, conditions="Sunny"),
        WeatherForecast(day="Day 3", temp=temp - 1, conditions="Cloudy")
    ]

return WeatherResponse(
    location=query.location,
    current_temp=temp,
    units=query.units,
    conditions="Sunny",
    forecast=forecast
)
```

### 4. Validation
All implementations get automatic Pydantic validation:
- Type checking (location must be str)
- Enum validation (units must be "celsius" or "fahrenheit")
- Default values (units defaults to "celsius")
- Optional fields (forecast can be None)

### 5. Serialization
All implementations use Pydantic's serialization:
```python
# Automatic JSON serialization in all frameworks
response.model_dump_json()  # Same in FastAPI, FastMCP, PydanticAI, FastA2A
```

## What's DIFFERENT

Only the **framework wrapper** changes:

### 1. Server Initialization
```python
# FastAPI
app = FastAPI(title="Weather Service API", ...)

# FastMCP
mcp = FastMCP("Weather Service")

# PydanticAI
agent = Agent('openai:gpt-4o-mini', system_prompt="...")

# FastA2A
app = agent.to_a2a()  # Automatic storage/broker/worker setup
```

### 2. Function Decorator
```python
# FastAPI
@app.post("/weather", response_model=WeatherResponse)

# FastMCP
@mcp.tool

# PydanticAI
@agent.tool_plain

# FastA2A
@agent.tool_plain  # Same as PydanticAI, but used in A2A context
```

### 3. Error Handling
```python
# FastAPI
raise HTTPException(status_code=400, detail="Location cannot be empty")

# FastMCP
raise ToolError("Location cannot be empty")

# PydanticAI / FastA2A
raise ValueError("Location cannot be empty")
```

### 4. Deployment
```python
# FastAPI
uvicorn.run(app, host="0.0.0.0", port=8000)

# FastMCP
mcp.run(transport="streamable-http", host="0.0.0.0", port=8100)

# PydanticAI
result = await agent.run("What's the weather in NYC?")  # Direct usage

# FastA2A
uvicorn.run(app, host="0.0.0.0", port=8300)  # ASGI app like FastAPI
```

## When to Use Each

### Use FastAPI When:
- You need a REST API
- Clients expect HTTP endpoints
- You want automatic OpenAPI docs
- Stateless requests are sufficient

### Use FastMCP When:
- Integrating with LLM systems (Claude Desktop, LangChain)
- Building tools for AI agents
- Exposing functions via Model Context Protocol
- Stateless tool calls are sufficient

### Use PydanticAI When:
- Building AI agents with reasoning capabilities
- Combining multiple tools in agent workflows
- Natural language understanding is needed
- Direct agent usage (not exposing as service)

### Use FastA2A When:
- Multi-turn conversations with memory
- Building chatbots (Slack, Discord, etc.)
- Agent collaboration (multiple agents, shared context)
- Long-running workflows with state persistence

## Detailed Examples

### FastAPI Example

**Start server:**
```bash
python examples/weather_service/fastapi_impl.py --port 8000
```

**Test with curl:**
```bash
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "NYC", "units": "fahrenheit", "include_forecast": true}'
```

**Response:**
```json
{
  "location": "NYC",
  "current_temp": 72.0,
  "units": "fahrenheit",
  "conditions": "Sunny",
  "forecast": [
    {"day": "Tomorrow", "temp": 74.0, "conditions": "Partly Cloudy"},
    {"day": "Day 2", "temp": 73.0, "conditions": "Sunny"},
    {"day": "Day 3", "temp": 71.0, "conditions": "Cloudy"}
  ]
}
```

### FastMCP Example

**Start server:**
```bash
python examples/weather_service/fastmcp_impl.py --port 8100
```

**Test with MCP client:**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "weather": {
        "url": "http://localhost:8100/mcp",
        "transport": "streamable_http"
    }
})

tools = await client.get_tools()
# tools[0] is get_weather with WeatherQuery schema
```

### PydanticAI Example

**Run interactively:**
```bash
python examples/weather_service/pydanticai_impl.py --mode interactive
```

**Interaction:**
```
You: What's the weather in NYC?
Agent: It's 72°F and sunny in NYC right now.

You: How about with forecast?
Agent: [Calls get_weather with include_forecast=True]
      It's 72°F and sunny today. Tomorrow will be 74°F and partly cloudy,
      followed by 73°F and sunny, then 71°F and cloudy.
```

### FastA2A Example

**Start server:**
```bash
python examples/weather_service/fasta2a_impl.py --port 8300
```

**Multi-turn conversation:**
```python
import httpx

# Create conversation context
ctx = httpx.post("http://localhost:8300/contexts", json={})
context_id = ctx.json()["id"]

# First message
task1 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "What's the weather in NYC?"}]
})

# Second message (context is preserved!)
task2 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,  # SAME context
    "messages": [{"role": "user", "content": "How about tomorrow?"}]
})

# Agent remembers we asked about NYC, provides tomorrow's forecast
```

## Code Metrics

| Implementation | Lines of Code | Unique Framework Code | Shared Code |
|---------------|---------------|----------------------|-------------|
| FastAPI | ~150 | ~50 (decorators, HTTP) | ~100 (models, logic) |
| FastMCP | ~140 | ~40 (decorators, MCP) | ~100 (models, logic) |
| PydanticAI | ~135 | ~35 (agent, tools) | ~100 (models, logic) |
| FastA2A | ~155 | ~55 (A2A setup) | ~100 (models, logic) |

**Key Insight:** 60-70% of the code is shared across all implementations. Only the framework-specific wrapper changes.

## Learning Path

Recommended progression for students:

1. **Start with FastAPI** (fastapi_impl.py)
   - Most familiar for students
   - Understand Pydantic models, validation, async
   - See OpenAPI auto-generation

2. **Move to FastMCP** (fastmcp_impl.py)
   - Compare decorator changes (`@app.post` → `@mcp.tool`)
   - Understand MCP protocol vs REST
   - See tool discovery mechanism

3. **Explore PydanticAI** (pydanticai_impl.py)
   - Add agent reasoning layer
   - Understand system prompts
   - See natural language → tool calls

4. **Graduate to FastA2A** (fasta2a_impl.py)
   - Understand stateful vs stateless
   - Learn task queue patterns
   - See conversation context management

## Key Takeaways

1. **Pydantic models are universal** - Define once, use everywhere
2. **Business logic stays identical** - Only the wrapper changes
3. **Choose based on use case** - REST, MCP tools, agents, or stateful agents
4. **Pivoting is easy** - Same models mean easy framework switching
5. **FastAPI knowledge transfers** - If you know FastAPI, you understand 95% of FastMCP/PydanticAI

## See Also

- [Common Models](../common/models.py:1) - Shared Pydantic models
- [Calculator Service](../calculator_service/README.md) - Another example with same pattern
- [MCP vs A2A Decision Guide](../../docs/MCP_VS_A2A_DECISION_GUIDE.md) - When to use which
- [Pydantic Model Reuse Patterns](../../docs/PYDANTIC_MODEL_REUSE_PATTERNS.md) - Code sharing techniques

