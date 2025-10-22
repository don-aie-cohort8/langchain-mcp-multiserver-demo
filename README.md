# LangChain MCP Multi-Server Integration Guide

> NOTE: this is a rework of the great examples found in the README.md of the great [LangChain MCP Adapter](https://github.com/langchain-ai/langchain-mcp-adapters) repository  

This guide demonstrates how to use the LangChain MCP adapters with multiple custom servers,
including configuration, tool discovery, and agent orchestration.

**Project:** `aie8-s13-langchain-mcp`
**Focus:** Educational demonstration of MCP integration patterns

## Quick Start

### 1. Start the Servers

In separate terminals, start the MCP servers:

**Terminal 1 - Weather Server (port 8000):**
```bash
cd /home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp
source .venv/bin/activate
python servers/weather_server.py
```

**Terminal 2 - LangChain Tools Server (port 8001):**
```bash
cd /home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp
source .venv/bin/activate
python servers/langchain_tools_server.py --port 8001
```

**Terminal 3 - Streamable HTTP (port 3000):**
```bash
cd examples/servers/streamable-http-stateless/
uv run mcp-simple-streamablehttp-stateless --port 3000
```


You should see output like:
```
Starting LangChain MCP Server on 127.0.0.1:8001
Available tools: add, multiply
INFO:     Started server process...
```

### 2. Use the Client (in Jupyter Notebook)

Open [`client.ipynb`](clients/client.ipynb)

## Server Configuration

### langchain_tools_server.py

This server converts LangChain tools to MCP format using FastMCP.

**Features:**
- Accepts `--port` and `--host` command-line arguments
- Runs on port 8001 by default
- Provides `add` and `multiply` tools
- Automatically loads environment variables from `.env` file (using `python-dotenv`)

**Usage:**
```bash
# Default (127.0.0.1:8001)
python servers/langchain_tools_server.py

# Custom port
python servers/langchain_tools_server.py --port 8002

# Custom host and port
python servers/langchain_tools_server.py --host 0.0.0.0 --port 9000
```

### weather_server.py

Simple weather MCP server using FastMCP.

**Features:**
- Accepts `--port` and `--host` command-line arguments
- Runs on port 8000 by default
- Provides `get_weather` tool
- Returns mock weather data for requested location

**Usage:**
```bash
# Default (127.0.0.1:8000)
python servers/weather_server.py

# Custom port
python servers/weather_server.py --port 8080

# Custom host and port
python servers/weather_server.py --host 0.0.0.0 --port 9000
```

## Display Utilities

The `display_utils.py` module provides functions for formatting agent responses.

### display_agent_response()

Display formatted agent response with message trace.

```python
from display_utils import display_agent_response

# Full trace with token usage
display_agent_response(response, show_full_trace=True, show_token_usage=True)

# Just the final answer
display_agent_response(response, show_full_trace=False)

# Get answer as return value
answer = display_agent_response(response, return_final_answer=True)
```

### get_final_answer()

Extract just the final answer without printing.

```python
from display_utils import get_final_answer

answer = get_final_answer(response)
print(f"The answer is: {answer}")
```

### print_tools_summary()

Display a summary of available tools.

```python
from display_utils import print_tools_summary

tools = await client.get_tools()
print_tools_summary(tools)
```

Output:
```
======================================================================
AVAILABLE TOOLS (4 total)
======================================================================

01. add
    └─ Add two numbers
02. multiply
    └─ Multiply two numbers
03. get_weather
    └─ Get weather for location.

======================================================================
```

## Examples

### Example 1: Math Calculation

```python
response = await agent.ainvoke({"messages": "what is (15 + 27) * 3?"})
display_agent_response(response)
```

Output:
```
======================================================================
AGENT RESPONSE TRACE
======================================================================

01. HumanMessage: what is (15 + 27) * 3?
02. AIMessage → 🔧 tool_call(s): add
03. ToolMessage [add]: ✓ 42
04. AIMessage → 🔧 tool_call(s): multiply
05. ToolMessage [multiply]: ✓ 126
06. AIMessage: (15 + 27) * 3 = 42 * 3 = 126.

======================================================================
```

### Example 2: Weather Query

```python
response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
display_agent_response(response, show_full_trace=False)
```

Output:
```
💡 Final Answer: The weather in New York City is always sunny!
```

### Example 3: Programmatic Answer Extraction

```python
response = await agent.ainvoke({"messages": "multiply 7 and 9"})
answer = get_final_answer(response)

if "63" in answer:
    print("Correct!")
```

## Troubleshooting

### Port Already in Use

**Error:**
```
ERROR: [Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): address already in use
```

**Solution:**
- Check if a server is already running: `lsof -i :8000`
- Kill the process: `kill -9 <PID>`
- Or use a different port: `python servers/langchain_tools_server.py --port 8002`

### Connection Closed Error

**Error:**
```
mcp.shared.exceptions.McpError: Connection closed
```

**Solution:**
- Ensure the server is running before starting the client
- Check that you're using the correct port number
- Verify the server started successfully (no errors in the terminal)

### RuntimeError: Already running asyncio

**Error:**
```
RuntimeError: Already running asyncio in this thread
```

**Solution:**
- Don't run `mcp.run()` inside a Jupyter notebook
- MCP servers must run in separate terminals/processes
- Use the client code in the notebook to connect to running servers

## Architecture

```
┌─────────────────────┐
│  Jupyter Notebook   │
│  or Python Script   │
│                     │
│  - Client Code      │
│  - Display Utils    │
└──────────┬──────────┘
           │
           │ HTTP (streamable-http)
           │
    ┌──────┴───────┐
    │              │
    ▼              ▼
┌─────────┐    ┌──────────────────────┐
│ Weather │    │ LangChain Tools      │
│ Server  │    │ Server               │
│         │    │                      │
│ Port    │    │ Port 8001            │
│ 8000    │    │ - add()              │
│         │    │ - multiply()         │
└─────────┘    └──────────────────────┘
```

## Files

- `langchain_tools_server.py` - Converts LangChain tools to MCP format
- `weather_server.py` - Example weather MCP server
- `math_server.py` - Example math MCP server (stdio transport)
- `display_utils.py` - Formatting utilities for agent responses
- `integration_test.py` - Complete working example
- `client.ipynb` - Jupyter notebook with various examples

## Next Steps

1. Add more tools to `langchain_tools_server.py`
2. Create custom display formats in `display_utils.py`
3. Build your own MCP servers for different domains
4. Integrate with LangGraph for complex workflows

## References

- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
