# Component Inventory

## Overview

**Project Name:** `langchain-mcp-multiserver-demo`
**Version:** 0.1.0
**Python Requirements:** >=3.13
**Purpose:** Educational demonstration of MCP (Model Context Protocol) integration patterns with LangChain

This project showcases how to integrate multiple MCP servers with LangChain agents, demonstrating:
- Multi-server architecture with heterogeneous transports (stdio, streamable-http)
- Dynamic tool discovery and agent orchestration
- LangChain tool conversion to MCP format
- Display utilities for formatting agent responses
- Reference patterns for building LLM agents with MCP

The codebase consists of three primary layers:
1. **MCP Servers** - Backend services exposing tools via MCP protocol
2. **Client Integration** - LangChain-based clients that consume MCP tools
3. **Supporting Infrastructure** - Utilities, configuration, and examples

---

## Public API

### Modules

#### 1. `servers` Package
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/servers/__init__.py`
**Purpose:** Container package for MCP server implementations

**Public Exports:**
- `__version__ = "0.1.0"` (line 13)
- Package-level documentation describing all server modules (lines 1-11)

**Submodules:**
- `math_server.py` - Basic arithmetic operations (stdio transport)
- `weather_server.py` - Mock weather service (streamable-http transport)
- `wrap_langchain_tools_server.py` - LangChain tool conversion demo (streamable-http transport)

#### 2. `clients.display_utils` Module
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/clients/display_utils.py`
**Purpose:** Utility functions for displaying LangChain agent responses

**Public Functions:**
- `display_agent_response()` (lines 9-96)
- `get_final_answer()` (lines 99-129)
- `print_tools_summary()` (lines 132-153)

#### 3. `mcp_simple_streamablehttp_stateless` Package
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/examples/servers/streamable-http-stateless/mcp_simple_streamablehttp_stateless/`
**Purpose:** Example MCP server using streamable HTTP transport in stateless mode

**Public Entry Points:**
- `server.main()` - CLI entry point (lines 35-187)
- Package exports via `__main__.py` (lines 1-4)

---

### Classes

This project primarily uses functional programming patterns and does not define custom classes. Key framework classes used include:

#### Framework Classes (External Dependencies)

| Class | Source | Purpose | Usage Location |
|-------|--------|---------|----------------|
| `FastMCP` | `mcp.server.fastmcp` | High-level MCP server builder | `servers/math_server.py:4`, `servers/weather_server.py:25`, `servers/wrap_langchain_tools_server.py:46` |
| `MultiServerMCPClient` | `langchain_mcp_adapters.client` | Client for connecting to multiple MCP servers | `clients/integration_test.py:87`, `clients/integration_test_mcp_json.py:92` |
| `Server` | `mcp.server.lowlevel` | Low-level MCP server implementation | `examples/.../server.py:56` |
| `StreamableHTTPSessionManager` | `mcp.server.streamable_http_manager` | Manages HTTP sessions for MCP | `examples/.../server.py:138` |
| `AIMessage`, `HumanMessage`, `ToolMessage` | `langchain_core.messages` | LangChain message types | `clients/display_utils.py:6` |

---

### Functions

#### Server Functions

##### 1. `add(a: int, b: int) -> int`
**File:** `servers/math_server.py:8-10`
**Type:** MCP Tool (decorated with `@mcp.tool()`)
**Purpose:** Add two numbers
**Parameters:**
- `a` (int): First number
- `b` (int): Second number
**Returns:** Sum of a and b

**Also appears in:**
- `servers/wrap_langchain_tools_server.py:11-13` (as LangChain tool)
- `examples/.../server.py:74-80` (as MCP handler)

##### 2. `multiply(a: int, b: int) -> int`
**File:** `servers/math_server.py:14-16`
**Type:** MCP Tool (decorated with `@mcp.tool()`)
**Purpose:** Multiply two numbers
**Parameters:**
- `a` (int): First number
- `b` (int): Second number
**Returns:** Product of a and b

**Also appears in:**
- `servers/wrap_langchain_tools_server.py:17-19` (as LangChain tool)
- `examples/.../server.py:81-87` (as MCP handler)

##### 3. `get_weather(location: str) -> str`
**File:** `servers/weather_server.py:28-37`
**Type:** Async MCP Tool (decorated with `@mcp.tool()`)
**Purpose:** Get weather for a location (returns mock data)
**Parameters:**
- `location` (str): Location to get weather for (e.g., "NYC", "London", "Tokyo")
**Returns:** Weather description string

#### Client Utility Functions

##### 4. `display_agent_response(response, show_full_trace=True, show_token_usage=False, return_final_answer=False)`
**File:** `clients/display_utils.py:9-96`
**Purpose:** Display formatted agent response with message trace
**Parameters:**
- `response` (Dict[str, Any]): Agent response dict with 'messages' key
- `show_full_trace` (bool): If True, show all messages; if False, only final answer (default: True)
- `show_token_usage` (bool): If True, show token usage statistics for AI messages (default: False)
- `return_final_answer` (bool): If True, return the final answer text (default: False)
**Returns:** Final answer text if `return_final_answer=True`, else None

**Key Features:**
- Formats different message types (AIMessage, HumanMessage, ToolMessage)
- Displays tool call sequences
- Shows token usage metadata when available
- Supports both verbose and minimal display modes

##### 5. `get_final_answer(response: Dict[str, Any]) -> Optional[str]`
**File:** `clients/display_utils.py:99-129`
**Purpose:** Extract just the final answer from an agent response without printing
**Parameters:**
- `response` (Dict[str, Any]): Agent response dict with 'messages' key
**Returns:** The final answer text, or None if no answer found

**Implementation:** Iterates in reverse through messages to find the most recent AIMessage without tool calls

##### 6. `print_tools_summary(tools: list) -> None`
**File:** `clients/display_utils.py:132-153`
**Purpose:** Print a summary of available tools
**Parameters:**
- `tools` (list): List of LangChain tools
**Returns:** None (prints to stdout)

**Output Format:**
```
======================================================================
AVAILABLE TOOLS (N total)
======================================================================

