# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **lightweight educational repository** for teaching Model Context Protocol (MCP) core concepts through clear, runnable examples. Created for AI Engineering Bootcamp Cohort 8, Session 13.

**Core Teaching Goals:**
1. **Multi-server MCP architecture** - How to connect agents to multiple MCP servers simultaneously
2. **Transport types** - stdio vs streamable-http (and when to use each)
3. **Tool conversion** - Converting LangChain tools to MCP format
4. **Agent orchestration** - How LangGraph agents work with MCP tools

## Environment Setup

### Python Environment (Python 3.13)

```bash
# Create virtual environment
uv venv --python 3.13

# Activate virtual environment
source .venv/bin/activate  # Linux/WSL/Mac

# Install dependencies in editable mode
uv pip install -e .
```

### Environment Variables

Required environment variables in `.env` file:
- `OPENAI_API_KEY` - Required for LLM operations
- `LANGCHAIN_API_KEY` - Optional, for LangSmith tracing
- `LANGSMITH_TRACING` - Optional, set to "true" for tracing

See [.env.example](.env.example) for template.

## Project Structure

Clean, focused structure for teaching MCP concepts:

```
aie8-s13-langchain-mcp/
├── servers/                          # 🎯 MCP server examples
│   ├── math_server.py               # Example: stdio transport
│   ├── weather_server.py            # Example: streamable-http (port 8000)
│   └── langchain_tools_server.py    # Example: LangChain→MCP conversion (port 8001)
│
├── clients/                          # 🎯 Client examples & utilities
│   ├── integration_test.py          # Standalone Python test suite
│   ├── client.ipynb                 # Interactive Jupyter notebook
│   └── display_utils.py             # Agent response formatting utilities
│
├── docs/
│   └── TRANSPORT_COMPARISON.md      # 📚 Educational: stdio vs HTTP
│
├── examples/servers/                 # Additional server examples
│   └── streamable-http-stateless/   # FastMCP stateless HTTP example
│
├── .mcp.json                         # MCP server registry for Claude Desktop
├── .env.example                      # Environment template
└── pyproject.toml                    # Package configuration
```

**Focus:** The code in `servers/` and `clients/` are the teaching materials. Everything else supports running these examples.

## Common Development Commands

### Starting MCP Servers

MCP servers must run in separate terminals/processes before clients can connect.

**Terminal 1 - Weather Server (port 8000):**
```bash
source .venv/bin/activate
python servers/weather_server.py
```

**Terminal 2 - LangChain Tools Server (port 8001):**
```bash
source .venv/bin/activate
python servers/langchain_tools_server.py --port 8001

# Custom port
python servers/langchain_tools_server.py --port 8002

# Network access (default is 127.0.0.1)
python servers/langchain_tools_server.py --host 0.0.0.0 --port 8001
```

**Math Server (stdio transport, for testing):**
```bash
source .venv/bin/activate
python servers/math_server.py
```

### Running Client Examples

**Integration Test Suite:**
```bash
source .venv/bin/activate
python clients/integration_test.py
```

**Jupyter Notebook:**
```bash
source .venv/bin/activate
jupyter notebook clients/client.ipynb
```

### Checking Port Usage

```bash
# Check if port is in use
lsof -i :8000
lsof -i :8001

# Kill process if needed
kill -9 <PID>
```

## Key Architecture Patterns

### MCP Transport Types

This project demonstrates both MCP transport protocols:

1. **stdio (Standard I/O)**
   - Used by: `math_server.py`
   - Communication: stdin/stdout pipes
   - Use case: Process-to-process communication
   - Started by: Client spawns server process

2. **streamable-http**
   - Used by: `weather_server.py`, `langchain_tools_server.py`
   - Communication: HTTP endpoints
   - Use case: Network-accessible services
   - Started by: Server runs independently, client connects via HTTP

See [docs/TRANSPORT_COMPARISON.md](docs/TRANSPORT_COMPARISON.md) for detailed comparison.

### Multi-Server Architecture

The `MultiServerMCPClient` pattern enables simultaneous connections to heterogeneous MCP servers:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "langchain_math": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    },
    "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
    "math": {
        "command": "python",
        "args": ["servers/math_server.py"],
        "transport": "stdio",
    }
})

