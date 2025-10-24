# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an **educational demonstration** of integrating multiple Model Context Protocol (MCP) servers with LangChain agents. The project shows how to orchestrate tools and capabilities from heterogeneous services (Python, Node.js, different transports) into a unified agent framework.

**Key Problem Solved**: Traditional AI agent frameworks struggle with integrating tools from diverse sources. This project demonstrates a clean, protocol-based approach where tools can be exposed via MCP servers and consumed uniformly by LangChain agents, regardless of the underlying transport.

## Python Environment

### Setup

```bash
# Create virtual environment (Python 3.13)
uv venv --python 3.13
source .venv/bin/activate  # Linux/WSL/Mac

# Install dependencies
uv pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Environment Variables

Required:
- `OPENAI_API_KEY` - For LLM reasoning (GPT-4.1)

Optional:
- `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, `LANGSMITH_PROJECT` - For LangSmith tracing
- `CALCOM_API_KEY` - For Context7 calendar integration

## Common Development Commands

### Running MCP Servers

```bash
# Weather Server (HTTP, port 8000)
python servers/weather_server.py

# Weather Server (custom port)
python servers/weather_server.py --port 8080 --host 0.0.0.0

# LangChain Tools Server (HTTP, port 8001)
python servers/wrap_langchain_tools_server.py

# LangChain Tools Server (custom port)
python servers/wrap_langchain_tools_server.py --port 8002

# Math Server (stdio) - run via client integration
# See clients/integration_test_mcp_json.py

# Example Low-Level Server (HTTP, port 3000)
cd examples/servers/streamable-http-stateless/
uv run mcp-simple-streamablehttp-stateless --port 3000
```

### Running Clients

```bash
# Integration Test (requires servers running)
# Terminal 1: python servers/weather_server.py
# Terminal 2: python servers/wrap_langchain_tools_server.py
# Terminal 3:
python clients/integration_test.py

# MCP JSON Test (spawns servers as subprocesses)
python clients/integration_test_mcp_json.py

# Jupyter Notebook Client
jupyter notebook clients/langchain_mcp_adapter_client.ipynb
```

### Troubleshooting Servers

```bash
# Check if server is running
curl http://localhost:8000/mcp  # For HTTP servers
lsof -i :8000  # Check port usage

# Kill server on port
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Test server manually
python servers/weather_server.py  # Should show "Starting server..."
```

## Architecture Overview

### Four-Layer Architecture

1. **Client Layer** (Blue)
   - Integration Test Client (`clients/integration_test.py`)
   - LangChain Agent (ReAct pattern)
   - MultiServerMCPClient (manages connections to multiple servers)
   - Display Utils (`clients/display_utils.py`)

2. **Custom MCP Server Layer** (Green)
   - Weather Server (Port 8000) - FastMCP HTTP server
   - LangChain Tools Server (Port 8001) - Converts LangChain tools to MCP format
   - Math Server (stdio) - Simple stdio transport
   - Example Server (Port 3000) - Low-level MCP implementation

3. **External MCP Services Layer** (Orange)
   - Time Server (via uvx)
   - Sequential Thinking (via npx)
   - Context7 Calendar (via npx)
   - AI Docs Server (via uvx)

4. **External APIs Layer** (Red)
   - OpenAI API (GPT-4.1)
   - Cal.com API
   - llms.txt Documentation sources

### Transport Protocols

The system supports multiple transports through a unified interface:

- **stdio** - Subprocess-based, fastest for local tools
- **streamable-http** - HTTP POST + Server-Sent Events, best for web services
- **SSE** - Server-Sent Events only
- **WebSocket** - Bidirectional streaming (optional)

### Key Design Patterns

1. **Adapter Pattern** - Bidirectional conversion between LangChain and MCP formats
   - LangChain tools → MCP: `to_fastmcp()` from `langchain_mcp_adapters.tools`
   - MCP tools → LangChain: `MultiServerMCPClient.get_tools()` returns `BaseTool` instances

2. **Factory Pattern** - Transport selection via configuration in `MultiServerMCPClient`

