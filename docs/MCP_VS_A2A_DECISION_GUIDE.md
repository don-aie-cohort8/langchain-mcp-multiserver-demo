# MCP vs A2A Decision Guide

**Quick Answer:** Use **MCP (FastMCP)** for stateless tool calls. Use **A2A (FastA2A)** for stateful conversations.

This guide helps you choose between Model Context Protocol (MCP) and Agent-to-Agent Protocol (A2A) for your project.

---

## Decision Tree

```
START: Do you need conversation state/memory?
│
├─ NO → Do you need to expose tools to LLM systems?
│       │
│       ├─ YES → Use FastMCP (MCP Protocol)
│       │        Examples: Claude Desktop tools, LangChain integrations
│       │
│       └─ NO → Do you need AI reasoning?
│                │
│                ├─ YES → Use PydanticAI (Direct Agent)
│                │        Examples: One-shot agent tasks, automation
│                │
│                └─ NO → Use FastAPI (REST API)
│                         Examples: Traditional web services
│
└─ YES → Use FastA2A (A2A Protocol)
          Examples: Chatbots, customer support, multi-agent systems
```

---

## Quick Comparison

| Question | MCP (FastMCP) | A2A (FastA2A) |
|----------|---------------|---------------|
| **Need conversation memory?** | ❌ No | ✅ Yes |
| **Multi-turn dialogues?** | ❌ No | ✅ Yes |
| **Stateless tool calls?** | ✅ Yes | ❌ Overkill |
| **Task queue needed?** | ❌ No | ✅ Yes |
| **Simple deployment?** | ✅ Yes (single server) | ❌ No (storage + broker + worker) |
| **Integration with Claude Desktop?** | ✅ Yes | ❌ No |
| **Agent collaboration?** | ❌ No | ✅ Yes |
| **Protocol complexity?** | Low | High |

---

## When to Use MCP (FastMCP)

### ✅ Use MCP When:

1. **Exposing stateless tools to LLM systems**
   - Claude Desktop integrations
   - LangChain tool libraries
   - Custom tools for AI agents

2. **Simple function calls via protocol**
   - Weather lookup
   - Database queries
   - File operations
   - API wrappers

3. **No conversation state needed**
   - Each call is independent
   - No memory between calls
   - Stateless operations

4. **Integration requirements**
   - Must work with MCP-compatible clients
   - Tool discovery via protocol
   - Standard MCP transports (stdio, HTTP, SSE)

### ❌ Don't Use MCP When:

- You need multi-turn conversations
- Conversation context must persist
- Building a chatbot
- Agent collaboration is required
- Long-running stateful workflows

### MCP Example: Weather Tool

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather Tools")

@mcp.tool
async def get_weather(location: str, units: str = "celsius") -> dict:
    """Get current weather for a location (stateless)."""
    # Each call is independent, no memory
    return {"location": location, "temp": 22.2, "units": units}

# Start server
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

**Use Case:** Claude Desktop can call this tool, but each call is independent.

---

## When to Use A2A (FastA2A)

### ✅ Use A2A When:

1. **Multi-turn conversations with memory**
   - Chatbots (Slack, Discord, Teams)
   - Customer support agents
   - Personal assistants

2. **Conversation context persistence**
   - Agent remembers previous messages
   - Context spans multiple tasks
   - Conversation threads

3. **Agent collaboration**
   - Multiple agents working on same context
   - Supervisor/worker patterns
   - Team-based architectures

4. **Long-running workflows**
   - Asynchronous task processing
   - Background agent execution
   - Task queues

### ❌ Don't Use A2A When:

- Simple stateless queries (use MCP)
- REST API (use FastAPI)
- One-shot agent calls (use PydanticAI directly)
- No conversation state needed

### A2A Example: Support Bot

```python
from pydantic_ai import Agent

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt="You are a customer support agent. Remember conversation history."
)

@agent.tool_plain
def lookup_order(order_id: str) -> dict:
    """Look up order details."""
    return {"order_id": order_id, "status": "shipped"}

# Convert to A2A (adds state management)
app = agent.to_a2a()

# Deploy as ASGI
# uvicorn module:app
```

**Use Case:** Multi-turn support conversation where agent remembers customer's order ID from earlier.