01. tool_name
    └─ Tool description
...
```

#### Example Implementation Functions

##### 7. `main()` (Integration Test)
**File:** `clients/integration_test.py:66-274`
**Type:** Async function
**Purpose:** Main test orchestrator for comprehensive MCP integration testing
**Test Cases:**
1. Multi-step reasoning with full trace display (lines 136-143)
2. Cross-server tool invocation with minimal display (lines 166-178)
3. Programmatic answer extraction (lines 201-217)
4. Complex multi-step sequential reasoning (lines 241-255)

##### 8. `main()` (MCP JSON Integration)
**File:** `clients/integration_test_mcp_json.py:90-111`
**Type:** Async function
**Purpose:** Integration test using hard-coded MCP server configuration from .mcp.json

##### 9. `show_mcp_tools_metadata(tools)`
**File:** `clients/integration_test_mcp_json.py:15-33`
**Purpose:** Print key metadata that `create_agent()` sees for each MCP tool
**Output:** Shows tool name, description, provider, transport, and endpoint

##### 10. `hardcoded_mcp_config() -> Dict[str, Dict[str, Any]]`
**File:** `clients/integration_test_mcp_json.py:40-87`
**Purpose:** Hard-coded MCP server definitions (ported from .mcp.json) for MultiServerMCPClient
**Returns:** Dictionary mapping server names to configuration dictionaries

**Configured Servers:**
- `mcp-server-time` - Time server with LA timezone
- `sequential-thinking` - Sequential thinking MCP server
- `Context7` - Upstash Context7 server with CalCom integration

##### 11. `main()` (Streamable HTTP Server)
**File:** `examples/.../server.py:35-187`
**Type:** Click command decorated function
**Purpose:** Run the MCP server with streamable HTTP transport
**Parameters:**
- `--port` (int): Port to listen on (default: 3000)
- `--log-level` (str): Logging level (default: "INFO")
- `--json-response` (bool): Enable JSON responses instead of SSE streams (default: False)
**Returns:** Exit code (0 for success)

##### 12. `call_tool(name: str, arguments: dict)`
**File:** `examples/.../server.py:59-89`
**Type:** Async function (decorated with `@app.call_tool()`)
**Purpose:** Handle tool calls for math operations in low-level MCP server

##### 13. `list_tools()`
**File:** `examples/.../server.py:92-135`
**Type:** Async function (decorated with `@app.list_tools()`)
**Purpose:** List all available tools provided by the server
**Returns:** List of `types.Tool` objects with JSON schemas

---

## Internal Implementation

### Core Modules

#### 1. MCP Server Implementations

##### `servers/math_server.py`
**Lines:** 1-21
**Purpose:** Minimal MCP server demonstrating stdio transport
**Key Components:**
- FastMCP instance creation (line 4)
- Tool decorators for add and multiply (lines 7, 13)
- Main entry point with stdio transport (lines 19-20)

**Transport:** stdio (suitable for subprocess-based integration)

##### `servers/weather_server.py`
**Lines:** 1-61
**Purpose:** Mock weather service demonstrating streamable-http transport
**Key Components:**
- Comprehensive module documentation (lines 1-20)
- Async tool implementation (lines 28-37)
- Command-line argument parsing with argparse (lines 40-53)
- Host/port configuration (lines 56-57)
- Streamable-http transport (line 60)

**CLI Arguments:**
- `--port` (default: 8000)
- `--host` (default: "127.0.0.1")

##### `servers/wrap_langchain_tools_server.py`
**Lines:** 1-55
**Purpose:** Demonstrate LangChain to MCP tool conversion
**Key Components:**
- Environment variable loading (lines 7-8)
- LangChain tool decorators (lines 10, 16)
- `to_fastmcp()` conversion utility (lines 22-23)
- FastMCP instance with converted tools (lines 46-51)
- Streamable-http transport (line 54)

**Integration Pattern:** Shows how to wrap existing LangChain tools for use in MCP servers

#### 2. Client Integration Layer

##### `clients/integration_test.py`
**Lines:** 1-275
**Purpose:** Comprehensive integration test suite demonstrating MCP workflow
**Architecture:**
- Multi-server connection configuration (lines 87-98)
- Tool discovery from heterogeneous services (lines 102-107)
- LangGraph ReAct agent creation (line 113)
- Multiple test cases with different display patterns (lines 136-255)

**Test Coverage:**
- Multi-step reasoning
- Cross-server tool invocation
- Programmatic answer extraction
- Sequential instruction following

**Educational Value:**
- Reference implementation for production applications
- Demonstrates all display_utils features
- Shows proper async/await patterns

##### `clients/integration_test_mcp_json.py`
**Lines:** 1-112
**Purpose:** Integration test using .mcp.json configuration
**Key Differences from integration_test.py:**
- Uses hard-coded MCP configuration from .mcp.json (lines 40-87)
- Demonstrates stdio transport with subprocess servers (lines 49-78)
- Shows environment variable expansion pattern (line 76)
- Includes metadata inspection utility (lines 15-33)

**Use Case:** Testing MCP servers configured via Claude Desktop's .mcp.json format

#### 3. Low-Level MCP Server Example

##### `examples/servers/streamable-http-stateless/mcp_simple_streamablehttp_stateless/server.py`
**Lines:** 1-188
**Purpose:** Advanced example showing low-level MCP server API
**Key Components:**
- Low-level `Server` class usage (line 56)
- Manual tool registration with decorators (lines 58, 91)
- `StreamableHTTPSessionManager` configuration (lines 138-143)
- Starlette ASGI application integration (lines 175-181)
- Uvicorn server runner (line 185)

**Advanced Features:**
- Stateless mode configuration (line 142)
- JSON response vs SSE streaming toggle (line 141)
- Lifespan context manager (lines 158-172)
- Click-based CLI (lines 22-39)

---

### Utility Modules

#### `clients/display_utils.py`
**Lines:** 1-154
**Purpose:** Formatting utilities for agent responses
**Implementation Details:**

##### Message Type Handling
- **AIMessage** (lines 45-69):
  - Detects tool calls (modern and legacy formats)
  - Extracts final answers
  - Shows token usage metadata when available
- **ToolMessage** (lines 71-79):
  - Displays tool results with success/error indicators
  - Shows checkmark (✓) for success, cross (❌) for errors
- **HumanMessage** (lines 81-83):
  - Shows user input messages

##### Display Modes
- **Full Trace** (lines 37-89): Shows all messages with numbering and formatting
- **Minimal** (lines 92-93): Shows only final answer with emoji indicator
- **Programmatic** (lines 99-129): Silent extraction for integration

##### Token Usage Display
- Input tokens, output tokens, and total (lines 65-69)
- Only displayed when `show_token_usage=True` and metadata available

---

### Support Components

#### Configuration Files

##### 1. `pyproject.toml`
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/pyproject.toml`
**Purpose:** Project metadata and dependency specification