3. **Strategy Pattern** - Display modes (full trace, minimal, programmatic)
   - See `clients/display_utils.py`

## Repository Structure

```
.
├── servers/                    # MCP server implementations
│   ├── weather_server.py      # FastMCP HTTP server (port 8000)
│   ├── wrap_langchain_tools_server.py  # LangChain → MCP adapter (port 8001)
│   └── math_server.py         # Stdio server
├── clients/                   # Client implementations and utilities
│   ├── integration_test.py    # Multi-server HTTP integration test
│   ├── integration_test_mcp_json.py  # **Main demo** - Stdio transport (112 lines)
│   ├── display_utils.py       # Response formatting utilities
│   └── langchain_mcp_adapter_client.ipynb  # Interactive examples
├── examples/                  # Additional examples
│   └── servers/streamable-http-stateless/  # Low-level server example
├── architecture/              # Generated architecture documentation
├── storytelling/              # Story generation templates and outputs
│   ├── templates/             # Template files for documentation generation
│   └── output/                # Generated documentation outputs
├── docs/                      # Additional documentation
│   ├── LANGGRAPH_MIGRATION_V1.md  # Migration guide from LangGraph to LangChain v1
│   ├── TRANSPORT_COMPARISON.md    # Comparison of MCP transport protocols
│   └── integration_test_mcp_json.md  # Detailed output from main demo
├── .mcp.json                  # External MCP server configuration
├── .env.example               # Environment variable template
├── pyproject.toml             # Project dependencies
└── README.md                  # Project documentation
```

## Key Implementation Patterns

### Creating an MCP Server (FastMCP)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ServerName")

@mcp.tool()
async def my_tool(param: str) -> str:
    """Tool description for LLM"""
    return f"Result: {param}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    mcp.run(transport="streamable-http", host=args.host, port=args.port)
```

### Converting LangChain Tools to MCP

```python
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp

@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Convert to FastMCP tool
fastmcp_add = to_fastmcp(add)

# Use in FastMCP server
mcp = FastMCP("Math")
mcp.add_tool(fastmcp_add)
```

### Client Integration Pattern

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# Configure multiple servers
client = MultiServerMCPClient({
    "weather": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http"
    },
    "math": {
        "command": "python",
        "args": ["servers/math_server.py"],
        "transport": "stdio"
    }
})

# Discover tools from all servers
tools = await client.get_tools()

# Create agent with aggregated tools
agent = create_agent("openai:gpt-4.1", tools)

# Execute query
response = await agent.ainvoke({"messages": "What's 5 + 3?"})
```

### Display Response Pattern

```python
from clients.display_utils import display_agent_response, get_final_answer

# Development/Debugging: Full trace with token usage
display_agent_response(response, show_full_trace=True, show_token_usage=True)

# Production: Minimal display (final answer only)
display_agent_response(response, show_full_trace=False)

# Automated Pipelines: Programmatic extraction
answer = get_final_answer(response)
if "8" in answer:
    proceed_with_next_step()
```

### MCP Server Subprocess Spawning Pattern

The main demo (`clients/integration_test_mcp_json.py`) shows how to spawn MCP servers as subprocesses using hardcoded configuration:

```python
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

def hardcoded_mcp_config():
    """Hard-coded MCP server definitions for subprocess spawning."""
    return {
        "mcp-server-time": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=America/Los_Angeles"],
            "env": {},
        },
        "sequential-thinking": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
            "env": {},
        },
        "Context7": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"],
            "env": {"CALCOM_API_KEY": os.environ.get("CALCOM_API_KEY", "")},
        },
    }

async def main():
    # Client spawns servers as subprocesses automatically
    client = MultiServerMCPClient(hardcoded_mcp_config())
    tools = await client.get_tools()
    agent = create_agent("openai:gpt-4.1", tools)
    # ... use agent
```

**Key Points:**
- `MultiServerMCPClient` auto-spawns stdio servers as subprocesses
- Environment variables can be passed via `env` dict
- Mix stdio and HTTP transports in same config
- See `clients/integration_test_mcp_json.py` for complete example

