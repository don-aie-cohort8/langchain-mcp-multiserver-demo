# FastMCP and PydanticAI/FastA2A: Comprehensive Comparison

This document provides a deep technical comparison of FastMCP (for building MCP servers) and PydanticAI/FastA2A (for agent-to-agent communication), demonstrating how both leverage Pydantic models and familiar Python patterns.

**Target Audience:** AIE Cohort 8 students with FastAPI and Pydantic experience

**Key Insight:** If you know FastAPI, you already understand 95% of both FastMCP and PydanticAI. The primary difference is conceptual (RPC vs agents vs stateful agents), not syntactical.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Similarities](#core-similarities)
3. [Framework Comparison Matrix](#framework-comparison-matrix)
4. [Pydantic Models as Universal Foundation](#pydantic-models-as-universal-foundation)
5. [FastMCP Deep Dive](#fastmcp-deep-dive)
6. [PydanticAI Deep Dive](#pydanticai-deep-dive)
7. [FastA2A Deep Dive](#fasta2a-deep-dive)
8. [When to Use Each](#when-to-use-each)
9. [Migration Examples](#migration-examples)
10. [Common Pitfalls](#common-pitfalls)

---

## Executive Summary

### The Three Frameworks

| Framework | Purpose | Protocol | State | Best For |
|-----------|---------|----------|-------|----------|
| **FastMCP** | MCP servers | Model Context Protocol | Stateless | LLM tool integration (Claude, LangChain) |
| **PydanticAI** | AI agents | Direct/MCP client | Stateless | Agent workflows, natural language tasks |
| **FastA2A** | Stateful agents | Agent2Agent | Stateful | Chatbots, multi-turn conversations |

### Key Similarities

All three frameworks:
- Use Pydantic models for validation and schema generation
- Support async/await patterns
- Use decorator-based tool/function registration
- Generate schemas automatically from type annotations
- Feel familiar to FastAPI developers

### Key Differences

- **FastMCP**: RPC-style tool provisioning (like FastAPI for AI tools)
- **PydanticAI**: Agent orchestration with LLM reasoning
- **FastA2A**: Adds persistent state and task queues to PydanticAI

---

## Core Similarities

### 1. Pydantic-First Design

All three frameworks treat Pydantic models as first-class citizens:

```python
from pydantic import BaseModel, Field

class WeatherQuery(BaseModel):
    location: str = Field(description="City name")
    units: Literal["celsius", "fahrenheit"] = "celsius"

# This SAME model works in:
# - FastMCP tool parameters
# - PydanticAI agent tool parameters
# - FastA2A task payloads
# - FastAPI request bodies (for comparison)
```

### 2. Decorator Patterns

```python
# FastAPI (for reference)
@app.post("/weather")
async def get_weather(query: WeatherQuery) -> WeatherResponse:
    ...

# FastMCP
@mcp.tool
async def get_weather(query: WeatherQuery) -> WeatherResponse:
    ...

# PydanticAI
@agent.tool_plain
def get_weather(query: WeatherQuery) -> WeatherResponse:
    ...

# FastA2A (same as PydanticAI, different deployment)
@agent.tool_plain
def get_weather(query: WeatherQuery) -> WeatherResponse:
    ...
```

**Observation:** The function body is IDENTICAL across all frameworks.

### 3. Async/Await Support

```python
# All frameworks support async patterns
@mcp.tool
async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### 4. Schema Auto-Generation

All frameworks automatically generate JSON schemas from Pydantic models for:
- Parameter validation
- Documentation (OpenAPI, MCP tool descriptions, agent tool schemas)
- Client code generation

---

## Framework Comparison Matrix

| Aspect | FastAPI | FastMCP | PydanticAI | FastA2A |
|--------|---------|---------|------------|---------|
| **Server Init** | `FastAPI()` | `FastMCP()` | `Agent()` | `agent.to_a2a()` |
| **Decorator** | `@app.post()` | `@mcp.tool` | `@agent.tool_plain` | Same as PydanticAI |
| **Error Type** | `HTTPException` | `ToolError` | `ValueError` | `ValueError` |
| **Protocol** | HTTP REST | MCP | Direct calls | A2A |
| **State** | Stateless | Stateless | Stateless | **Stateful** |
| **Discovery** | OpenAPI `/docs` | MCP `list_tools()` | Programmatic | A2A protocol |
| **Async Support** | ✓ | ✓ | ✓ | ✓ |
| **Pydantic Models** | ✓ SAME | ✓ SAME | ✓ SAME | ✓ SAME |
| **Validation** | ✓ SAME | ✓ SAME | ✓ SAME | ✓ SAME |
| **Business Logic** | ✓ SAME | ✓ SAME | ✓ SAME | ✓ SAME |
| **Deployment** | Uvicorn | `mcp.run()` | Direct usage | Uvicorn |
| **Use Case** | REST APIs | LLM tools | Agent tasks | Chatbots |

---

## Pydantic Models as Universal Foundation

### Shared Model Example

```python
# examples/common/models.py
from pydantic import BaseModel, Field
from typing import Literal

class WeatherQuery(BaseModel):
    """Universal weather query model."""
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = "celsius"
    include_forecast: bool = False

class WeatherResponse(BaseModel):
    """Universal weather response model."""
    location: str
    current_temp: float
    units: str
    conditions: str
    forecast: list[dict] | None = None
```

### Usage Across Frameworks

```python
# FastAPI
@app.post("/weather", response_model=WeatherResponse)
async def get_weather(query: WeatherQuery) -> WeatherResponse:
    return WeatherResponse(location=query.location, ...)

# FastMCP
@mcp.tool
async def get_weather(query: WeatherQuery) -> WeatherResponse:
    return WeatherResponse(location=query.location, ...)

# PydanticAI
@agent.tool_plain
def get_weather(query: WeatherQuery) -> WeatherResponse:
    return WeatherResponse(location=query.location, ...)
```

**Key Insight:** The function signature and body are IDENTICAL. Only the decorator changes.

---

## FastMCP Deep Dive

### What is FastMCP?

FastMCP is a framework for building Model Context Protocol (MCP) servers. Think of it as "FastAPI for AI tools."

### Tool Definition

```python
from mcp.server.fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("My Server")

@mcp.tool
async def calculate(a: float, b: float, operation: str) -> float:
    """Perform calculation."""
    if operation == "divide" and b == 0:
        raise ToolError("Division by zero")

    operations = {"add": a + b, "divide": a / b}
    return operations[operation]
```

### Pydantic Integration Levels

#### Level 1: Simple Types with Field Annotations

```python
from typing import Annotated
from pydantic import Field

@mcp.tool
def search(
    query: Annotated[str, Field(description="Search term", min_length=1)],
    limit: Annotated[int, Field(ge=1, le=100)] = 10
) -> list:
    ...
```

#### Level 2: Pydantic Model as Parameter

```python
class SearchParams(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(ge=1, le=100, default=10)

@mcp.tool
def search(params: SearchParams) -> list:
    # FastMCP "unpacks" the model to individual fields in the schema
    ...
```

#### Level 3: Pydantic Models for Outputs

```python
@dataclass
class Product:
    id: int
    name: str
    price: float

@mcp.tool
def get_product(product_id: str) -> Product:
    return Product(id=1, name="Widget", price=29.99)
```

### Transport Options

```python
# stdio (for Claude Desktop, subprocesses)
mcp.run(transport="stdio")

# streamable-http (for web services)
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)

# SSE (server-sent events)
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

### Integration with LangChain

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "my_server": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http"
    }
})

tools = await client.get_tools()  # Returns LangChain BaseTool instances
```

---

## PydanticAI Deep Dive

### What is PydanticAI?

PydanticAI is a framework for building AI agents with tools, using Pydantic for type safety and validation.

### Agent Creation

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt="You are a helpful assistant."
)
```

### Tool Definition

```python
@agent.tool_plain  # No context dependencies
def calculate(a: float, b: float, operation: str) -> float:
    """Perform calculation."""
    operations = {"add": a + b, "subtract": a - b}
    return operations[operation]

@agent.tool  # With context (RunContext)
def get_user_data(ctx: RunContext[UserDeps]) -> dict:
    """Get user data from context."""
    return {"user_id": ctx.deps.user_id}
```

### Running Agents

```python
# Synchronous
result = agent.run_sync("Calculate 5 + 3")
print(result.data)  # "8"

# Asynchronous
result = await agent.run("Calculate 5 + 3")
print(result.data)
```

### PydanticAI as MCP Client

```python
from pydantic_ai.mcp import MCPServerHTTP

mcp_server = MCPServerHTTP(url='http://127.0.0.1:8000/sse')

agent = Agent(
    'anthropic:claude-3-5-sonnet',
    mcp_servers=[mcp_server]  # Agent can call MCP tools
)

async with agent.run_mcp_servers():
    result = await agent.run("Use the weather tool for NYC")
```

### PydanticAI as MCP Server

```python
from mcp.server.fastmcp import FastMCP

server = FastMCP('AI Assistant')
assistant = Agent('openai:gpt-4o-mini', system_prompt='Be helpful')

@server.tool()
async def ask_assistant(question: str) -> str:
    """Ask the AI assistant (exposes agent as MCP tool)."""
    result = await assistant.run(question)
    return result.output
```

---

## FastA2A Deep Dive

### What is FastA2A?

FastA2A is PydanticAI's protocol for **stateful** agent-to-agent communication. It adds task queues and conversation context to PydanticAI agents.

### Key Differences from PydanticAI

| Aspect | PydanticAI | FastA2A |
|--------|------------|---------|
| State | Stateless (each call independent) | Stateful (context persists) |
| Execution | Synchronous | Asynchronous task queue |
| Infrastructure | Simple (agent only) | Complex (storage + broker + worker) |
| Use Case | One-shot agent tasks | Multi-turn conversations |

### Architecture Components

```python
from fasta2a import FastA2A, Worker
from fasta2a.broker import InMemoryBroker
from fasta2a.storage import InMemoryStorage

# 1. Storage: Persists tasks and conversation context
storage = InMemoryStorage()

# 2. Broker: Manages task queue
broker = InMemoryBroker()

# 3. Worker: Executes agent logic
class MyWorker(Worker):
    async def run_task(self, params):
        task = await self.storage.load_task(params['id'])
        # Run agent with full conversation context
        ...

# 4. FastA2A App: ASGI application
app = FastA2A(storage=storage, broker=broker)
```

### Convenience Method

For PydanticAI agents, FastA2A setup is automatic:

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o-mini', system_prompt='Be helpful')

# Automatically creates storage, broker, worker
app = agent.to_a2a()

# Deploy as ASGI app
# uvicorn my_module:app
```

### Task vs Context Models

**Task:** Single agent execution
```json
{
  "id": "task_123",
  "context_id": "conv_456",
  "state": "running",
  "messages": [{"role": "user", "content": "Hello"}]
}
```

**Context:** Conversation thread spanning multiple tasks
```json
{
  "id": "conv_456",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"},
    {"role": "user", "content": "Tell me about Python"}
  ]
}
```

### Multi-Turn Conversation Example

```python
import httpx

# Create conversation
ctx = httpx.post("http://localhost:8300/contexts", json={})
context_id = ctx.json()["id"]

# Task 1
httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "Weather in NYC?"}]
})

# Task 2 (same context - agent remembers!)
httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,  # SAME context
    "messages": [{"role": "user", "content": "How about tomorrow?"}]
})
```

---

## When to Use Each

### Use FastMCP When:

✅ Exposing stateless tools to LLM systems
✅ Integrating with Claude Desktop
✅ Building tools for LangChain agents
✅ Simple function calls via protocol
✅ No conversation state needed

**Example Use Cases:**
- Weather lookup tool
- Database query tool
- File system operations
- API wrappers

### Use PydanticAI When:

✅ Building AI agents with reasoning
✅ Combining multiple tools in workflows
✅ Natural language understanding needed
✅ Direct agent usage (not as service)
✅ Stateless agent tasks

**Example Use Cases:**
- Data analysis agents
- Code generation agents
- Research assistants
- One-shot automation tasks

### Use FastA2A When:

✅ Multi-turn conversations with memory
✅ Building chatbots (Slack, Discord)
✅ Agent collaboration (shared context)
✅ Long-running workflows
✅ Conversation history required

**Example Use Cases:**
- Customer support bots
- Personal assistants
- Multi-agent systems
- Stateful workflows

---

## Migration Examples

### FastAPI → FastMCP

**Before (FastAPI):**
```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/calculate")
async def calculate(a: float, b: float) -> float:
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return a / b
```

**After (FastMCP):**
```python
from mcp.server.fastmcp import FastMCP
from fastmcp.exceptions import ToolError