**Key Sections:**
- **[project]** (lines 1-19):
  - name: "langchain-mcp-multiserver-demo"
  - version: "0.1.0"
  - requires-python: ">=3.13"

- **dependencies** (lines 7-19):
  - `claude-agent-sdk>=0.1.4`
  - `langchain>=0.3.19`
  - `langchain-mcp-adapters>=0.1.11`
  - `langchain-openai>=0.3.7`
  - `langgraph>=0.6.7`
  - `mcp[cli]>=1.6.0`
  - `python-dotenv>=1.1.0`
  - And others (numpy, openai, tavily-python, ipykernel)

##### 2. `.mcp.json`
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/.mcp.json`
**Purpose:** MCP server configuration for Claude Desktop integration

**Configured Servers:**
1. **mcp-server-time** (lines 3-10):
   - Command: `uvx mcp-server-time`
   - Args: `--local-timezone=America/Los_Angeles`

2. **sequential-thinking** (lines 11-17):
   - Command: `npx -y @modelcontextprotocol/server-sequential-thinking`

3. **Context7** (lines 18-27):
   - Command: `npx -y @upstash/context7-mcp`
   - Requires: `CALCOM_API_KEY` environment variable

4. **ai-docs-server** (lines 28-56):
   - Command: `uvx mcpdoc`
   - Fetches documentation from: ModelContextProtocol, FastMCP, LangChain, LangGraph, Anthropic
   - Transport: stdio

5. **ai-docs-server-full** (lines 57-85):
   - Same as ai-docs-server but with full documentation URLs

##### 3. `.env.example`
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/.env.example`
**Purpose:** Template for environment variables