```
User: "I need help with my order"
Agent: "Sure! What's your order ID?"
User: "ORDER-123"
Agent: [Calls lookup_order] "Your order has shipped!"
User: "When will it arrive?"  # Agent remembers we're talking about ORDER-123
```

---

## Detailed Comparison

### Architecture

**MCP (Stateless):**
```
Client → [MCP Protocol] → Server → Tool → Response
         No persistence between calls
```

**A2A (Stateful):**
```
Client → [A2A Protocol] → Server
                          ↓
                      [Storage] (Tasks + Context)
                          ↓
                      [Broker] (Task Queue)
                          ↓
                      [Worker] (Agent Execution)
                          ↓
                      Response (stored in context)
```

### Deployment Complexity

**MCP:**
```bash
# Single command
python my_mcp_server.py
```

**A2A:**
```bash
# Requires infrastructure
# 1. Storage (Redis/Postgres)
# 2. Broker (Redis/RabbitMQ)
# 3. Worker processes
# 4. ASGI server
uvicorn my_a2a_app:app
```

### Client Interaction

**MCP Client:**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "weather": {"url": "http://localhost:8000/mcp", "transport": "streamable_http"}
})

tools = await client.get_tools()
# Each tool call is independent, no state
```

**A2A Client:**
```python
import httpx

# Create persistent conversation
ctx = httpx.post("http://localhost:8300/contexts", json={})
context_id = ctx.json()["id"]

# Task 1
httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "Hello"}]
})

# Task 2 (same context - stateful!)
httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "Continue our conversation"}]
})
```

---

## Use Case Examples

### MCP Use Cases

#### 1. Claude Desktop Integration
```python
# Expose file system tools to Claude Desktop
@mcp.tool
def list_files(directory: str) -> list[str]:
    """List files in directory."""
    return os.listdir(directory)

@mcp.tool
def read_file(path: str) -> str:
    """Read file contents."""
    with open(path) as f:
        return f.read()

# Claude can now browse and read files (stateless tools)
```

#### 2. Database Query Tool
```python
@mcp.tool
async def query_database(sql: str) -> list[dict]:
    """Execute SQL query (stateless)."""
    async with database.connection() as conn:
        result = await conn.fetch(sql)
        return [dict(row) for row in result]
