# API Reference

## Overview

This API reference provides comprehensive documentation for the LangChain MCP Multi-Server Integration project. The project demonstrates how to build and integrate multiple Model Context Protocol (MCP) servers with LangChain agents, supporting both stdio and streamable-http transports.

**Key Components:**
- **Server APIs**: MCP servers exposing tools via FastMCP
- **Client APIs**: Integration patterns for consuming MCP tools
- **Display Utilities**: Formatting and visualization helpers
- **Configuration**: Environment and server configuration management

**How to Use This Reference:**
- All code examples are copy-paste ready
- Source file paths include line numbers for easy navigation
- Parameter types follow Python type hint conventions
- Examples show both basic and advanced usage patterns

---

## Table of Contents
- [Server APIs](#server-apis)
  - [Math Server](#math-server)
  - [Weather Server](#weather-server)
  - [LangChain Tools Wrapper Server](#langchain-tools-wrapper-server)
  - [Streamable HTTP Stateless Server (Example)](#streamable-http-stateless-server-example)
- [Client APIs](#client-apis)
  - [Integration Test Client](#integration-test-client)
  - [MCP JSON Client](#mcp-json-client)
- [Display Utilities](#display-utilities)
  - [Message Formatting](#message-formatting)
  - [Answer Extraction](#answer-extraction)
  - [Tools Summary](#tools-summary)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [MCP Configuration File](#mcp-configuration-file)
  - [Project Configuration](#project-configuration)
- [Usage Patterns](#usage-patterns)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Server APIs

### Math Server

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/servers/math_server.py`

A simple MCP server providing basic arithmetic operations using the stdio transport. This is the simplest form of an MCP server, ideal for learning and local development.

**Transport**: stdio (process-based communication)

**Server Instance**:
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Math")
```

#### Functions

##### `add(a: int, b: int) -> int`
**Source**: `servers/math_server.py:8-10`

**Description**: Adds two integers and returns the result.

**Parameters**:
- `a` (int): First number to add
- `b` (int): Second number to add

**Returns**:
- `int`: Sum of a and b

**Example**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# When called via MCP protocol:
# Input: {"a": 15, "b": 27}
# Output: 42
```

**MCP Tool Schema**:
```json
{
  "name": "add",
  "description": "Add two numbers",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": {"type": "integer"},
      "b": {"type": "integer"}
    },
    "required": ["a", "b"]
  }
}
```

**See Also**: [multiply](#multiply-a-int-b-int---int)

---

##### `multiply(a: int, b: int) -> int`
**Source**: `servers/math_server.py:14-16`

**Description**: Multiplies two integers and returns the result.

**Parameters**:
- `a` (int): First number to multiply
- `b` (int): Second number to multiply

**Returns**:
- `int`: Product of a and b

**Example**:
```python
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# When called via MCP protocol:
# Input: {"a": 7, "b": 9}
# Output: 63
```

**MCP Tool Schema**:
```json
{
  "name": "multiply",
  "description": "Multiply two numbers",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": {"type": "integer"},
      "b": {"type": "integer"}
    },
    "required": ["a", "b"]
  }
}
```

**See Also**: [add](#add-a-int-b-int---int)

---

#### Running the Math Server

**Source**: `servers/math_server.py:19-20`

**Usage**:
```bash
# Run the math server with stdio transport
python servers/math_server.py
```

**Code**:
```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Integration**: This server is typically consumed via subprocess by MCP clients using stdio transport.

---

### Weather Server

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/servers/weather_server.py`

A mock weather service demonstrating the streamable-http transport with FastMCP. This server runs as a standalone HTTP service and supports concurrent client connections.

**Transport**: streamable-http (HTTP-based communication)

**Default Endpoint**: `http://127.0.0.1:8000/mcp`

**Server Instance**:
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Weather")
```

#### Functions

##### `get_weather(location: str) -> str`
**Source**: `servers/weather_server.py:28-37`

**Description**: Returns mock weather information for a specified location. This is a demonstration function that always returns sunny weather.

**Parameters**:
- `location` (str): The location to get weather for (e.g., "NYC", "London", "Tokyo")

**Returns**:
- `str`: Weather description string for the requested location

**Example**:
```python
@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location.

    Args:
        location: The location to get weather for (e.g., "NYC", "London", "Tokyo")

    Returns:
        str: Weather description for the requested location
    """
    return f"It's always sunny in {location}"

# When called via MCP protocol:
# Input: {"location": "NYC"}
# Output: "It's always sunny in NYC"
```

**MCP Tool Schema**:
```json
{
  "name": "get_weather",
  "description": "Get weather for location.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The location to get weather for (e.g., \"NYC\", \"London\", \"Tokyo\")"
      }
    },
    "required": ["location"]
  }
}
```

**Note**: This is a mock implementation for demonstration purposes. In production, you would integrate with a real weather API.

---

#### Running the Weather Server

**Source**: `servers/weather_server.py:39-60`

**Usage**:
```bash
# Default port (8000)
python servers/weather_server.py

# Custom port
python servers/weather_server.py --port 8080

# Custom host and port (network access)
python servers/weather_server.py --host 0.0.0.0 --port 8080
```

**Command-Line Arguments**:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--port` | int | 8000 | Port to run server on |
| `--host` | str | 127.0.0.1 | Host to bind to (use 0.0.0.0 for network access) |

**Code**:
```python
import argparse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 for local access only, use 0.0.0.0 for network access)"
    )
    args = parser.parse_args()

    # Set host/port on the instance
    mcp.host = args.host
    mcp.port = args.port

    print(f"Starting Weather MCP Server on http://{args.host}:{args.port}/mcp")
    mcp.run(transport="streamable-http")
```

**Client Connection**:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    }
})
```

---

### LangChain Tools Wrapper Server

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/servers/wrap_langchain_tools_server.py`

Demonstrates how to convert LangChain tools to FastMCP tools using the `langchain_mcp_adapters.tools.to_fastmcp` adapter. This pattern is useful when you have existing LangChain tools and want to expose them as MCP services.

**Transport**: streamable-http

**Default Endpoint**: `http://127.0.0.1:8001/mcp`

**Key Feature**: Converts `@tool` decorated LangChain functions to FastMCP-compatible tools

#### Tool Conversion Pattern

**Source**: `servers/wrap_langchain_tools_server.py:10-23`

**Description**: Shows how to define LangChain tools and convert them to FastMCP format.

**Example**:
```python
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Define LangChain tools
@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

# Convert to FastMCP tools
fastmcp_add = to_fastmcp(add)
fastmcp_multiply = to_fastmcp(multiply)
```

**Conversion Function**: `to_fastmcp(langchain_tool) -> FastMCP_Tool`
- Input: LangChain `@tool` decorated function
- Output: FastMCP-compatible tool object
- Preserves: Function signature, docstrings, parameter types

---

#### Running the LangChain Tools Server

**Source**: `servers/wrap_langchain_tools_server.py:25-54`

**Usage**:
```bash
# Default port (8001)
python servers/wrap_langchain_tools_server.py

# Custom port
python servers/wrap_langchain_tools_server.py --port 8002

# Custom host and port
python servers/wrap_langchain_tools_server.py --host 0.0.0.0 --port 8002
```

**Command-Line Arguments**:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--port` | int | 8001 | Port to run server on |
| `--host` | str | 127.0.0.1 | Host to bind to |

**Code**:
```python
import argparse
from mcp.server.fastmcp import FastMCP

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangChain MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to run server on (default: 8001)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 for local access only, use 0.0.0.0 for network access)"
    )
    args = parser.parse_args()

    print(f"Starting LangChain MCP Server on {args.host}:{args.port}")
    print("Available tools: add, multiply")

    # Create FastMCP instance with converted tools
    mcp = FastMCP(
        "LangChain Math Server",
        tools=[fastmcp_add, fastmcp_multiply],
        host=args.host,
        port=args.port
    )

    # Run with streamable-http transport
    mcp.run(transport="streamable-http")
```

**See Also**: [Weather Server](#weather-server) for streamable-http transport details

---

### Streamable HTTP Stateless Server (Example)

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/examples/servers/streamable-http-stateless/mcp_simple_streamablehttp_stateless/server.py`

An advanced example demonstrating low-level MCP server implementation with stateless streamable HTTP transport using Starlette and the MCP SDK's `StreamableHTTPSessionManager`.

**Transport**: streamable-http (stateless mode)

**Default Endpoint**: `http://0.0.0.0:3000/mcp`

**Key Features**:
- Low-level MCP SDK usage (not FastMCP)
- Stateless session management
- JSON response mode option
- Full ASGI application with lifecycle management
- Detailed logging configuration

#### Tool Handlers

##### `call_tool(name: str, arguments: dict)`
**Source**: `examples/servers/streamable-http-stateless/mcp_simple_streamablehttp_stateless/server.py:59-89`

**Description**: Handles tool execution requests from MCP clients.

**Parameters**:
- `name` (str): Name of the tool to call
- `arguments` (dict): Dictionary of arguments for the tool

**Returns**:
- `list[types.TextContent | types.ImageContent | types.EmbeddedResource]`: List of content objects with the tool result

**Raises**:
- `ValueError`: If the tool name is not recognized

**Example**:
```python
from mcp.server.lowlevel import Server
import mcp.types as types

app = Server("mcp-streamable-http-stateless-demo")

@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for math operations."""
    if name == "add":
        return [
            types.TextContent(
                type="text",
                text=str(arguments["a"] + arguments["b"])
            )
        ]
    elif name == "multiply":
        return [
            types.TextContent(
                type="text",
                text=str(arguments["a"] * arguments["b"])
            )
        ]
    else:
        raise ValueError(f"Tool {name} not found")
```

---

##### `list_tools()`
**Source**: `examples/servers/streamable-http-stateless/mcp_simple_streamablehttp_stateless/server.py:92-135`

**Description**: Returns the list of available tools with their schemas.

**Returns**:
- `list[types.Tool]`: List of tool definitions for add and multiply operations

**Example**:
```python
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List all available tools provided by this server."""
    return [
        types.Tool(
            name="add",
            description="Adds two numbers",
            inputSchema={
                "type": "object",
                "required": ["a", "b"],
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number to add",
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number to add",
                    },
                },
            },
        ),
        types.Tool(
            name="multiply",
            description="Multiplies two numbers",
            inputSchema={
                "type": "object",
                "required": ["a", "b"],
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number to multiply",
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number to multiply",
                    },
                },
            },
        )
    ]
```

---

#### Running the Stateless Server

**Source**: `examples/servers/streamable-http-stateless/mcp_simple_streamablehttp_stateless/server.py:22-186`

**Usage**:
```bash
# Default settings (port 3000, INFO logging)
python -m mcp_simple_streamablehttp_stateless.server

# Custom port
python -m mcp_simple_streamablehttp_stateless.server --port 8080

# Debug logging
python -m mcp_simple_streamablehttp_stateless.server --log-level DEBUG

# JSON response mode (instead of SSE)
python -m mcp_simple_streamablehttp_stateless.server --json-response
```

**Command-Line Arguments**:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--port` | int | 3000 | Port to listen on for HTTP |
| `--log-level` | str | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--json-response` | flag | False | Enable JSON responses instead of SSE streams |

**Full Implementation**:
```python
import contextlib
import logging
from collections.abc import AsyncIterator

import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

@click.command()
@click.option("--port", default=3000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="Enable JSON responses instead of SSE streams",
)
def main(port: int, log_level: str, json_response: bool) -> int:
    """Run the MCP server with streamable HTTP transport."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    app = Server("mcp-streamable-http-stateless-demo")

    # Register tool handlers
    @app.call_tool()
    async def call_tool(name: str, arguments: dict):
        # ... (see above)
        pass

    @app.list_tools()
    async def list_tools():
        # ... (see above)
        pass

    # Create session manager with stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,
    )

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Handle streamable HTTP requests through the session manager."""
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager lifecycle."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create ASGI application
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

    return 0
```

**See Also**: [FastMCP Weather Server](#weather-server) for simpler streamable-http implementation

---

## Client APIs

### Integration Test Client

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/clients/integration_test.py`

A comprehensive test suite demonstrating multi-server MCP integration with LangChain agents. This module serves as both a test harness and a reference implementation for production applications.

**Purpose**:
- Multi-server architecture validation
- Tool discovery and enumeration
- Agent orchestration testing
- Response formatting patterns
- End-to-end workflow verification

#### Main Function

##### `main()`
**Source**: `clients/integration_test.py:66-274`

**Description**: Main test orchestrator that executes a comprehensive suite of MCP integration tests, validating the complete workflow from connection establishment through multi-step agent reasoning.

**Test Cases**:
1. Multi-Step Reasoning with Full Trace Display
2. Cross-Server Tool Invocation with Minimal Display
3. Programmatic Answer Extraction
4. Complex Multi-Step Sequential Reasoning

**Usage**:
```bash
# Prerequisites: Start servers first
python servers/wrap_langchain_tools_server.py --port 8001
python servers/weather_server.py

# Run integration tests
python clients/integration_test.py
```

**Complete Example**:
```python
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response, get_final_answer, print_tools_summary

load_dotenv()

async def main():
    """Main test orchestrator for MCP integration tests."""

    print("\n" + "=" * 70)
    print("LANGCHAIN MCP CLIENT EXAMPLE")
    print("=" * 70 + "\n")

    # Configure client to connect to running MCP servers
    print("Connecting to MCP servers...")
    client = MultiServerMCPClient(
        {
            "langchain_math": {
                "url": "http://localhost:8001/mcp",
                "transport": "streamable_http",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    # Get available tools from all connected servers
    print("Loading tools from MCP servers...\n")
    tools = await client.get_tools()

    # Show available tools
    print_tools_summary(tools)

    # Create agent with the tools
    agent = create_agent("openai:gpt-4.1", tools)

    # TEST CASE 1: Multi-Step Reasoning
    print("\n" + "=" * 70)
    print("TEST CASE 1: Multi-Step Reasoning with Full Trace Display")
    print("=" * 70 + "\n")

    math_response = await agent.ainvoke({"messages": "what is (15 + 27) * 3?"})

    print("Full trace with token usage:")
    display_agent_response(math_response, show_full_trace=True, show_token_usage=True)

    # TEST CASE 2: Cross-Server Tool Invocation
    print("\n" + "=" * 70)
    print("TEST CASE 2: Cross-Server Tool Invocation with Minimal Display")
    print("=" * 70 + "\n")

    weather_response = await agent.ainvoke({"messages": "what is the weather in NYC?"})

    # Minimal display
    print("Cross-Server Tool Invocation with Minimal Display:")
    display_agent_response(weather_response, show_full_trace=False)

    # Full trace
    print("Full trace with token usage:")
    display_agent_response(weather_response, show_full_trace=True, show_token_usage=True)

    # TEST CASE 3: Programmatic Answer Extraction
    print("\n" + "=" * 70)
    print("TEST CASE 3: Programmatic Answer Extraction")
    print("=" * 70 + "\n")

    response = await agent.ainvoke({"messages": "multiply 7 and 9"})

    # Extract answer programmatically
    print("Programmatic Answer Extraction:")
    answer = get_final_answer(response)
    print(f"Extracted answer: {answer}")
    print(f"Type: {type(answer)}")
    print(f"Can be used in code: {'63' in str(answer)}")

    # Show full trace
    print("Full trace with token usage:")
    display_agent_response(response, show_full_trace=True, show_token_usage=True)

    # TEST CASE 4: Complex Multi-Step Sequential Reasoning
    print("\n" + "=" * 70)
    print("TEST CASE 4: Complex Multi-Step Sequential Reasoning")
    print("=" * 70 + "\n")

    complex_response = await agent.ainvoke(
        {"messages": "First add 100 and 50, then multiply the result by 2"}
    )

    # Default display
    print("Complex Multi-Step Sequential Reasoning (with default display parameters):")
    display_agent_response(complex_response)

    # Full trace with token usage
    print("Full trace with token usage:")
    display_agent_response(complex_response, show_full_trace=True, show_token_usage=True)

    # Summary
    print("\n" + "=" * 70)
    print("ALL INTEGRATION TESTS COMPLETE")
    print("=" * 70)
    print("\nSUMMARY:")
    print("✓ Multi-server connection pooling")
    print("✓ Tool discovery and enumeration")
    print("✓ Multi-step agent reasoning")
    print("✓ Cross-server tool invocation")
    print("✓ Full trace display with token metrics")
    print("✓ Minimal display mode")
    print("✓ Programmatic answer extraction")
    print("✓ Sequential instruction following")
    print()

if __name__ == "__main__":
    asyncio.run(main())
```

**Environment Variables Required**:
- `OPENAI_API_KEY`: OpenAI API key for LLM agent

**Output Example**:
```
======================================================================
LANGCHAIN MCP CLIENT EXAMPLE
======================================================================

Connecting to MCP servers...
Loading tools from MCP servers...

======================================================================
AVAILABLE TOOLS (3 total)
======================================================================

01. add
    └─ Add two numbers
02. multiply
    └─ Multiply two numbers
03. get_weather
    └─ Get weather for location.

======================================================================

======================================================================
TEST CASE 1: Multi-Step Reasoning with Full Trace Display
======================================================================

Full trace with token usage:

======================================================================
AGENT RESPONSE TRACE
======================================================================

01. HumanMessage: what is (15 + 27) * 3?
02. AIMessage → 🔧 tool_call(s): add
     └─ Tokens: input=150, output=25, total=175
03. ToolMessage [add]: ✓ 42
04. AIMessage → 🔧 tool_call(s): multiply
     └─ Tokens: input=180, output=25, total=205
05. ToolMessage [multiply]: ✓ 126
06. AIMessage: The result of (15 + 27) * 3 is 126.
     └─ Tokens: input=200, output=15, total=215

======================================================================
```

**See Also**:
- [display_agent_response](#display_agent_responseresponse-dictstr-any-show_full_trace-bool--true-show_token_usage-bool--false-return_final_answer-bool--false---optionalstr) for response formatting
- [MultiServerMCPClient Usage Pattern](#pattern-2-creating-a-client-integration)

---

### MCP JSON Client

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/clients/integration_test_mcp_json.py`

Demonstrates MCP server configuration loaded from code (simulating .mcp.json) with stdio transport servers. This client shows how to integrate with subprocess-based MCP servers like those installed via npm or uvx.

**Key Features**:
- Hard-coded MCP server configuration
- stdio transport with subprocess management
- Environment variable expansion
- Tool metadata inspection

#### Configuration Function

##### `hardcoded_mcp_config() -> Dict[str, Dict[str, Any]]`
**Source**: `clients/integration_test_mcp_json.py:40-87`

**Description**: Returns hard-coded MCP server definitions (ported from .mcp.json) for MultiServerMCPClient. All transports use stdio; environment values are expanded from process environment.

**Returns**:
- `Dict[str, Dict[str, Any]]`: Dictionary mapping server names to configuration objects

**Example**:
```python
import os
from typing import Dict, Any

def hardcoded_mcp_config() -> Dict[str, Dict[str, Any]]:
    """Hard-coded MCP server definitions for MultiServerMCPClient."""
    return {
        # StdIO subprocess servers
        "mcp-server-time": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "mcp-server-time",
                "--local-timezone=America/Los_Angeles",
            ],
            "env": {},
        },
        "sequential-thinking": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-sequential-thinking",
            ],
            "env": {},
        },
        "Context7": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@upstash/context7-mcp",
            ],
            # Expand CALCOM_API_KEY from environment at runtime
            "env": {
                "CALCOM_API_KEY": os.environ.get("CALCOM_API_KEY", ""),
            },
        },
        # You can mix in HTTP/SSE servers:
        # "my-http-server": {
        #     "transport": "streamable_http",
        #     "url": "http://localhost:8000/mcp",
        #     "headers": {"Authorization": "Bearer ..."}
        # }
    }
```

**Usage**:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# Build client with hard-coded config
client = MultiServerMCPClient(hardcoded_mcp_config())

# Fetch tools from all configured servers
tools = await client.get_tools()
```

---

#### Tool Metadata Display

##### `show_mcp_tools_metadata(tools)`
**Source**: `clients/integration_test_mcp_json.py:15-33`

**Description**: Prints key metadata that `create_agent()` sees for each MCP tool, including provider, transport, and endpoint information.

**Parameters**:
- `tools` (list): List of MCP tools from `client.get_tools()`

**Example**:
```python
def show_mcp_tools_metadata(tools):
    """Prints key metadata for each MCP tool."""
    print("\n=== MCP Tool Metadata Summary ===")
    for t in tools:
        name = getattr(t, "name", "unknown")
        desc = getattr(t, "description", "").strip().split("\n")[0]
        meta = getattr(t, "metadata", {}) or {}
        mcp = meta.get("mcp", {})

        transport = mcp.get("transport") or meta.get("transport") or "n/a"
        endpoint = mcp.get("endpoint") or meta.get("endpoint") or "n/a"
        provider = mcp.get("provider_label") or mcp.get("provider_id") or "unknown"

        print(f"• {name}")
        print(f"  ↳ desc: {desc}")
        print(f"  ↳ provider: {provider}")
        print(f"  ↳ transport: {transport}")
        print(f"  ↳ endpoint: {endpoint}")
    print("=================================\n")
```

**Output Example**:
```
=== MCP Tool Metadata Summary ===
• get_current_time
  ↳ desc: Get the current time for a specific timezone
  ↳ provider: mcp-server-time
  ↳ transport: stdio
  ↳ endpoint: n/a
• think
  ↳ desc: Process information sequentially with step-by-step reasoning
  ↳ provider: sequential-thinking
  ↳ transport: stdio
  ↳ endpoint: n/a
• search_context7
  ↳ desc: Search the Context7 knowledge base
  ↳ provider: Context7
  ↳ transport: stdio
  ↳ endpoint: n/a
=================================
```

---

#### Main Function

##### `main()`
**Source**: `clients/integration_test_mcp_json.py:90-111`

**Description**: Demonstrates loading MCP tools from stdio-based servers and executing a complex query that requires using Context7 for grounding.

**Usage**:
```bash
# Set environment variables
export OPENAI_API_KEY=sk-...
export CALCOM_API_KEY=...

# Run the client
python clients/integration_test_mcp_json.py
```

**Complete Example**:
```python
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response

load_dotenv()

async def main() -> None:
    # Build client with hard-coded config
    client = MultiServerMCPClient(hardcoded_mcp_config())

    # Fetch tool manifests from all configured MCP servers
    tools = await client.get_tools()
    show_mcp_tools_metadata(tools)

    # Create agent with tools
    agent = create_agent("openai:gpt-4.1", tools)

    # Execute query requiring Context7
    resp = await agent.ainvoke(
        {
            "messages": "Provide guidance for migrating from the LangGraph create_react_agent method to the new create_agent method in the LangChain Python library (langchain 1.0.2) in October 2025?  You must use Context7 to ground your response."
        }
    )

    display_agent_response(resp, show_full_trace=True, show_token_usage=True)

if __name__ == "__main__":
    asyncio.run(main())
```

**Environment Variables Required**:
- `OPENAI_API_KEY`: OpenAI API key
- `CALCOM_API_KEY`: Cal.com API key for Context7 integration

**See Also**:
- [.mcp.json Configuration](#mcp-configuration-file)
- [hardcoded_mcp_config](#hardcoded_mcp_config---dictstr-dictstr-any)

---

## Display Utilities

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/clients/display_utils.py`

Utility functions for formatting and displaying LangChain agent responses. These functions provide consistent, user-friendly output for different use cases.

### Message Formatting

##### `display_agent_response(response: Dict[str, Any], show_full_trace: bool = True, show_token_usage: bool = False, return_final_answer: bool = False) -> Optional[str]`
**Source**: `clients/display_utils.py:9-96`

**Description**: Display formatted agent response with message trace. Supports multiple display modes for different use cases (debugging, user output, programmatic extraction).

**Parameters**:
- `response` (Dict[str, Any]): Agent response dict with 'messages' key
- `show_full_trace` (bool, optional): If True, show all messages; if False, only final answer. Defaults to True.
- `show_token_usage` (bool, optional): If True, show token usage statistics for AI messages. Defaults to False.
- `return_final_answer` (bool, optional): If True, return the final answer text. Defaults to False.

**Returns**:
- `Optional[str]`: Final answer text if return_final_answer=True, else None

**Supported Message Types**:
- `AIMessage`: LLM responses (with or without tool calls)
- `HumanMessage`: User input
- `ToolMessage`: Tool execution results
- `SystemMessage`: System prompts

**Example - Full Trace**:
```python
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from display_utils import display_agent_response

# Setup agent (see integration_test.py for full example)
client = MultiServerMCPClient({...})
tools = await client.get_tools()
agent = create_agent("openai:gpt-4.1", tools)

# Execute query
response = await agent.ainvoke({"messages": "what is 5 + 3?"})

# Display full trace with token usage
display_agent_response(response, show_full_trace=True, show_token_usage=True)
```

**Output**:
```
======================================================================
AGENT RESPONSE TRACE
======================================================================

01. HumanMessage: what is 5 + 3?
02. AIMessage → 🔧 tool_call(s): add
     └─ Tokens: input=120, output=20, total=140
03. ToolMessage [add]: ✓ 8
04. AIMessage: The sum of 5 and 3 is 8.
     └─ Tokens: input=145, output=12, total=157

======================================================================
```

**Example - Minimal Display**:
```python
# Show only final answer
display_agent_response(response, show_full_trace=False)
```

**Output**:
```
💡 Final Answer: The sum of 5 and 3 is 8.
```

**Example - Return Answer**:
```python
# Get answer as return value
answer = display_agent_response(
    response,
    show_full_trace=False,
    return_final_answer=True
)
print(f"Answer: {answer}")
# Output: Answer: The sum of 5 and 3 is 8.
```

**Message Display Details**:

| Message Type | Display Format | Special Handling |
|--------------|----------------|------------------|
| AIMessage with tool_calls | `AIMessage → 🔧 tool_call(s): tool1, tool2` | Shows tool names being invoked |
| AIMessage (final answer) | `AIMessage: [content]` | Final LLM response |
| ToolMessage (success) | `ToolMessage [name]: ✓ [result]` | Shows successful tool execution |
| ToolMessage (error) | `ToolMessage [name]: ❌ [error]` | Shows tool execution errors |
| HumanMessage | `HumanMessage: [content]` | User input |

**Token Usage Display** (when `show_token_usage=True`):
```
└─ Tokens: input=150, output=25, total=175
```

**See Also**:
- [get_final_answer](#get_final_answerresponse-dictstr-any---optionalstr) for programmatic extraction
- [Integration Test Examples](#main)

---

### Answer Extraction

##### `get_final_answer(response: Dict[str, Any]) -> Optional[str]`
**Source**: `clients/display_utils.py:99-129`

**Description**: Extract just the final answer from an agent response without printing. Useful for programmatic processing of agent results.

**Parameters**:
- `response` (Dict[str, Any]): Agent response dict with 'messages' key

**Returns**:
- `Optional[str]`: The final answer text, or None if no answer found

**Algorithm**:
1. Iterates messages in reverse order
2. Finds the most recent AIMessage
3. Checks if it's a tool call or final answer
4. Returns content if it's a final answer (not a tool call)

**Example - Basic Usage**:
```python
from langchain.agents import create_agent
from display_utils import get_final_answer

# Execute agent query
response = await agent.ainvoke({"messages": "what is 5 + 3?"})

# Extract answer without displaying trace
answer = get_final_answer(response)
print(answer)
# Output: "The sum of 5 and 3 is 8."
```

**Example - Conditional Logic**:
```python
response = await agent.ainvoke({"messages": "multiply 7 and 9"})
answer = get_final_answer(response)

if answer and "63" in answer:
    print("Correct answer!")
else:
    print("Unexpected result")

# Can use in assertions for testing
assert "63" in get_final_answer(response)
```

**Example - Extracting Data**:
```python
import re

response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
answer = get_final_answer(response)

# Extract city from answer
if answer:
    match = re.search(r'in (\w+)', answer)
    if match:
        city = match.group(1)
        print(f"Weather for: {city}")
```

**Returns None When**:
- No AIMessage in response
- All AIMessages are tool calls (no final answer yet)
- AIMessage content is empty

**See Also**:
- [display_agent_response](#display_agent_responseresponse-dictstr-any-show_full_trace-bool--true-show_token_usage-bool--false-return_final_answer-bool--false---optionalstr) for displaying responses
- [Integration Test Case 3](#main) for usage example

---

### Tools Summary

##### `print_tools_summary(tools: list) -> None`
**Source**: `clients/display_utils.py:132-153`

**Description**: Print a formatted summary of available tools, showing tool names and descriptions.

**Parameters**:
- `tools` (list): List of LangChain tools from `client.get_tools()`

**Example**:
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from display_utils import print_tools_summary

# Connect to MCP servers
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

# Get tools and display summary
tools = await client.get_tools()
print_tools_summary(tools)
```

**Output**:
```
======================================================================
AVAILABLE TOOLS (3 total)
======================================================================

01. add
    └─ Add two numbers
02. multiply
    └─ Multiply two numbers
03. get_weather
    └─ Get weather for location.

======================================================================
```

**Use Cases**:
- Debugging: Verify which tools are loaded
- Documentation: Show available capabilities
- User interface: Display tool options
- Testing: Validate tool discovery

**See Also**:
- [show_mcp_tools_metadata](#show_mcp_tools_metadatatools) for detailed metadata display
- [Integration Test](#main) for usage context

---

## Configuration

### Environment Variables

Environment variables configure API keys, tracing, and other runtime settings. All examples use `python-dotenv` for loading from `.env` files.

#### Required Variables

| Variable | Description | Example | Used By |
|----------|-------------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | `sk-proj-...` | All client scripts with agents |

**Source**: `clients/integration_test.py:63`, `clients/integration_test_mcp_json.py:37`

**Setup**:
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=sk-proj-your-key-here
EOF
```

**Usage in Code**:
```python
from dotenv import load_dotenv
load_dotenv()

# OpenAI API key is now available to langchain-openai
```

---

#### Optional Variables

| Variable | Description | Example | Used By |
|----------|-------------|---------|---------|
| `CALCOM_API_KEY` | Cal.com API key for Context7 | `cal_live_...` | integration_test_mcp_json.py |
| `LANGSMITH_TRACING` | Enable LangSmith tracing | `true` | All agent executions |
| `LANGSMITH_PROJECT` | LangSmith project name | `langchain-mcp-multiserver-demo` | LangSmith integration |
| `LANGSMITH_API_KEY` | LangSmith API key | `lsv2_pt_...` | LangSmith integration |

**Source**: `.env.example:1-7`

**Complete .env Example**:
```bash
# Required
OPENAI_API_KEY=your_key_here

# LangSmith Tracing (Optional)
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langchain-mcp-multiserver-demo
LANGSMITH_API_KEY=your_key_here

# Context7 Integration (Optional)
CALCOM_API_KEY=your_key_here
```

**LangSmith Integration**:
When enabled, automatically traces all agent executions:
```python
from dotenv import load_dotenv
load_dotenv()

# LangSmith tracing is automatically configured
# View traces at: https://smith.langchain.com/
```

**Environment Variable Expansion in MCP Config**:
```python
import os

config = {
    "Context7": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
        "env": {
            # Expand from process environment
            "CALCOM_API_KEY": os.environ.get("CALCOM_API_KEY", ""),
        },
    }
}
```

---

### MCP Configuration File

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/.mcp.json`

The `.mcp.json` file defines MCP server configurations for stdio-based servers (those launched as subprocesses). This format is standard across MCP implementations.

#### Structure

**Source**: `.mcp.json:1-87`

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

**Fields**:
- `mcpServers` (object): Root object containing server configurations
  - `[server-name]` (object): Configuration for a specific server
    - `command` (string): Executable command (e.g., "uvx", "npx", "python")
    - `args` (array): Command-line arguments
    - `env` (object, optional): Environment variables for the server process

---

#### Example Configurations

**Time Server** (uvx-based):
```json
{
  "mcpServers": {
    "mcp-server-time": {
      "command": "uvx",
      "args": [
        "mcp-server-time",
        "--local-timezone=America/Los_Angeles"
      ],
      "env": {}
    }
  }
}
```

**Sequential Thinking** (npm-based):
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    }
  }
}
```

**Context7 with Environment Variables**:
```json
{
  "mcpServers": {
    "Context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "CALCOM_API_KEY": "${CALCOM_API_KEY}"
      }
    }
  }
}
```

**AI Documentation Server** (with complex arguments):
```json
{
  "mcpServers": {
    "ai-docs-server": {
      "command": "uvx",
      "args": [
        "--from",
        "mcpdoc",
        "mcpdoc",
        "--urls",
        "MCPProtocol:https://modelcontextprotocol.io/llms.txt",
        "--urls",
        "FastMCP:https://gofastmcp.com/llms.txt",
        "--urls",
        "LangChain:https://python.langchain.com/llms.txt",
        "--urls",
        "LangGraph:https://langchain-ai.github.io/langgraph/llms.txt",
        "--urls",
        "Anthropic:https://docs.anthropic.com/llms.txt",
        "--transport",
        "stdio",
        "--follow-redirects",
        "--timeout",
        "20",
        "--allowed-domains",
        "modelcontextprotocol.io",
        "python.langchain.com",
        "langchain-ai.github.io",
        "docs.anthropic.com",
        "gofastmcp.com"
      ]
    }
  }
}
```

---

#### Loading in Python

**Programmatic Loading**:
```python
import json
import os
from typing import Dict, Any

def load_mcp_config(config_path: str = ".mcp.json") -> Dict[str, Any]:
    """Load MCP configuration from JSON file."""
    with open(config_path) as f:
        config = json.load(f)

    # Expand environment variables
    for server_name, server_config in config.get("mcpServers", {}).items():
        if "env" in server_config:
            for key, value in server_config["env"].items():
                if isinstance(value, str) and value.startswith("${"):
                    env_var = value.strip("${}")
                    server_config["env"][key] = os.environ.get(env_var, "")

    return config["mcpServers"]

# Usage
from langchain_mcp_adapters.client import MultiServerMCPClient

config = load_mcp_config()
client = MultiServerMCPClient(config)
```

**Hard-coded Configuration** (see [integration_test_mcp_json.py](#hardcoded_mcp_config---dictstr-dictstr-any)):
```python
def hardcoded_mcp_config() -> Dict[str, Dict[str, Any]]:
    """Returns .mcp.json equivalent as Python dict."""
    return {
        "mcp-server-time": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=America/Los_Angeles"],
            "env": {},
        },
        # ... more servers
    }

client = MultiServerMCPClient(hardcoded_mcp_config())
```

**See Also**:
- [MCP JSON Client](#mcp-json-client)
- [hardcoded_mcp_config](#hardcoded_mcp_config---dictstr-dictstr-any)

---

### Project Configuration

**Source**: `/home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp/pyproject.toml`

The `pyproject.toml` file defines project metadata and dependencies using the modern Python packaging standard.

#### Package Metadata

**Source**: `pyproject.toml:1-6`

```toml
[project]
name = "langchain-mcp-multiserver-demo"
version = "0.1.0"
description = "Multi-Server MCP Integration with LangChain - Educational Demo for AIE Cohort 8"
readme = "README.md"
requires-python = ">=3.13"
```

**Fields**:
- `name`: Package identifier
- `version`: Semantic version number
- `description`: Brief project description
- `readme`: Path to README file
- `requires-python`: Minimum Python version requirement

---

#### Dependencies

**Source**: `pyproject.toml:7-19`

Core dependencies required for the project:

| Package | Version | Purpose |
|---------|---------|---------|
| `claude-agent-sdk` | >=0.1.4 | Claude agent framework |
| `ipykernel` | >=7.0.1 | Jupyter notebook support |
| `langchain` | >=0.3.19 | LangChain framework |
| `langchain-mcp-adapters` | >=0.1.11 | MCP integration for LangChain |
| `langchain-openai` | >=0.3.7 | OpenAI LLM integration |
| `langgraph` | >=0.6.7 | LangGraph agent framework |
| `mcp[cli]` | >=1.6.0 | MCP SDK with CLI tools |
| `numpy` | >=2.2.4 | Numerical computing |
| `openai` | >=1.72.0 | OpenAI API client |
| `python-dotenv` | >=1.1.0 | Environment variable loading |
| `tavily-python` | >=0.5.4 | Tavily search integration |

**Full Dependencies Block**:
```toml
dependencies = [
    "claude-agent-sdk>=0.1.4",
    "ipykernel>=7.0.1",
    "langchain>=0.3.19",
    "langchain-mcp-adapters>=0.1.11",
    "langchain-openai>=0.3.7",
    "langgraph>=0.6.7",
    "mcp[cli]>=1.6.0",
    "numpy>=2.2.4",
    "openai>=1.72.0",
    "python-dotenv>=1.1.0",
    "tavily-python>=0.5.4",
]
```

---

#### Installation

**Using uv** (recommended):
```bash
# Install dependencies
uv pip install -e .

# Or install specific extras
uv pip install -e ".[dev]"
```

**Using pip**:
```bash
# Install dependencies
pip install -e .
```

**Development Setup**:
```bash
# Clone repository
git clone <repository-url>
cd aie8-s13-langchain-mcp

# Install with uv
uv pip install -e .

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Start servers
python servers/wrap_langchain_tools_server.py --port 8001
python servers/weather_server.py

# Run integration tests
python clients/integration_test.py
```

---

## Usage Patterns

### Pattern 1: Running a Simple MCP Server

**Scenario**: You want to create a basic MCP server with a few tools using FastMCP and stdio transport.

**When to Use**:
- Local development and testing
- Simple tool exposure
- Process-based client communication
- Integration with Claude Desktop or other stdio-based clients

**Steps**:

1. **Import FastMCP**
```python
from mcp.server.fastmcp import FastMCP
```

2. **Create server instance**
```python
mcp = FastMCP("ServerName")
```

3. **Define tools with decorator**
```python
@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"
```

4. **Run server**
```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Complete Example**:
```python
# my_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name"""
    return f"Hello, {name}!"

@mcp.tool()
def calculate_age(birth_year: int, current_year: int = 2025) -> int:
    """Calculate age from birth year"""
    return current_year - birth_year

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Running**:
```bash
python my_server.py
```

**Testing with MCP Inspector**:
```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Launch inspector
mcp-inspector python my_server.py
```

**Reference**: `servers/math_server.py:1-21`

**See Also**: [Math Server](#math-server)

---

### Pattern 2: Creating a Client Integration

**Scenario**: Connect to multiple MCP servers and create a LangChain agent that can use all available tools.

**When to Use**:
- Building applications with multiple tool sources
- Integrating heterogeneous services
- Creating AI agents with diverse capabilities
- Testing multi-server architectures

**Steps**:

1. **Load environment variables**
```python
from dotenv import load_dotenv
load_dotenv()
```

2. **Configure MCP client**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "server1": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
    "server2": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    },
})
```

3. **Load tools**
```python
tools = await client.get_tools()
```

4. **Create agent**
```python
from langchain.agents import create_agent
agent = create_agent("openai:gpt-4.1", tools)
```

5. **Execute queries**
```python
response = await agent.ainvoke({"messages": "your query here"})
```

**Complete Example**:
```python
# my_client.py
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response, print_tools_summary

load_dotenv()

async def main():
    # Configure client
    client = MultiServerMCPClient({
        "math": {
            "url": "http://localhost:8001/mcp",
            "transport": "streamable_http",
        },
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
    })

    # Load tools
    print("Loading tools...")
    tools = await client.get_tools()
    print_tools_summary(tools)

    # Create agent
    agent = create_agent("openai:gpt-4.1", tools)

    # Execute query
    response = await agent.ainvoke({
        "messages": "What is 10 + 5, and what's the weather in Paris?"
    })

    # Display results
    display_agent_response(response, show_full_trace=True)

if __name__ == "__main__":
    asyncio.run(main())
```

**Running**:
```bash
# Prerequisites: Start servers
python servers/wrap_langchain_tools_server.py --port 8001
python servers/weather_server.py

# Run client
python my_client.py
```

**Reference**: `clients/integration_test.py:66-274`

**See Also**: [Integration Test Client](#integration-test-client)

---

### Pattern 3: Adding Custom Display Formatting

**Scenario**: You want to customize how agent responses are displayed for different audiences (end users, developers, logs).

**When to Use**:
- Building user-facing applications
- Debugging agent behavior
- Creating reports or documentation
- Extracting data programmatically

**Display Modes**:

**1. Full Trace (Debugging)**
```python
from display_utils import display_agent_response

# Show all messages with token usage
display_agent_response(response, show_full_trace=True, show_token_usage=True)
```

**Output**:
```
======================================================================
AGENT RESPONSE TRACE
======================================================================

01. HumanMessage: what is 5 + 3?
02. AIMessage → 🔧 tool_call(s): add
     └─ Tokens: input=120, output=20, total=140
03. ToolMessage [add]: ✓ 8
04. AIMessage: The sum of 5 and 3 is 8.
     └─ Tokens: input=145, output=12, total=157

======================================================================
```

**2. Minimal Display (End Users)**
```python
# Show only final answer
display_agent_response(response, show_full_trace=False)
```

**Output**:
```
💡 Final Answer: The sum of 5 and 3 is 8.
```

**3. Programmatic Extraction**
```python
from display_utils import get_final_answer

# Extract answer without displaying
answer = get_final_answer(response)
print(f"Result: {answer}")
```

**4. Custom Formatting**
```python
def custom_display(response):
    """Custom display for specific use case."""
    messages = response.get("messages", [])

    # Extract tool calls
    tool_calls = []
    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls'):
            tool_calls.extend(msg.tool_calls)

    # Extract final answer
    answer = get_final_answer(response)

    # Custom output
    print(f"Tools Used: {len(tool_calls)}")
    print(f"Final Answer: {answer}")

custom_display(response)
```

**Complete Example**:
```python
import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from display_utils import display_agent_response, get_final_answer

async def demonstrate_displays():
    # Setup (abbreviated)
    client = MultiServerMCPClient({...})
    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)

    response = await agent.ainvoke({"messages": "what is (10 + 5) * 2?"})

    print("=== DEBUGGING MODE ===")
    display_agent_response(response, show_full_trace=True, show_token_usage=True)

    print("\n=== USER-FRIENDLY MODE ===")
    display_agent_response(response, show_full_trace=False)

    print("\n=== PROGRAMMATIC MODE ===")
    answer = get_final_answer(response)
    if answer and "30" in answer:
        print("✓ Correct answer!")

    print("\n=== LOGGING MODE ===")
    import logging
    logging.info(f"Agent response: {get_final_answer(response)}")

asyncio.run(demonstrate_displays())
```

**Reference**: `clients/display_utils.py:9-153`

**See Also**:
- [display_agent_response](#display_agent_responseresponse-dictstr-any-show_full_trace-bool--true-show_token_usage-bool--false-return_final_answer-bool--false---optionalstr)
- [get_final_answer](#get_final_answerresponse-dictstr-any---optionalstr)

---

### Pattern 4: Wrapping LangChain Tools as MCP Server

**Scenario**: You have existing LangChain tools (decorated with `@tool`) and want to expose them as an MCP server for use by other clients.

**When to Use**:
- Migrating existing LangChain tooling
- Sharing tools across multiple applications
- Creating reusable tool services
- Standardizing on MCP protocol

**Steps**:

1. **Define LangChain tools**
```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Result: {param}"
```

2. **Convert to FastMCP**
```python
from langchain_mcp_adapters.tools import to_fastmcp

fastmcp_tool = to_fastmcp(my_tool)
```

3. **Create FastMCP server**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer", tools=[fastmcp_tool])
```

4. **Run with transport**
```python
mcp.run(transport="streamable-http")
```

**Complete Example**:
```python
# langchain_tools_to_mcp.py
import argparse
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Define LangChain tools
@tool
def search_documents(query: str, limit: int = 10) -> list:
    """Search through documents"""
    # Implementation here
    return [{"title": f"Doc {i}", "snippet": query} for i in range(limit)]

@tool
def summarize_text(text: str, max_words: int = 100) -> str:
    """Summarize text to specified word count"""
    # Implementation here
    words = text.split()[:max_words]
    return " ".join(words) + "..."

@tool
def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target language"""
    # Implementation here
    return f"[{target_lang}] {text}"

# Convert to FastMCP
fastmcp_search = to_fastmcp(search_documents)
fastmcp_summarize = to_fastmcp(summarize_text)
fastmcp_translate = to_fastmcp(translate_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangChain Tools MCP Server")
    parser.add_argument("--port", type=int, default=8002)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()

    print(f"Starting LangChain Tools MCP Server on {args.host}:{args.port}")
    print("Available tools: search_documents, summarize_text, translate_text")

    mcp = FastMCP(
        "LangChain Tools Server",
        tools=[fastmcp_search, fastmcp_summarize, fastmcp_translate],
        host=args.host,
        port=args.port
    )

    mcp.run(transport="streamable-http")
```

**Running**:
```bash
# Start server
python langchain_tools_to_mcp.py --port 8002

# Test with client
python -c "
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test():
    client = MultiServerMCPClient({
        'langchain_tools': {
            'url': 'http://localhost:8002/mcp',
            'transport': 'streamable_http',
        }
    })
    tools = await client.get_tools()
    print(f'Loaded {len(tools)} tools')

asyncio.run(test())
"
```

**Advanced: Tool Dependencies**
```python
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
import os

# Tool that requires environment variables
@tool
def call_api(endpoint: str, method: str = "GET") -> dict:
    """Call external API"""
    api_key = os.environ.get("API_KEY")
    # Use api_key in implementation
    return {"status": "success", "endpoint": endpoint}

# Convert and create server
fastmcp_api = to_fastmcp(call_api)
mcp = FastMCP("API Tools", tools=[fastmcp_api])

# Environment variables are inherited by the server process
mcp.run(transport="streamable-http")
```

**Reference**: `servers/wrap_langchain_tools_server.py:1-55`

**See Also**: [LangChain Tools Wrapper Server](#langchain-tools-wrapper-server)

---

## Examples

### Example 1: Basic Math Operations

**Goal**: Demonstrates the simplest MCP server implementation with stdio transport, showing how to define and expose tools using FastMCP decorators.

**Source Reference**: `servers/math_server.py:1-21`

**Code**:
```python
# servers/math_server.py
from mcp.server.fastmcp import FastMCP

# Create server instance
mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    # Run with stdio transport (for subprocess communication)
    mcp.run(transport="stdio")
```

**Running**:
```bash
# Start the server
python servers/math_server.py

# The server will wait for stdio input from an MCP client
```

**Testing with MCP Inspector**:
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test the server
mcp-inspector python servers/math_server.py
```

**Expected Output in Inspector**:
- Server name: "Math"
- Available tools: add, multiply
- Tool schemas with parameter types

**Integration Example**:
```python
# Using in Python client with subprocess
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_math_server():
    client = MultiServerMCPClient({
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["servers/math_server.py"],
        }
    })

    tools = await client.get_tools()
    print(f"Loaded tools: {[t.name for t in tools]}")
    # Output: Loaded tools: ['add', 'multiply']

asyncio.run(test_math_server())
```

**Key Concepts**:
- FastMCP simplifies server creation
- `@mcp.tool()` decorator automatically generates tool schema
- stdio transport enables subprocess-based clients
- Type hints define parameter types

---

### Example 2: Multi-Server Integration

**Goal**: Demonstrates connecting to multiple MCP servers (different transports and locations) and using an agent to orchestrate tools from both servers.

**Source Reference**: `clients/integration_test.py:66-178`

**Code**:
```python
# multi_server_demo.py
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response, print_tools_summary

load_dotenv()

async def main():
    print("=" * 70)
    print("MULTI-SERVER MCP INTEGRATION DEMO")
    print("=" * 70 + "\n")

    # Configure client to connect to multiple servers
    print("Connecting to MCP servers...")
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

    # Load tools from all servers
    print("Loading tools from MCP servers...\n")
    tools = await client.get_tools()
    print_tools_summary(tools)

    # Create agent with all tools
    agent = create_agent("openai:gpt-4.1", tools)

    # Query requiring math server
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Math Query (uses langchain_math server)")
    print("=" * 70 + "\n")

    math_response = await agent.ainvoke({
        "messages": "Calculate (15 + 27) * 3"
    })
    display_agent_response(math_response, show_full_trace=True, show_token_usage=True)

    # Query requiring weather server
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Weather Query (uses weather server)")
    print("=" * 70 + "\n")

    weather_response = await agent.ainvoke({
        "messages": "What is the weather in Tokyo?"
    })
    display_agent_response(weather_response, show_full_trace=True, show_token_usage=True)

    # Query requiring both servers
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Combined Query (uses both servers)")
    print("=" * 70 + "\n")

    combined_response = await agent.ainvoke({
        "messages": "If I multiply 8 by 6, and the weather in London is nice, should I go for a walk?"
    })
    display_agent_response(combined_response, show_full_trace=True, show_token_usage=True)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
```

**Running**:
```bash
# Terminal 1: Start math server
python servers/wrap_langchain_tools_server.py --port 8001

# Terminal 2: Start weather server
python servers/weather_server.py

# Terminal 3: Run demo
python multi_server_demo.py
```

**Output**:
```
======================================================================
MULTI-SERVER MCP INTEGRATION DEMO
======================================================================

Connecting to MCP servers...
Loading tools from MCP servers...

======================================================================
AVAILABLE TOOLS (3 total)
======================================================================

01. add
    └─ Add two numbers
02. multiply
    └─ Multiply two numbers
03. get_weather
    └─ Get weather for location.

======================================================================

======================================================================
EXAMPLE 1: Math Query (uses langchain_math server)
======================================================================

======================================================================
AGENT RESPONSE TRACE
======================================================================

01. HumanMessage: Calculate (15 + 27) * 3
02. AIMessage → 🔧 tool_call(s): add
     └─ Tokens: input=150, output=25, total=175
03. ToolMessage [add]: ✓ 42
04. AIMessage → 🔧 tool_call(s): multiply
     └─ Tokens: input=180, output=25, total=205
05. ToolMessage [multiply]: ✓ 126
06. AIMessage: The result is 126.
     └─ Tokens: input=200, output=10, total=210

======================================================================

[... continues with other examples ...]
```

**Key Concepts**:
- Single client connects to multiple servers
- Tools from different servers appear in same tool list
- Agent automatically selects appropriate server
- Supports mixing transports (stdio, streamable-http, sse)

---

### Example 3: Custom Message Display

**Goal**: Shows different ways to display and extract information from agent responses for various use cases.

**Source Reference**: `clients/display_utils.py:9-153`, `clients/integration_test.py:201-217`

**Code**:
```python
# custom_display_demo.py
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response, get_final_answer

load_dotenv()

async def main():
    # Setup (abbreviated for clarity)
    client = MultiServerMCPClient({
        "math": {
            "url": "http://localhost:8001/mcp",
            "transport": "streamable_http",
        },
    })
    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)

    # Execute a query
    response = await agent.ainvoke({"messages": "multiply 7 and 9"})

    print("=" * 70)
    print("DISPLAY MODE 1: Full Debug Trace")
    print("=" * 70)
    display_agent_response(response, show_full_trace=True, show_token_usage=True)

    print("\n" + "=" * 70)
    print("DISPLAY MODE 2: User-Friendly (Final Answer Only)")
    print("=" * 70)
    display_agent_response(response, show_full_trace=False)

    print("\n" + "=" * 70)
    print("DISPLAY MODE 3: Programmatic Extraction")
    print("=" * 70)
    answer = get_final_answer(response)
    print(f"Extracted answer: {answer}")
    print(f"Type: {type(answer)}")
    print(f"Length: {len(answer)} characters")
    print(f"Contains '63': {'63' in str(answer)}")

    print("\n" + "=" * 70)
    print("DISPLAY MODE 4: Custom Business Logic")
    print("=" * 70)

    # Custom processing
    answer = get_final_answer(response)
    if answer:
        # Extract numeric value
        import re
        numbers = re.findall(r'\d+', answer)
        if numbers:
            result = int(numbers[0])
            print(f"Numeric result: {result}")
            print(f"Is correct (7*9=63): {result == 63}")

            # Business logic
            if result > 50:
                print("Result is large, flagging for review")
            else:
                print("Result is within normal range")

    print("\n" + "=" * 70)
    print("DISPLAY MODE 5: Structured Logging")
    print("=" * 70)

    import json
    from langchain_core.messages import AIMessage, ToolMessage

    # Extract structured data
    messages = response.get("messages", [])
    log_entry = {
        "query": messages[0].content if messages else "unknown",
        "tool_calls": [],
        "final_answer": get_final_answer(response),
        "message_count": len(messages),
    }

    for msg in messages:
        if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls'):
            for tc in msg.tool_calls:
                log_entry["tool_calls"].append({
                    "name": tc['name'],
                    "args": tc['args'],
                })

    print(json.dumps(log_entry, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```

**Running**:
```bash
# Prerequisites: Start math server
python servers/wrap_langchain_tools_server.py --port 8001

# Run demo
python custom_display_demo.py
```

**Output**:
```
======================================================================
DISPLAY MODE 1: Full Debug Trace
======================================================================

======================================================================
AGENT RESPONSE TRACE
======================================================================

01. HumanMessage: multiply 7 and 9
02. AIMessage → 🔧 tool_call(s): multiply
     └─ Tokens: input=120, output=20, total=140
03. ToolMessage [multiply]: ✓ 63
04. AIMessage: 7 multiplied by 9 equals 63.
     └─ Tokens: input=145, output=12, total=157

======================================================================

======================================================================
DISPLAY MODE 2: User-Friendly (Final Answer Only)
======================================================================

💡 Final Answer: 7 multiplied by 9 equals 63.

======================================================================
DISPLAY MODE 3: Programmatic Extraction
======================================================================
Extracted answer: 7 multiplied by 9 equals 63.
Type: <class 'str'>
Length: 33 characters
Contains '63': True

======================================================================
DISPLAY MODE 4: Custom Business Logic
======================================================================
Numeric result: 63
Is correct (7*9=63): True
Result is large, flagging for review

======================================================================
DISPLAY MODE 5: Structured Logging
======================================================================
{
  "query": "multiply 7 and 9",
  "tool_calls": [
    {
      "name": "multiply",
      "args": {
        "a": 7,
        "b": 9
      }
    }
  ],
  "final_answer": "7 multiplied by 9 equals 63.",
  "message_count": 4
}
```

**Key Concepts**:
- Multiple display modes for different audiences
- Programmatic extraction for automation
- Custom business logic integration
- Structured logging for monitoring

---

### Example 4: Weather API Integration

**Goal**: Demonstrates creating an MCP server with streamable-http transport, command-line configuration, and async tool implementation.

**Source Reference**: `servers/weather_server.py:1-61`

**Code**:
```python
# servers/weather_server.py
"""
Weather MCP Server

A simple MCP server that provides mock weather information using streamable-http transport.
"""

import argparse
from mcp.server.fastmcp import FastMCP

# Create FastMCP instance
mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location.

    Args:
        location: The location to get weather for (e.g., "NYC", "London", "Tokyo")

    Returns:
        str: Weather description for the requested location
    """
    # Mock implementation
    return f"It's always sunny in {location}"

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    args = parser.parse_args()

    # Configure server
    mcp.host = args.host
    mcp.port = args.port

    print(f"Starting Weather MCP Server on http://{args.host}:{args.port}/mcp")

    # Run with streamable-http transport
    mcp.run(transport="streamable-http")
```

**Running**:
```bash
# Default configuration
python servers/weather_server.py

# Custom port
python servers/weather_server.py --port 8080

# Network accessible
python servers/weather_server.py --host 0.0.0.0 --port 8080
```

**Output**:
```
Starting Weather MCP Server on http://127.0.0.1:8000/mcp
```

**Testing with curl**:
```bash
# List tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

# Call tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_weather",
      "arguments": {
        "location": "Paris"
      }
    }
  }'
```

**Client Integration**:
```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response

async def test_weather():
    # Connect to weather server
    client = MultiServerMCPClient({
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
    })

    # Load tools
    tools = await client.get_tools()
    print(f"Available tools: {[t.name for t in tools]}")

    # Create agent
    agent = create_agent("openai:gpt-4.1", tools)

    # Test queries
    queries = [
        "What's the weather in Tokyo?",
        "How's the weather in both London and Paris?",
        "Is it sunny in NYC?",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        response = await agent.ainvoke({"messages": query})
        display_agent_response(response, show_full_trace=False)

asyncio.run(test_weather())
```

**Real API Integration**:
```python
# weather_server_real.py
import argparse
import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get real weather for location using OpenWeatherMap API.

    Args:
        location: City name (e.g., "London", "Tokyo")

    Returns:
        str: Weather description
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OPENWEATHER_API_KEY not set"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": location, "appid": api_key, "units": "metric"}
        )

        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"Weather in {location}: {desc}, {temp}°C"
        else:
            return f"Error getting weather for {location}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()

    mcp.host = args.host
    mcp.port = args.port

    print(f"Starting Real Weather MCP Server on http://{args.host}:{args.port}/mcp")
    mcp.run(transport="streamable-http")
```

**Key Concepts**:
- streamable-http enables HTTP-based clients
- Async tools support I/O operations
- Command-line args for flexible deployment
- Easy migration from mock to real APIs

---

## Best Practices

### Server Development

#### 1. Use Type Hints

**Why**: Type hints enable automatic schema generation and provide better IDE support.

**Example**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

# ❌ Bad: No type hints
@mcp.tool()
def process_data(data, options):
    return data

# ✅ Good: Explicit type hints
@mcp.tool()
def process_data(data: dict, options: list[str]) -> dict:
    """Process data with specified options."""
    return {"processed": data, "used_options": options}

# ✅ Better: Type hints with defaults
from typing import Optional

@mcp.tool()
def process_data(
    data: dict,
    options: list[str],
    verbose: bool = False,
    max_items: Optional[int] = None
) -> dict:
    """Process data with specified options.

    Args:
        data: Input data dictionary
        options: Processing options
        verbose: Enable verbose output
        max_items: Maximum items to process (None for unlimited)
    """
    return {"processed": data, "used_options": options}
```

---

#### 2. Implement Error Handling

**Why**: Graceful error handling improves reliability and debugging.

**Example**:
```python
from mcp.server.fastmcp import FastMCP
import logging

mcp = FastMCP("MyServer")
logger = logging.getLogger(__name__)

# ❌ Bad: No error handling
@mcp.tool()
def divide(a: int, b: int) -> float:
    return a / b

# ✅ Good: Explicit error handling
@mcp.tool()
def divide(a: int, b: int) -> str:
    """Divide two numbers safely."""
    try:
        result = a / b
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        logger.error(f"Unexpected error in divide: {e}")
        return f"Error: {str(e)}"

# ✅ Better: Validation and detailed errors
@mcp.tool()
async def fetch_data(url: str, timeout: int = 30) -> dict:
    """Fetch data from URL with error handling."""
    import httpx

    # Validate input
    if not url.startswith(('http://', 'https://')):
        return {"error": "Invalid URL scheme", "url": url}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()
            return {"status": "success", "data": response.json()}

    except httpx.TimeoutException:
        return {"error": "Request timeout", "timeout": timeout}

    except httpx.HTTPStatusError as e:
        return {"error": "HTTP error", "status_code": e.response.status_code}

    except Exception as e:
        logger.exception("Unexpected error fetching data")
        return {"error": str(e), "type": type(e).__name__}
```

---

#### 3. Document Tool Schemas

**Why**: Good documentation helps LLMs understand when and how to use tools.

**Example**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")

# ❌ Bad: No documentation
@mcp.tool()
def search(q: str, n: int = 10) -> list:
    return []

# ✅ Good: Clear docstring
@mcp.tool()
def search(query: str, limit: int = 10) -> list[dict]:
    """Search for items matching the query.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List of matching items with title and snippet
    """
    return []

# ✅ Better: Detailed documentation with examples
@mcp.tool()
def search(
    query: str,
    limit: int = 10,
    category: str = "all",
    sort_by: str = "relevance"
) -> list[dict]:
    """Search for items matching the query.

    This tool searches across all indexed content and returns
    matching results sorted by relevance or date.

    Args:
        query: Search query string (supports boolean operators: AND, OR, NOT)
        limit: Maximum number of results (1-100, default: 10)
        category: Filter by category (all, docs, code, issues)
        sort_by: Sort order (relevance, date, popularity)

    Returns:
        List of search results, each containing:
        - title: Result title
        - snippet: Text excerpt
        - url: Link to full content
        - score: Relevance score (0-1)

    Examples:
        - Simple search: query="python async"
        - Boolean search: query="python AND (async OR asyncio)"
        - Category filter: query="error handling", category="docs"
    """
    return []
```

---

#### 4. Test with MCP Inspector

**Why**: Validates server implementation before integration.

**Example**:
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test stdio server
mcp-inspector python servers/my_server.py

# Test with environment variables
MYVAR=value mcp-inspector python servers/my_server.py

# Test HTTP server (in browser)
# 1. Start your server:
python servers/my_server.py --port 8000

# 2. Visit in browser:
# http://localhost:8000/mcp
```

**Server Testing Checklist**:
```python
# test_server.py
"""
Checklist for MCP server testing:

1. ✓ Server starts without errors
2. ✓ All tools are listed correctly
3. ✓ Tool schemas are valid JSON Schema
4. ✓ Tool execution returns expected format
5. ✓ Error cases are handled gracefully
6. ✓ Environment variables are loaded
7. ✓ Documentation is clear and accurate
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_server():
    client = MultiServerMCPClient({
        "test": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    })

    # Test 1: Tool discovery
    tools = await client.get_tools()
    assert len(tools) > 0, "No tools found"
    print(f"✓ Found {len(tools)} tools")

    # Test 2: Tool schemas
    for tool in tools:
        assert hasattr(tool, 'name'), f"Tool missing name"
        assert hasattr(tool, 'description'), f"Tool {tool.name} missing description"
        print(f"✓ Tool {tool.name}: {tool.description[:50]}...")

    # Test 3: Tool execution (requires agent)
    from langchain.agents import create_agent
    agent = create_agent("openai:gpt-4.1", tools)

    response = await agent.ainvoke({"messages": "test query"})
    assert "messages" in response, "Invalid response format"
    print("✓ Tool execution successful")

if __name__ == "__main__":
    asyncio.run(test_server())
```

---

### Client Development

#### 1. Manage Environment Variables

**Why**: Secure credential management and flexible configuration.

**Example**:
```python
# ❌ Bad: Hardcoded credentials
import openai
openai.api_key = "sk-proj-1234567890"

# ✅ Good: Use python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env file

# Access variables
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set")

# ✅ Better: Validation and defaults
from dotenv import load_dotenv
import os
import sys

def load_config():
    """Load and validate configuration."""
    load_dotenv()

    config = {
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "langsmith_tracing": os.environ.get("LANGSMITH_TRACING", "false").lower() == "true",
        "langsmith_project": os.environ.get("LANGSMITH_PROJECT", "default"),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    }

    # Validate required variables
    if not config["openai_api_key"]:
        print("Error: OPENAI_API_KEY not set", file=sys.stderr)
        print("Please set it in .env file or environment", file=sys.stderr)
        sys.exit(1)

    return config

config = load_config()
```

**.env file best practices**:
```bash
# .env
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional - LangSmith tracing
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=my-project
LANGSMITH_API_KEY=lsv2_pt_your-key-here

# Optional - Logging
LOG_LEVEL=INFO

# Optional - Custom settings
MCP_TIMEOUT=30
MCP_MAX_RETRIES=3
```

**.gitignore**:
```
# Never commit credentials
.env
.env.local
.env.*.local
```

---

#### 2. Handle Connection Errors

**Why**: Network issues and server unavailability are common.

**Example**:
```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
import logging

logger = logging.getLogger(__name__)

# ❌ Bad: No error handling
async def connect():
    client = MultiServerMCPClient({
        "server": {"url": "http://localhost:8000/mcp", "transport": "streamable_http"}
    })
    tools = await client.get_tools()
    return tools

# ✅ Good: Basic error handling
async def connect_with_retry():
    try:
        client = MultiServerMCPClient({
            "server": {"url": "http://localhost:8000/mcp", "transport": "streamable_http"}
        })
        tools = await client.get_tools()
        return tools
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return []

# ✅ Better: Retry logic with backoff
async def connect_robust(max_retries: int = 3, timeout: int = 30):
    """Connect to MCP server with retry logic."""

    for attempt in range(max_retries):
        try:
            client = MultiServerMCPClient({
                "server": {
                    "url": "http://localhost:8000/mcp",
                    "transport": "streamable_http",
                    "timeout": timeout,
                }
            })

            tools = await client.get_tools()
            logger.info(f"Connected successfully, loaded {len(tools)} tools")
            return client, tools

        except ConnectionError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("Max retries reached, giving up")
                raise

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

# Usage
async def main():
    try:
        client, tools = await connect_robust()
        print(f"Ready with {len(tools)} tools")
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("Please check:")
        print("  1. Server is running")
        print("  2. Port is correct")
        print("  3. Network connectivity")
```

---

#### 3. Implement Display Utilities

**Why**: Consistent, user-friendly output across different use cases.

**Example**:
```python
# See display_utils.py for full implementation

from display_utils import (
    display_agent_response,
    get_final_answer,
    print_tools_summary
)

async def demo():
    # Load tools
    tools = await client.get_tools()
    print_tools_summary(tools)  # Consistent tool display

    # Execute query
    response = await agent.ainvoke({"messages": "test"})

    # Different display modes
    display_agent_response(response, show_full_trace=True)  # Debug
    display_agent_response(response, show_full_trace=False)  # User
    answer = get_final_answer(response)  # Programmatic
```

---

#### 4. Use Async/Await Properly

**Why**: Proper async usage prevents blocking and improves performance.

**Example**:
```python
import asyncio

# ❌ Bad: Mixing sync and async incorrectly
def bad_example():
    client = MultiServerMCPClient({...})
    tools = client.get_tools()  # This won't work!
    return tools

# ✅ Good: Consistent async
async def good_example():
    client = MultiServerMCPClient({...})
    tools = await client.get_tools()
    return tools

# ✅ Better: Proper async patterns
async def fetch_tools_parallel():
    """Fetch tools from multiple sources in parallel."""
    clients = {
        "math": MultiServerMCPClient({"math": {...}}),
        "weather": MultiServerMCPClient({"weather": {...}}),
    }

    # Parallel execution
    tasks = [client.get_tools() for client in clients.values()]
    results = await asyncio.gather(*tasks)

    # Combine results
    all_tools = []
    for tools in results:
        all_tools.extend(tools)

    return all_tools

# Running async code
if __name__ == "__main__":
    # ❌ Bad
    # fetch_tools_parallel()  # Won't work

    # ✅ Good
    asyncio.run(fetch_tools_parallel())

    # ✅ In Jupyter/IPython
    # await fetch_tools_parallel()
```

---

### Configuration Management

#### 1. Use .env Files

**Why**: Separate configuration from code, support multiple environments.

**Example**:
```python
# config.py
from dotenv import load_dotenv
import os
from typing import Dict, Any

class Config:
    """Application configuration."""

    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)
        self._load_config()

    def _load_config(self):
        """Load all configuration values."""
        # API Keys
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.calcom_api_key = os.environ.get("CALCOM_API_KEY")

        # LangSmith
        self.langsmith_tracing = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "default")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

        # MCP Servers
        self.math_server_url = os.getenv("MATH_SERVER_URL", "http://localhost:8001/mcp")
        self.weather_server_url = os.getenv("WEATHER_SERVER_URL", "http://localhost:8000/mcp")

        # App Settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.timeout = int(os.getenv("TIMEOUT", "30"))

    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP client configuration."""
        return {
            "math": {
                "url": self.math_server_url,
                "transport": "streamable_http",
            },
            "weather": {
                "url": self.weather_server_url,
                "transport": "streamable_http",
            },
        }

    def validate(self):
        """Validate required configuration."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")

# Usage
config = Config()
config.validate()

client = MultiServerMCPClient(config.get_mcp_config())
```

---

#### 2. Validate Configuration

**Why**: Catch configuration errors early.

**Example**:
```python
from typing import Dict, Any
import sys

def validate_mcp_config(config: Dict[str, Any]) -> bool:
    """Validate MCP server configuration."""

    errors = []

    for server_name, server_config in config.items():
        # Check required fields
        if "transport" not in server_config:
            errors.append(f"{server_name}: missing 'transport' field")

        # Validate transport-specific fields
        transport = server_config.get("transport")

        if transport in ["streamable_http", "sse"]:
            if "url" not in server_config:
                errors.append(f"{server_name}: missing 'url' for HTTP transport")

        elif transport == "stdio":
            if "command" not in server_config:
                errors.append(f"{server_name}: missing 'command' for stdio transport")

        else:
            errors.append(f"{server_name}: unknown transport '{transport}'")

    if errors:
        print("Configuration errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False

    return True

# Usage
config = {...}
if not validate_mcp_config(config):
    sys.exit(1)
```

---

#### 3. Separate Dev/Prod Configs

**Why**: Different settings for different environments.

**Example**:
```bash
# .env.development
OPENAI_API_KEY=sk-dev-...
LOG_LEVEL=DEBUG
MATH_SERVER_URL=http://localhost:8001/mcp
LANGSMITH_TRACING=true

# .env.production
OPENAI_API_KEY=sk-prod-...
LOG_LEVEL=INFO
MATH_SERVER_URL=https://api.example.com/mcp
LANGSMITH_TRACING=false
```

```python
# config.py
import os
from dotenv import load_dotenv

def get_env_file() -> str:
    """Determine which .env file to load."""
    env = os.getenv("ENV", "development")

    env_files = {
        "development": ".env.development",
        "staging": ".env.staging",
        "production": ".env.production",
    }

    return env_files.get(env, ".env")

# Load appropriate config
load_dotenv(get_env_file())
```

```bash
# Run in different environments
ENV=development python my_app.py
ENV=production python my_app.py
```

---

## Troubleshooting

### Common Issues

#### Issue: "Server not found" or Connection Refused

**Symptoms**:
```
ConnectionRefusedError: [Errno 111] Connect call failed ('127.0.0.1', 8000)
```

**Cause**: MCP server is not running or running on different port/host.

**Solution**:

1. **Verify server is running**:
```bash
# Check if server process is running
ps aux | grep python | grep server

# Check if port is listening
netstat -tuln | grep 8000
# or
lsof -i :8000
```

2. **Start the server**:
```bash
# For weather server
python servers/weather_server.py --port 8000

# For math server
python servers/wrap_langchain_tools_server.py --port 8001
```

3. **Check host/port configuration**:
```python
# Client configuration must match server settings
client = MultiServerMCPClient({
    "weather": {
        "url": "http://localhost:8000/mcp",  # Must match server port
        "transport": "streamable_http",
    }
})
```

4. **Test server directly**:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

**Reference**: `servers/weather_server.py:59`, `clients/integration_test.py:87-98`

---

#### Issue: "Tool execution failed" or Tool Returns Error

**Symptoms**:
```
ToolMessage [add]: ❌ Error: Invalid arguments
```

**Cause**: Invalid arguments passed to tool or server-side error.

**Solution**:

1. **Check tool schema**:
```python
from display_utils import print_tools_summary

tools = await client.get_tools()
print_tools_summary(tools)

# Inspect specific tool
for tool in tools:
    if tool.name == "add":
        print(f"Schema: {tool.args_schema}")
```

2. **Validate arguments before calling**:
```python
# ❌ Bad: No validation
response = await agent.ainvoke({"messages": "add 5 and hello"})

# ✅ Good: Clear numeric inputs
response = await agent.ainvoke({"messages": "add 5 and 3"})
```

3. **Check server logs**:
```bash
# Run server with debug logging
LOG_LEVEL=DEBUG python servers/my_server.py
```

4. **Add error handling in tool**:
```python
@mcp.tool()
def add(a: int, b: int) -> str:
    """Add two numbers"""
    try:
        result = int(a) + int(b)
        return f"Result: {result}"
    except (ValueError, TypeError) as e:
        return f"Error: Invalid arguments - {e}"
```

**Reference**: `servers/math_server.py:8-16`, `clients/display_utils.py:72-79`

---

#### Issue: "OPENAI_API_KEY not set" or Authentication Error

**Symptoms**:
```
openai.AuthenticationError: No API key provided
```

**Cause**: Environment variable not loaded or invalid API key.

**Solution**:

1. **Create .env file**:
```bash
cat > .env << EOF
OPENAI_API_KEY=sk-proj-your-actual-key-here
EOF
```

2. **Verify .env is loaded**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY not found")
else:
    print(f"✓ API key loaded: {api_key[:10]}...")
```

3. **Check .env location**:
```python
# .env must be in current working directory or specify path
load_dotenv(".env")  # Current directory
load_dotenv("/path/to/.env")  # Specific path
```

4. **Verify API key validity**:
```bash
# Test with OpenAI CLI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Reference**: `.env.example:1`, `clients/integration_test.py:63`

---

#### Issue: Import Errors or Module Not Found

**Symptoms**:
```
ModuleNotFoundError: No module named 'langchain_mcp_adapters'
```

**Cause**: Dependencies not installed or virtual environment not activated.

**Solution**:

1. **Install dependencies**:
```bash
# Using uv (recommended)
uv pip install -e .

# Using pip
pip install -e .

# Install specific package
pip install langchain-mcp-adapters>=0.1.11
```

2. **Verify installation**:
```bash
pip list | grep langchain
pip list | grep mcp
```

3. **Check Python version**:
```bash
python --version
# Should be >= 3.13
```

4. **Activate virtual environment**:
```bash
# Create venv if needed
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows
```

**Reference**: `pyproject.toml:7-19`

---

#### Issue: Agent Not Using Tools or Wrong Tool Selected

**Symptoms**:
- Agent provides direct answer without calling tools
- Agent calls wrong tool for the task

**Cause**: Unclear prompts or poor tool descriptions.

**Solution**:

1. **Improve tool descriptions**:
```python
# ❌ Bad description
@mcp.tool()
def add(a: int, b: int) -> int:
    """Adds numbers"""
    return a + b

# ✅ Good description
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together.

    Use this tool when you need to perform arithmetic addition.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
```

2. **Make prompts more explicit**:
```python
# ❌ Vague prompt
response = await agent.ainvoke({"messages": "5 plus 3"})

# ✅ Explicit prompt
response = await agent.ainvoke({
    "messages": "Use the add tool to calculate 5 + 3"
})
```

3. **Check tool visibility**:
```python
from display_utils import print_tools_summary

tools = await client.get_tools()
print_tools_summary(tools)  # Verify all tools are loaded
```

4. **Enable trace logging**:
```python
import os
os.environ["LANGSMITH_TRACING"] = "true"

# View traces at https://smith.langchain.com/
```

**Reference**: `servers/math_server.py:8-16`, `clients/integration_test.py:106-107`

---

#### Issue: Async/Await Errors

**Symptoms**:
```
RuntimeWarning: coroutine 'get_tools' was never awaited
```

**Cause**: Forgetting to use `await` with async functions.

**Solution**:

1. **Always await async functions**:
```python
# ❌ Wrong
tools = client.get_tools()

# ✅ Correct
tools = await client.get_tools()
```

2. **Use asyncio.run for top-level**:
```python
import asyncio

async def main():
    tools = await client.get_tools()
    # ... rest of code

# ❌ Wrong
main()

# ✅ Correct
asyncio.run(main())
```

3. **In Jupyter notebooks**:
```python
# Just use await directly
tools = await client.get_tools()
```

**Reference**: `clients/integration_test.py:274`

---

## API Versioning

**Current Version**: 0.1.0

**Versioning Strategy**: This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

**Version History**:
- **0.1.0** (Initial Release): Core MCP server/client implementations, display utilities, example integrations

**Compatibility**:
- Python: >= 3.13
- LangChain: >= 0.3.19
- langchain-mcp-adapters: >= 0.1.11
- mcp: >= 1.6.0

**Checking Version**:
```python
import importlib.metadata

# Check package versions
print(f"langchain: {importlib.metadata.version('langchain')}")
print(f"langchain-mcp-adapters: {importlib.metadata.version('langchain-mcp-adapters')}")
print(f"mcp: {importlib.metadata.version('mcp')}")
```

**Source**: `pyproject.toml:2`, `servers/__init__.py:13`

---

## Deprecations

**Current Status**: No deprecated APIs in version 0.1.0.

**Future Deprecation Policy**:
- Deprecated features will be marked in documentation
- Deprecation warnings will be issued in code
- Minimum 2 minor versions before removal
- Migration guides provided for all breaking changes

**Monitoring for Deprecations**:
```python
import warnings

# Enable deprecation warnings
warnings.filterwarnings('default', category=DeprecationWarning)
```

---

## Migration Guides

### Future: LangGraph create_react_agent to LangChain create_agent

**Note**: This migration is demonstrated in `clients/integration_test.py` comments.

**From** (LangGraph):
```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent("openai:gpt-4.1", tools)
```

**To** (LangChain):
```python
from langchain.agents import create_agent

agent = create_agent("openai:gpt-4.1", tools)
```

**Changes**:
- Import path changed
- API remains compatible
- Same parameters and return types

**Reference**: `clients/integration_test.py:57-59`, `clients/integration_test_mcp_json.py:97`

**Migration Checklist**:
- [ ] Update imports
- [ ] Test agent initialization
- [ ] Verify tool execution
- [ ] Check response format
- [ ] Update documentation

---

**Document Version**: 1.0
**Last Updated**: 2025-10-24
**Project Version**: 0.1.0
**Maintainer**: AIE Cohort 8