**Required Variables:**
- `OPENAI_API_KEY` - OpenAI API authentication
- `LANGSMITH_TRACING` - Enable LangSmith tracing (true/false)
- `LANGSMITH_PROJECT` - LangSmith project name
- `LANGSMITH_API_KEY` - LangSmith API authentication
- `CALCOM_API_KEY` - CalCom API for Context7 integration

##### 4. Example Server Configuration
**File:** `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/examples/servers/streamable-http-stateless/pyproject.toml`

**Project:**
- name: "mcp-simple-streamablehttp-stateless"
- version: "0.1.0"
- requires-python: ">=3.10"

**Script Entry Point:**
```toml
[project.scripts]
mcp-simple-streamablehttp-stateless = "mcp_simple_streamablehttp_stateless.server:main"
```

**Dependencies:**
- anyio>=4.5
- click>=8.1.0
- httpx>=0.27
- mcp
- starlette
- uvicorn

#### Documentation Files

##### Technical Documentation
1. **README.md** (286 lines) - Main project documentation
2. **docs/TRANSPORT_COMPARISON.md** - MCP transport comparison
3. **docs/LANGGRAPH_MIGRATION_V1.md** - Migration guide for LangGraph 1.0
4. **docs/langgraph_react_agent_migration_walkthrough.md** - Detailed migration walkthrough
5. **docs/integration_test_mcp_json.md** - Output documentation for JSON integration test