mcp = FastMCP("Calculator")

@mcp.tool
async def calculate(a: float, b: float) -> float:
    if b == 0:
        raise ToolError("Division by zero")
    return a / b
```

**Changes:**
1. `FastAPI()` → `FastMCP()`
2. `@app.post()` → `@mcp.tool`
3. `HTTPException` → `ToolError`
4. Remove route path (`"/calculate"`)

### FastMCP → PydanticAI

**Before (FastMCP):**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Assistant")

@mcp.tool
def answer_question(question: str) -> str:
    return f"The answer is: {question}"
```

**After (PydanticAI):**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o-mini', system_prompt='Be helpful')

@agent.tool_plain
def answer_question(question: str) -> str:
    return f"The answer is: {question}"
```

**Changes:**
1. `FastMCP()` → `Agent()`
2. `@mcp.tool` → `@agent.tool_plain`
3. Add system prompt for agent behavior

### PydanticAI → FastA2A

**Before (PydanticAI):**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o-mini', system_prompt='Be helpful')

@agent.tool_plain
def get_data() -> dict:
    return {"data": "value"}

# Direct usage
result = await agent.run("Get me the data")
```

**After (FastA2A):**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o-mini', system_prompt='Be helpful')

@agent.tool_plain
def get_data() -> dict:
    return {"data": "value"}

