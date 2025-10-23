# MCP Transport Comparison: stdio vs streamable-http

## Original Example (stdio transport)

```python
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP


@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


fastmcp_tool = to_fastmcp(add)

mcp = FastMCP("Math", tools=[fastmcp_tool])
mcp.run(transport="stdio")  # ← Uses stdin/stdout for communication
```

### How to Use (stdio)

**Server side:**
- The client **automatically spawns** the server as a subprocess
- Communication happens via stdin/stdout pipes
- **No manual server startup needed**

**Client side:**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "math": {
        "command": "python",
        "args": ["/path/to/server.py"],  # Client starts this automatically
        "transport": "stdio",
    }
})

tools = await client.get_tools()
```

### Limitations of stdio
- ❌ Only one client connection at a time
- ❌ Cannot run in Jupyter notebook (asyncio conflict)
- ❌ Server dies when client disconnects
- ❌ No network access (same machine only)
- ✅ Good for: CLI tools, single-user applications

---

## Our Enhanced Version (streamable-http transport)

```python
import argparse
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP


@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangChain MCP Server")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()

    print(f"Starting LangChain MCP Server on {args.host}:{args.port}")
    print("Available tools: add, multiply")

    fastmcp_add = to_fastmcp(add)
    fastmcp_multiply = to_fastmcp(multiply)

    # Pass host and port directly to FastMCP constructor
    mcp = FastMCP(
        "LangChain Math Server",
        tools=[fastmcp_add, fastmcp_multiply],
        host=args.host,  # ← Configurable host
        port=args.port   # ← Configurable port
    )

    mcp.run(transport="streamable-http")  # ← Uses HTTP for communication
```

### How to Use (streamable-http)

**Server side (manual startup required):**
```bash
# Terminal 1
python servers/wrap_langchain_tools_server.py --port 8001
```

**Client side:**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "langchain_math": {
        "url": "http://localhost:8001/mcp",  # ← Connect to running server
        "transport": "streamable_http",
    }
})

tools = await client.get_tools()
```

### Advantages of streamable-http
- ✅ Multiple concurrent client connections
- ✅ Works in Jupyter notebooks
- ✅ Server runs independently
- ✅ Network accessible (can connect from other machines)
- ✅ Can configure host/port
- ✅ Better for development/production

---

## Key Differences

| Feature | stdio | streamable-http |
|---------|-------|-----------------|
| **Server startup** | Automatic (by client) | Manual (separate terminal) |
| **Communication** | stdin/stdout pipes | HTTP requests |
| **Multiple clients** | ❌ No | ✅ Yes |
| **Network access** | ❌ No | ✅ Yes |
| **Jupyter compatible** | ❌ No | ✅ Yes |
| **Port configuration** | N/A | ✅ `--port` flag |
| **Use case** | CLI tools | Web services, development |

---

## Why We Made the Changes

### Problem with Original (stdio)
1. **Port conflict impossible to fix** - stdio doesn't use ports
2. **Can't run multiple servers** - each needs dedicated subprocess
3. **Jupyter incompatible** - `anyio.run()` conflicts with notebook event loop
4. **Manual server management** - harder to debug and monitor

### Our Solution (streamable-http)
1. ✅ **Configurable ports** - `--port 8001` flag
2. ✅ **Independent servers** - weather on 8000, math on 8001
3. ✅ **Jupyter compatible** - servers run separately, notebook connects
4. ✅ **Easy debugging** - see server logs in terminal

---

## When to Use Each

### Use stdio when:
- Building CLI applications
- Single-user desktop tools
- Want automatic subprocess management
- Don't need network access
- Example: VS Code extensions, CLI assistants

### Use streamable-http when:
- Building web services
- Need multiple clients
- Working in Jupyter notebooks
- Want to inspect/debug server independently
- Need network access
- **Example: Your learning/development environment** ✅

---

## Converting from stdio to streamable-http

**Step 1:** Add command-line arguments for host/port
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()
```

**Step 2:** Pass host/port to FastMCP
```python
mcp = FastMCP(
    "Server Name",
    tools=[...],
    host=args.host,
    port=args.port
)
```

**Step 3:** Change transport
```python
mcp.run(transport="streamable-http")  # Changed from "stdio"
```

**Step 4:** Update client configuration
```python
# Before (stdio):
client = MultiServerMCPClient({
    "server": {
        "command": "python",
        "args": ["/path/to/server.py"],
        "transport": "stdio",
    }
})

# After (streamable-http):
client = MultiServerMCPClient({
    "server": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    }
})
```

---

## Summary

- **Original README example**: Simple stdio server for basic use cases
- **Our enhanced version**: Production-ready HTTP server with configuration
- **Why we changed it**: Better for development, debugging, and Jupyter notebooks
- **Trade-off**: Manual server startup vs automatic subprocess management

Your enhanced version is actually **more robust and flexible** than the original example! 🎉