##### Storytelling Templates (storytelling/templates/)
- ARCHITECTURE_OVERVIEW_TEMPLATE.md
- LEARNING_REFLECTION_TEMPLATE.md
- LINKEDIN_POST_TEMPLATE.md
- PROJECT_CONTEXT_TEMPLATE.md
- REPO_OVERVIEW_TEMPLATE.md
- SLIDES_TEMPLATE.md
- VIDEO_SCRIPT_TEMPLATE.md

##### Generated Outputs (storytelling/output/)
- ARCHITECTURE_OVERVIEW.md
- LEARNING_REFLECTION.md
- LINKEDIN_POST.md
- PROJECT_CONTEXT.md
- REPO_OVERVIEW.md
- SLIDES.md
- VIDEO_SCRIPT.md

---

## Entry Points

### Main Scripts

#### 1. Math Server (stdio)
**File:** `servers/math_server.py:19-20`
**Execution:**
```bash
python servers/math_server.py
```
**Transport:** stdio (subprocess-based)
**Tools Provided:** add, multiply

#### 2. Weather Server (streamable-http)
**File:** `servers/weather_server.py:39-60`
**Execution:**
```bash
python servers/weather_server.py [--host HOST] [--port PORT]
```
**Default:** http://127.0.0.1:8000/mcp
**Transport:** streamable-http
**Tools Provided:** get_weather

#### 3. LangChain Tools Server (streamable-http)
**File:** `servers/wrap_langchain_tools_server.py:25-54`
**Execution:**
```bash
python servers/wrap_langchain_tools_server.py [--host HOST] [--port PORT]
```
**Default:** http://127.0.0.1:8001/mcp
**Transport:** streamable-http
**Tools Provided:** add, multiply (converted from LangChain tools)

#### 4. Integration Test Suite
**File:** `clients/integration_test.py:273-274`
**Execution:**
```bash
python clients/integration_test.py
```
**Prerequisites:**
- Weather server running on port 8000
- LangChain tools server running on port 8001
- OPENAI_API_KEY environment variable set

**Test Coverage:**
- Multi-server connection pooling
- Tool discovery and enumeration
- Multi-step agent reasoning
- Cross-server tool invocation
- Full trace display with token metrics
- Minimal display mode
- Programmatic answer extraction
- Sequential instruction following

#### 5. MCP JSON Integration Test
**File:** `clients/integration_test_mcp_json.py:110-111`
**Execution:**
```bash
python clients/integration_test_mcp_json.py
```
**Prerequisites:**
- OPENAI_API_KEY environment variable
- CALCOM_API_KEY environment variable
- Node.js (for npx commands)
- Python uvx tool

**Configured Servers:**
- mcp-server-time (stdio)
- sequential-thinking (stdio)
- Context7 (stdio)

### CLI Commands

#### 1. Streamable HTTP Stateless Server
**File:** `examples/.../server.py:22-39`
**Command:** `mcp-simple-streamablehttp-stateless`
**Installation:**
```bash
cd examples/servers/streamable-http-stateless/
uv run mcp-simple-streamablehttp-stateless [OPTIONS]
```

**Options:**
- `--port INTEGER` - Port to listen on for HTTP (default: 3000)
- `--log-level TEXT` - Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `--json-response` - Enable JSON responses instead of SSE streams (flag, default: False)

**Example Usage:**
```bash
# Default configuration
uv run mcp-simple-streamablehttp-stateless

# Custom port with debug logging
uv run mcp-simple-streamablehttp-stateless --port 8080 --log-level DEBUG

# JSON responses instead of SSE
uv run mcp-simple-streamablehttp-stateless --json-response
```

### Package Entry Points

#### From pyproject.toml (Main Project)
**No explicit entry points defined** - The main project uses script-based execution rather than installed console scripts.

#### From pyproject.toml (Example Server)
**File:** `examples/servers/streamable-http-stateless/pyproject.toml:12-13`