# Convert to A2A (adds state management)
app = agent.to_a2a()

# Deploy as ASGI
# uvicorn module:app
```

**Changes:**
1. Add `app = agent.to_a2a()`
2. Deploy as ASGI application
3. Client uses A2A protocol (tasks/contexts)

---

## Common Pitfalls

### 1. Mixing Decorators

❌ **Don't:**
```python
@mcp.tool  # Wrong - this is for FastMCP
def my_agent_tool():
    ...

agent = Agent(...)
```

✅ **Do:**
```python
agent = Agent(...)

@agent.tool_plain  # Correct - this is for PydanticAI
def my_agent_tool():
    ...
```

### 2. Forgetting Type Annotations

❌ **Don't:**
```python
@mcp.tool
def calculate(a, b):  # Missing types!
    return a + b
```

✅ **Do:**
```python
@mcp.tool
def calculate(a: float, b: float) -> float:
    return a + b
```

### 3. Blocking I/O in Async Functions

❌ **Don't:**
```python
@mcp.tool
async def fetch_data():
    result = requests.get("https://api.example.com")  # Blocking!
    return result.json()
```

✅ **Do:**
```python
@mcp.tool
async def fetch_data():
    async with httpx.AsyncClient() as client:
        result = await client.get("https://api.example.com")
        return result.json()
