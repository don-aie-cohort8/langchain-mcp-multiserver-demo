# Educational Examples: FastAPI → FastMCP → PydanticAI → FastA2A

This directory contains educational examples showing how **Pydantic models and business logic** transfer across four popular Python frameworks for building AI-powered services.

## Philosophy

**Start with what students know (FastAPI), then show what's different.**

All examples follow this pattern:
1. Define **shared Pydantic models** once in [common/models.py](common/models.py:1)
2. Implement the **same service** in four frameworks
3. Keep **business logic identical**, only change the wrapper
4. Demonstrate **60-70% code reuse** through Pydantic

## Framework Comparison

| Framework | Purpose | State | Protocol | Use Case |
|-----------|---------|-------|----------|----------|
| **FastAPI** | REST APIs | Stateless | HTTP | Web services, traditional APIs |
| **FastMCP** | MCP Servers | Stateless | MCP | LLM tool integration, Claude Desktop |
| **PydanticAI** | AI Agents | Stateless | Direct | Agent workflows, natural language |
| **FastA2A** | Stateful Agents | Stateful | A2A | Chatbots, multi-turn conversations |

## Available Examples

### 1. Weather Service
**Path:** [weather_service/](weather_service/README.md)

Demonstrates a weather lookup service with optional forecasts.

**Models:**
- `WeatherQuery` - Location, units, forecast flag
- `WeatherResponse` - Temperature, conditions, optional forecast array

**Implementations:**
- [fastapi_impl.py](weather_service/fastapi_impl.py:1) - REST API baseline (port 8000)
- [fastmcp_impl.py](weather_service/fastmcp_impl.py:1) - MCP server (port 8100)
- [pydanticai_impl.py](weather_service/pydanticai_impl.py:1) - Interactive agent
- [fasta2a_impl.py](weather_service/fasta2a_impl.py:1) - Stateful agent (port 8300)

**Key Learning:**
- Same Pydantic models across all frameworks
- Business logic is identical (60-70% code reuse)
- Only decorators and error handling differ

### 2. Calculator Service *(Coming Soon)*
**Path:** `calculator_service/`

Demonstrates a calculation service with multiple operations.

**Models:**
- `CalculationRequest` - Operation type, operands
- `CalculationResponse` - Result or error

**Implementations:** FastAPI, FastMCP, PydanticAI, FastA2A

## Quick Start

```bash
# Clone and setup
cd examples

# Run any implementation
python weather_service/fastapi_impl.py      # REST API on port 8000
python weather_service/fastmcp_impl.py      # MCP server on port 8100
python weather_service/pydanticai_impl.py   # Interactive agent
python weather_service/fasta2a_impl.py      # Stateful agent on port 8300
```

## Shared Models

All examples import from [common/models.py](common/models.py:1):

```python
from common.models import (
    WeatherQuery,
    WeatherResponse,
    WeatherForecast,
    CalculationRequest,
    CalculationResponse,
)
```

These models have **zero framework dependencies** and work identically in all four frameworks.

## Code Comparison

Here's what changes (and what doesn't) across frameworks:

### What's IDENTICAL (60-70% of code)

```python
# 1. Pydantic Models - Same import in all frameworks
from common.models import WeatherQuery, WeatherResponse

# 2. Function Signature - Same in all (except decorator)
def get_weather(query: WeatherQuery) -> WeatherResponse:

# 3. Business Logic - Exactly the same in all 4 implementations
temp = 72.0 if query.units == "fahrenheit" else 22.2
forecast = [...]  # Build forecast logic
return WeatherResponse(location=query.location, ...)

# 4. Validation - Automatic from Pydantic in all frameworks
# 5. Serialization - Same .model_dump_json() in all
```

### What's DIFFERENT (30-40% of code)

```python
# Server Initialization
FastAPI:     app = FastAPI(...)
FastMCP:     mcp = FastMCP(...)
PydanticAI:  agent = Agent(...)
FastA2A:     app = agent.to_a2a()

# Function Decorator
FastAPI:     @app.post("/weather")
FastMCP:     @mcp.tool
PydanticAI:  @agent.tool_plain
FastA2A:     @agent.tool_plain

# Error Handling
FastAPI:     raise HTTPException(status_code=400, ...)
FastMCP:     raise ToolError("...")
PydanticAI:  raise ValueError("...")
FastA2A:     raise ValueError("...")
```

## Learning Path

Recommended progression for students:

### Level 1: FastAPI (Baseline)
**Goal:** Understand Pydantic models, validation, OpenAPI

```bash
python weather_service/fastapi_impl.py
# Visit http://localhost:8000/docs
```

**Learn:**
- Pydantic request/response models
- Automatic validation and serialization
- OpenAPI schema generation
- Async route handlers

### Level 2: FastMCP (Transfer to MCP)
**Goal:** See what changes for LLM tool integration

```bash
python weather_service/fastmcp_impl.py
```

**Learn:**
- `@mcp.tool` decorator (vs `@app.post`)
- `ToolError` (vs `HTTPException`)
- MCP protocol (vs HTTP REST)
- Tool discovery mechanism

**Comparison:**
- **95% similar to FastAPI** - Same models, same logic
- **5% different** - Decorator, error type, protocol

### Level 3: PydanticAI (Add Agent Reasoning)
**Goal:** Add natural language understanding

```bash
python weather_service/pydanticai_impl.py --mode interactive
```