```toml
[project.scripts]
mcp-simple-streamablehttp-stateless = "mcp_simple_streamablehttp_stateless.server:main"
```

**Entry Point Mapping:**
- **Console Script:** `mcp-simple-streamablehttp-stateless`
- **Python Function:** `mcp_simple_streamablehttp_stateless.server:main`
- **Type:** Click command with options
- **Purpose:** Launch low-level MCP server with streamable HTTP transport

---

## Dependencies and Integration

### Core Dependencies

#### LangChain Ecosystem
| Package | Version | Purpose |
|---------|---------|---------|
| `langchain` | >=0.3.19 | Core LangChain framework for agent orchestration |
| `langchain-mcp-adapters` | >=0.1.11 | Adapters for MCP integration with LangChain |
| `langchain-openai` | >=0.3.7 | OpenAI integration for LangChain |
| `langgraph` | >=0.6.7 | Graph-based agent workflows |

**Integration Points:**
- `MultiServerMCPClient` from `langchain_mcp_adapters.client` (used in `clients/integration_test.py:56`)
- `create_agent` from `langchain.agents` (used in `clients/integration_test.py:59`)
- `to_fastmcp` from `langchain_mcp_adapters.tools` (used in `servers/wrap_langchain_tools_server.py:4`)
- LangChain `@tool` decorator (used in `servers/wrap_langchain_tools_server.py:10, 16`)

#### MCP Protocol
| Package | Version | Purpose |
|---------|---------|---------|
| `mcp[cli]` | >=1.6.0 | Model Context Protocol implementation with CLI tools |

**Key Imports:**
- `mcp.server.fastmcp.FastMCP` - High-level server builder (all server files)
- `mcp.server.lowlevel.Server` - Low-level server implementation (examples)
- `mcp.server.streamable_http_manager.StreamableHTTPSessionManager` - HTTP session management
- `mcp.types` - Protocol type definitions (Tool, TextContent, ImageContent, etc.)

#### Anthropic/Claude
| Package | Version | Purpose |
|---------|---------|---------|
| `claude-agent-sdk` | >=0.1.4 | Claude Agent SDK (used by analysis framework) |

#### Supporting Libraries
| Package | Version | Purpose |
|---------|---------|---------|
| `python-dotenv` | >=1.1.0 | Environment variable management |
| `openai` | >=1.72.0 | OpenAI API client |
| `tavily-python` | >=0.5.4 | Tavily search integration |
| `numpy` | >=2.2.4 | Numerical computing |
| `ipykernel` | >=7.0.1 | Jupyter notebook support |

### Integration Patterns

#### 1. Multi-Server Client Pattern
**File:** `clients/integration_test.py:87-103`

```python
client = MultiServerMCPClient({
    "langchain_math": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    },
    "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
})
tools = await client.get_tools()
```

**Features:**
- Concurrent connections to multiple servers
- Heterogeneous transport support (streamable_http, stdio)
- Unified tool aggregation
- Automatic tool discovery

#### 2. LangChain to MCP Conversion Pattern
**File:** `servers/wrap_langchain_tools_server.py:10-23`

```python
@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

fastmcp_add = to_fastmcp(add)
```

**Use Case:** Wrap existing LangChain tools for use in MCP servers

#### 3. Agent Creation Pattern
**File:** `clients/integration_test.py:113`

```python
from langchain.agents import create_agent
agent = create_agent("openai:gpt-4.1", tools)
```

**Note:** Migration from LangGraph's `create_react_agent` to LangChain's `create_agent` (see line 57-59 comments)

#### 4. Stdio Server Configuration Pattern
**File:** `clients/integration_test_mcp_json.py:49-77`

```python
{
    "mcp-server-time": {
        "transport": "stdio",
        "command": "uvx",
        "args": ["mcp-server-time", "--local-timezone=America/Los_Angeles"],
        "env": {},
    },
    "Context7": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "env": {
            "CALCOM_API_KEY": os.environ.get("CALCOM_API_KEY", ""),
        },
    },
}
```