## MCP Server Configuration

External MCP servers are configured in `.mcp.json`:

- **mcp-server-time** - Timezone operations (uvx)
- **sequential-thinking** - Advanced reasoning (npx)
- **Context7** - Calendar integration with Cal.com (npx)
- **ai-docs-server** - Documentation fetching (uvx) - MCP Protocol, FastMCP, LangChain, LangGraph, Anthropic
- **ai-docs-server-full** - Full documentation versions (uvx)

## Development Best Practices

### Server Development

1. **FastMCP for Simple Tools** - Use decorator-based approach for rapid development
2. **Low-Level Server for Control** - Use `Server` class for stateless operation or custom middleware
3. **CLI Arguments** - Accept `--port` and `--host` for flexibility
4. **Environment Loading** - Use `python-dotenv` to load `.env` files
5. **Async-First** - All I/O operations should use `async/await`

### Client Development

1. **Tool Discovery** - Always call `client.get_tools()` to discover available tools
2. **Session Management** - Use `async with client.session()` for persistent connections
3. **Error Handling** - Catch `ToolException`, protocol errors, and transport errors
4. **Display Modes** - Choose appropriate display mode for context (debug, production, automated)

### Agent Development

1. **Single Responsibility** - Each agent should have one clear purpose
2. **Explicit Tools** - Only include tools the agent needs
3. **File Writing Mandate** - Agents MUST use Write tool, not describe output
4. **Clear Prompts** - Include examples and edge cases in system prompts

## Integration with Cursor Rules

This repository includes Cursor rules in `.cursor/rules/`:

- **mcp-langgraph-context.mdc** - MCP and LangGraph integration patterns
- **llm-stack-alignment.mdc** - LLM stack component mapping
- **repo-storytelling-suite.mdc** - Repository storytelling and documentation generation

These rules guide context-aware assistance for MCP server development, LangGraph orchestration, and architecture documentation.

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python servers/weather_server.py --port 8080
```

### Connection Closed Error

- Ensure server is running before starting client
- Check port number matches between server and client
- Verify server started successfully (no errors in terminal)

### Agent Not Writing Files

Ensure agent prompt includes:
```
IMPORTANT: When asked to write to a file, ALWAYS use the Write tool
to create the actual file. Do not just describe what you would write.
```

## Documentation Structure

- `README.md` - Project overview, quick start, troubleshooting
- `architecture/README.md` - Comprehensive architecture documentation (generated)
- `docs/LANGGRAPH_MIGRATION_V1.md` - Migration guide from LangGraph to LangChain v1
- `docs/TRANSPORT_COMPARISON.md` - Comparison of MCP transport protocols
- `docs/integration_test_mcp_json.md` - Detailed output from main demo with LangSmith trace
- `storytelling/` - Templates and generated documentation for presentations
- This file - Development guidance for Claude Code

## Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | >=3.13 | Primary language |
| MCP SDK | >=1.6.0 | Model Context Protocol implementation |
| LangChain | >=1.0.0 | Agent orchestration framework |
| LangChain MCP Adapters | >=0.1.11 | Bridge between MCP and LangChain |
| LangGraph | >=1.0.0 | Graph-based agent workflows |
| OpenAI | >=1.72.0 | LLM provider (GPT-4.1) |
| Claude Agent SDK | >=0.1.4 | Multi-agent orchestration utilities |
| FastMCP | (via MCP SDK) | High-level server framework |
| Uvicorn | (transitive) | ASGI server runtime |

## Project Metadata

- **Project Name**: langchain-mcp-multiserver-demo
- **Version**: 0.1.0
- **Purpose**: Educational demonstration for AIE Cohort 8
- **Python Version**: >=3.13
- **License**: (Same as parent project)

## Notes

- `ra_*` directories are excluded from git (see `.gitignore`) and contain the Repository Analyzer Framework
- Generated architecture documentation in `architecture/` may reference internal implementation details from the `langchain-mcp-adapters` library (e.g., `sessions.py` is part of that library, not this repo)