```

#### 3. API Wrapper
```python
@mcp.tool
async def fetch_user(user_id: int) -> dict:
    """Fetch user from API (stateless)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()
```

### A2A Use Cases

#### 1. Slack Bot
```python
agent = Agent('openai:gpt-4o-mini', system_prompt="You are a Slack bot")

@agent.tool_plain
def get_channel_history(channel_id: str) -> list:
    """Get Slack channel history."""
    return slack_client.get_history(channel_id)

app = agent.to_a2a()

# Conversation persists across Slack messages
# User: "Summarize #general"
# Bot: [Gets history] "Here's the summary..."
# User: "What about yesterday?" (Bot remembers we're talking about #general)
```

#### 2. Customer Support
```python
agent = Agent('openai:gpt-4o-mini', system_prompt="You are a support agent")

@agent.tool_plain
def lookup_ticket(ticket_id: str) -> dict:
    return support_system.get_ticket(ticket_id)

@agent.tool_plain
def update_ticket(ticket_id: str, status: str) -> bool:
    return support_system.update(ticket_id, status)

app = agent.to_a2a()

# Multi-turn support conversation
# User: "I have an issue with my account"
# Agent: "Let me help. What's your ticket ID?"
# User: "TKT-456"
# Agent: [Looks up ticket, remembers context]
# User: "Can you close it?" (Agent knows we're talking about TKT-456)
```

#### 3. Research Assistant
```python
agent = Agent('openai:gpt-4o-mini', system_prompt="You are a research assistant")

@agent.tool_plain
def search_papers(query: str) -> list:
    return arxiv_client.search(query)

@agent.tool_plain
def summarize_paper(paper_id: str) -> str:
    return paper_summarizer.summarize(paper_id)

app = agent.to_a2a()

# Extended research session
# User: "Find papers on transformers"
# Agent: [Searches] "I found 50 papers. Here are the top 10..."
# User: "Summarize the first one" (Agent remembers the search results)
# User: "Compare it to the third paper" (Agent maintains research context)
```

---

## Migration Path

### From MCP to A2A (Adding State)

**Before (MCP - Stateless):**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Assistant")

@mcp.tool
def answer_question(question: str) -> str:
    return f"Answer: {question}"

mcp.run(transport="streamable-http")
```

**After (A2A - Stateful):**
```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-4o-mini', system_prompt='Be helpful')

@agent.tool_plain
def answer_question(question: str) -> str:
    return f"Answer: {question}"

app = agent.to_a2a()  # Now stateful!
```

**What Changed:**
1. MCP → PydanticAI agent
2. Added `agent.to_a2a()` for state management
3. Now supports multi-turn conversations

---

## Cost/Complexity Trade-offs

| Aspect | MCP | A2A |
|--------|-----|-----|
| **Infrastructure** | Single server | Storage + Broker + Worker |
| **Deployment** | Simple (`python server.py`) | Complex (ASGI + infrastructure) |
| **Scaling** | Horizontal (multiple servers) | Vertical (workers) + infrastructure scaling |
| **Monitoring** | Basic (HTTP logs) | Advanced (task queue metrics) |
| **Cost** | Low (single process) | High (multiple services) |
| **State Management** | None | Redis/Postgres/etc. |
| **Development Speed** | Fast (like FastAPI) | Slower (infrastructure setup) |

---

## Hybrid Approaches

### MCP Server with PydanticAI Agent

You can expose a PydanticAI agent as an MCP tool (stateless wrapping of agent):

```python
from mcp.server.fastmcp import FastMCP
from pydantic_ai import Agent

mcp = FastMCP("AI Tools")
agent = Agent('openai:gpt-4o-mini', system_prompt='Be concise')

@mcp.tool
async def ask_ai(question: str) -> str:
    """Ask AI a question (stateless, each call is independent)."""
    result = await agent.run(question)
    return result.output

# Exposes agent capabilities as stateless MCP tool
```

**Use Case:** Claude Desktop can ask your agent questions, but no conversation memory.

### A2A Server with MCP Tools

A FastA2A agent can consume MCP servers:

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

mcp_server = MCPServerHTTP(url='http://localhost:8000/sse')

agent = Agent(
    'openai:gpt-4o-mini',
    mcp_servers=[mcp_server]  # Agent can call MCP tools
)

app = agent.to_a2a()

# Stateful agent that can call stateless MCP tools
```

**Use Case:** Chatbot (stateful) that uses MCP tools (stateless functions).

---

## Checklist

### Choose MCP if:

- [ ] Tools are stateless
- [ ] No conversation memory needed
- [ ] Integrating with Claude Desktop or LangChain
- [ ] Simple deployment preferred
- [ ] Each call is independent

### Choose A2A if:

- [ ] Multi-turn conversations required
- [ ] Conversation context must persist
- [ ] Building a chatbot
- [ ] Agent collaboration needed
- [ ] Complex deployment is acceptable

### Choose PydanticAI (Direct) if:

- [ ] Need agent reasoning
- [ ] No protocol required (library usage)
- [ ] One-shot tasks
- [ ] Don't need to expose as service

### Choose FastAPI if:

- [ ] Traditional REST API
- [ ] No AI/agent features needed
- [ ] Standard HTTP endpoints
- [ ] OpenAPI documentation required

---

## Summary

| Framework | Protocol | State | Deployment | Best For |
|-----------|----------|-------|------------|----------|
| **FastAPI** | HTTP REST | Stateless | Simple | Web APIs |
| **FastMCP** | MCP | Stateless | Simple | LLM tools |
| **PydanticAI** | Direct | Stateless | N/A (library) | Agent tasks |
| **FastA2A** | A2A | **Stateful** | Complex | Chatbots |

**Golden Rule:** If you need state, use FastA2A. Otherwise, use FastMCP (for tools) or PydanticAI (for agents).

---

## See Also

- [FastMCP/PydanticAI Comparison](FASTMCP_PYDANTICAI_COMPARISON.md) - Technical deep dive
- [Pydantic Model Reuse Patterns](PYDANTIC_MODEL_REUSE_PATTERNS.md) - Code sharing techniques
- [Weather Service Examples](../examples/weather_service/README.md) - Side-by-side implementations

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Author:** AIE Cohort 8 Educational Materials