**Features:**
- Subprocess-based server management
- Environment variable passing
- Support for uvx (Python) and npx (Node.js) commands

#### 5. Low-Level Server Pattern
**File:** `examples/.../server.py:56-181`

```python
app = Server("mcp-streamable-http-stateless-demo")

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # Tool implementation

@app.list_tools()
async def list_tools():
    # Tool listing

session_manager = StreamableHTTPSessionManager(
    app=app,
    event_store=None,
    json_response=json_response,
    stateless=True,
)

starlette_app = Starlette(
    routes=[Mount("/mcp", app=handle_streamable_http)],
    lifespan=lifespan,
)

uvicorn.run(starlette_app, host="0.0.0.0", port=port)
```

**Use Case:** Advanced MCP server with custom ASGI integration and session management

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Layer                                │
│                                                                  │
│  ┌───────────────────────┐        ┌──────────────────────┐     │
│  │ integration_test.py   │        │ display_utils.py     │     │
│  │                       │        │                      │     │
│  │ - MultiServerClient   │───────▶│ - display_response() │     │
│  │ - Agent orchestration │        │ - get_final_answer() │     │
│  └───────────┬───────────┘        │ - print_summary()    │     │
│              │                     └──────────────────────┘     │
└──────────────┼──────────────────────────────────────────────────┘
               │
               │ HTTP/stdio
               │
┌──────────────┼──────────────────────────────────────────────────┐
│              │              Server Layer                         │
│              │                                                   │
│         ┌────┴────┬─────────────┬──────────────┐               │
│         ▼         ▼             ▼              ▼               │
│  ┌──────────┐ ┌──────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Math    │ │Weather│  │ LangChain   │  │ Streamable HTTP │  │
│  │  Server  │ │Server │  │ Wrap Server │  │ Stateless       │  │
│  │          │ │       │  │             │  │                 │  │
│  │ stdio    │ │ http  │  │ http:8001   │  │ http:3000       │  │
│  │ FastMCP  │ │:8000  │  │ to_fastmcp()│  │ Low-level API   │  │
│  └──────────┘ │FastMCP│  │ FastMCP     │  │ Server()        │  │
│               └───────┘  └─────────────┘  └─────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### Data Flow

#### Agent Request Flow
1. **User Query** → `integration_test.py:main()`
2. **Agent Invocation** → `agent.ainvoke({"messages": query})`
3. **Tool Discovery** → `MultiServerMCPClient.get_tools()`
4. **Tool Selection** → LLM selects appropriate tool(s)
5. **Tool Execution** → HTTP/stdio call to MCP server
6. **Response Processing** → `display_agent_response()`

#### Tool Registration Flow
1. **LangChain Tool Definition** → `@tool decorator`
2. **MCP Conversion** → `to_fastmcp()`
3. **Server Registration** → FastMCP instance
4. **Protocol Exposure** → HTTP endpoint or stdio
5. **Client Discovery** → `get_tools()` returns tool manifests

---

## Summary

This component inventory documents a well-structured educational project demonstrating MCP integration patterns. The codebase is organized into clear layers:

1. **Server Layer** - Three MCP server implementations showing different patterns (FastMCP, LangChain conversion, low-level API)
2. **Client Layer** - Integration tests and utilities for agent orchestration
3. **Configuration Layer** - Project dependencies, environment variables, and MCP server configurations

**Key Strengths:**
- Clear separation of concerns
- Comprehensive documentation and examples
- Multiple transport patterns (stdio, streamable-http)
- Production-ready display utilities
- Educational test cases with detailed comments

**Public API Surface:**
- 3 main server modules
- 1 utility module with 3 public functions
- 2 integration test scripts
- 1 example server package with CLI

**Entry Points:**
- 4 main script entry points
- 1 console script entry point
- Multiple CLI commands with argparse/click

This inventory provides a complete reference for understanding the project's architecture and can serve as a foundation for architectural analysis and documentation.