# Get tools from all servers
tools = await client.get_tools()
```

### LangChain ↔ MCP Tool Conversion

The `langchain_tools_server.py` demonstrates converting LangChain tools to MCP format:

```python
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    return result

fastmcp_tool = to_fastmcp(my_tool)
mcp = FastMCP("Server Name", tools=[fastmcp_tool])
mcp.run(transport="streamable-http")
```

## Import Patterns

**Display utilities (from clients directory):**
```python
# When running from project root or in notebooks/scripts in clients/
from display_utils import display_agent_response, get_final_answer, print_tools_summary
```

**Absolute imports (when display_utils is not in same directory):**
```python
import sys
sys.path.append('clients')
from display_utils import display_agent_response
```

**Server components (for testing):**
```python
# Import from servers directory
from servers.math_server import add, multiply
from servers.langchain_tools_server import add, multiply
```

## Display Utilities Usage

The `display_utils` module provides three key functions for formatting agent responses:

### display_agent_response()
```python
# Full trace with token usage
display_agent_response(response, show_full_trace=True, show_token_usage=True)

# Minimal output (final answer only)
display_agent_response(response, show_full_trace=False)

# Return final answer programmatically
answer = display_agent_response(response, return_final_answer=True)
```

### get_final_answer()
```python
# Extract just the final answer without printing
answer = get_final_answer(response)
```

### print_tools_summary()
```python
# Display formatted tool inventory
tools = await client.get_tools()
print_tools_summary(tools)
```

## Testing Patterns

The [clients/integration_test.py](clients/integration_test.py) demonstrates comprehensive testing patterns:

1. **Multi-step reasoning**: Tests agent's ability to chain tool calls
2. **Cross-server invocation**: Validates multi-server architecture
3. **Display modes**: Tests all output formatting options
4. **Programmatic extraction**: Shows integration into larger applications

Each test case includes detailed docstrings explaining what is tested, expected behavior, and educational value.

## Common Issues

### RuntimeError: Already running asyncio
**Cause:** Attempting to run `mcp.run()` inside Jupyter notebook

**Solution:** MCP servers must run in separate terminals. Use client code in notebooks to connect to running servers.

### Connection closed / Connection refused
**Cause:** Server not running or incorrect port

**Solution:**
1. Verify server is running in separate terminal
2. Check correct port number (8000 for weather, 8001 for langchain_tools)
3. Review server startup logs for errors

### Import Error
**Cause:** Package not installed

**Solution:** Run `uv pip install -e .` from project root

## Key Educational Resources

**For learning MCP concepts:**
- [docs/TRANSPORT_COMPARISON.md](docs/TRANSPORT_COMPARISON.md) - When to use stdio vs streamable-http
- [clients/integration_test.py](clients/integration_test.py) - Heavily documented test cases showing MCP patterns
- [clients/client.ipynb](clients/client.ipynb) - Interactive learning environment

**Note:** Other docs in `docs/` may be project maintenance artifacts not directly related to MCP learning.

## MCP Server Registry

The [.mcp.json](.mcp.json) file configures MCP servers for external MCP clients (e.g., Claude Desktop). It includes:
- `mcp-server-time` - Time utilities
- `sequential-thinking` - Chain-of-thought reasoning
- `Context7` - Documentation lookup
- `ai-docs-server` - Curated docs (LangChain, LangGraph, MCP, Anthropic)
- `ai-docs-server-full` - Full documentation mirrors

## Development Workflow

1. **Activate environment**: `source .venv/bin/activate`
2. **Start required servers**: Run weather and langchain_tools servers in separate terminals
3. **Run client code**: Either Jupyter notebook or integration test
4. **Verify results**: Check agent traces and final answers

For production use cases, consider adding tests in the `tests/` directory following pytest conventions.

## Dependencies

Key dependencies (see [pyproject.toml](pyproject.toml)):
- `langchain==0.3.19` - Core LangChain framework
- `langchain-mcp-adapters>=0.1.11` - MCP integration
- `langchain-openai==0.3.7` - OpenAI model support
- `langgraph==0.6.7` - Agent orchestration framework
- `mcp[cli]>=1.6.0` - Model Context Protocol implementation
- `python-dotenv>=1.1.0` - Environment variable management

All dependencies managed via `uv` package manager.