```

### 4. Overusing State (FastA2A)

❌ **Don't use FastA2A for:**
- Simple stateless queries
- One-shot function calls
- No conversation context needed

✅ **Do use FastMCP/PydanticAI instead** for stateless operations.

---

## Conclusion

### Key Takeaways

1. **Pydantic models are the common language** across FastAPI, FastMCP, PydanticAI, and FastA2A
2. **Business logic is portable** - Write once, deploy in multiple frameworks
3. **FastAPI knowledge transfers directly** - Same patterns, different protocols
4. **Choose based on use case:**
   - REST API → FastAPI
   - LLM tools → FastMCP
   - Agent tasks → PydanticAI
   - Stateful conversations → FastA2A

5. **The learning curve is conceptual, not syntactical:**
   - Syntax is familiar (Pydantic, decorators, async)
   - Concepts differ (RPC vs agents vs stateful workflows)

### Recommended Learning Path

1. **Start with FastAPI** (already familiar)
2. **Move to FastMCP** (95% similar, different protocol)
3. **Explore PydanticAI** (adds agent reasoning layer)
4. **Graduate to FastA2A** (when state is needed)

### Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [PydanticAI Documentation](https://ai.pydantic.dev)
- [Weather Service Examples](../examples/weather_service/README.md)
- [MCP vs A2A Decision Guide](MCP_VS_A2A_DECISION_GUIDE.md)
- [Pydantic Model Reuse Patterns](PYDANTIC_MODEL_REUSE_PATTERNS.md)

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Author:** AIE Cohort 8 Educational Materials