**Learn:**
- `Agent` initialization with system prompts
- `@agent.tool_plain` decorator
- Natural language → tool calls
- Direct agent usage

**Comparison:**
- **Same tool definition** as FastMCP
- **Added layer:** Agent reasoning with LLM
- **New capability:** Conversational interface

### Level 4: FastA2A (Add State & Persistence)
**Goal:** Understand stateful vs stateless

```bash
python weather_service/fasta2a_impl.py
```

**Learn:**
- `agent.to_a2a()` convenience method
- Storage/Broker/Worker architecture
- Conversation context persistence
- Multi-turn dialogues

**Comparison:**
- **Same agent** as PydanticAI
- **Added infrastructure:** Storage + broker + worker
- **New capability:** Stateful conversations

## When to Use Each

### FastAPI: REST APIs
**Choose when:**
- Building web services
- Need HTTP endpoints
- Want automatic OpenAPI docs
- Stateless requests are sufficient

**Port:** 8000 (default)
**Docs:** http://localhost:8000/docs

### FastMCP: LLM Tool Integration
**Choose when:**
- Integrating with Claude Desktop
- Building tools for LangChain agents
- Exposing functions via MCP protocol
- Stateless tool calls are sufficient

**Port:** 8100 (default)
**Protocol:** Model Context Protocol (MCP)

### PydanticAI: AI Agents
**Choose when:**
- Building AI agents
- Need natural language understanding
- Combining multiple tools
- Direct agent usage (not as service)

**Port:** N/A (interactive or library usage)
**Mode:** Interactive or programmatic

### FastA2A: Stateful Agents
**Choose when:**
- Multi-turn conversations
- Building chatbots (Slack, Discord)
- Agent collaboration needed
- Persistent conversation history required

**Port:** 8300 (default)
**Protocol:** Agent-to-Agent (A2A)

## Architecture Patterns

### Stateless Architecture (FastAPI, FastMCP, PydanticAI)

```
Request → [Framework] → Tool/Function → Response
          No persistence between calls
```

**Characteristics:**
- Each request is independent
- No conversation memory
- Simple deployment (single server)
- Horizontal scaling is easy

### Stateful Architecture (FastA2A)

```
Request → [A2A Protocol] → [Storage] ← [Context]
                          ↓
                      [Broker]
                          ↓
                      [Worker] → Agent → Tools
                          ↓
                      Response (stored in context)
```

**Characteristics:**
- Conversation context persists
- Multi-turn dialogues
- Complex deployment (storage + broker + worker)
- Requires state management

## Key Takeaways

1. **Pydantic models are portable** - Write once, use in FastAPI, FastMCP, PydanticAI, and FastA2A
2. **Business logic is reusable** - Same validation, serialization, and core logic across all frameworks
3. **Framework choice is use-case driven** - REST vs MCP vs agents vs stateful agents
4. **FastAPI knowledge transfers** - If you know FastAPI, you understand 95% of the others
5. **Start simple, add complexity** - REST → MCP tools → agents → stateful agents

## Additional Resources

- [Common Models Source](common/models.py:1) - All shared Pydantic models
- [Weather Service Comparison](weather_service/README.md) - Detailed weather service comparison
- [MCP vs A2A Decision Guide](../docs/MCP_VS_A2A_DECISION_GUIDE.md) - When to use which protocol
- [Pydantic Model Reuse Patterns](../docs/PYDANTIC_MODEL_REUSE_PATTERNS.md) - Code sharing techniques
- [FastMCP/PydanticAI Comprehensive Comparison](../docs/FASTMCP_PYDANTICAI_COMPARISON.md) - Deep dive

## Running All Examples

```bash
# Terminal 1: FastAPI
python examples/weather_service/fastapi_impl.py --port 8000

# Terminal 2: FastMCP
python examples/weather_service/fastmcp_impl.py --port 8100

# Terminal 3: PydanticAI (interactive)
python examples/weather_service/pydanticai_impl.py --mode interactive

# Terminal 4: FastA2A
python examples/weather_service/fasta2a_impl.py --port 8300
```

Now you have the same service running on four different ports with four different protocols!

## Testing Examples

### Test FastAPI (HTTP REST)
```bash
curl -X POST http://localhost:8000/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "NYC", "units": "fahrenheit", "include_forecast": true}'
```

### Test FastMCP (MCP Protocol)
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "weather": {"url": "http://localhost:8100/mcp", "transport": "streamable_http"}
})
tools = await client.get_tools()
```

### Test PydanticAI (Interactive)
```bash
python examples/weather_service/pydanticai_impl.py --mode interactive
# You: What's the weather in NYC with forecast?
# Agent: [Uses get_weather tool and responds conversationally]
```

### Test FastA2A (Stateful Context)
```python
import httpx

# Create context
ctx = httpx.post("http://localhost:8300/contexts", json={})
context_id = ctx.json()["id"]

# Send message (context persists across calls)
httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "Weather in NYC?"}]
})
```

## Contributing

When adding new examples:
1. Define Pydantic models in [common/models.py](common/models.py:1)
2. Create `{service}_service/` directory
3. Implement all four versions (FastAPI, FastMCP, PydanticAI, FastA2A)
4. Create `README.md` with side-by-side comparison
5. Keep business logic identical across all versions

## Questions?

- See [CLAUDE.md](../CLAUDE.md) for development guidance
- See [README.md](../README.md) for project overview
- See service-specific READMEs for detailed comparisons

