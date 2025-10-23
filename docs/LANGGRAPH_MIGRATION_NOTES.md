# LangGraph v1 Migration Notes
## Presentation Demo Guide

### The Story Arc

This demo showcases the value of simplicity and the power of the `integration_test.py` script while demonstrating real-world engineering: handling breaking changes in production dependencies.

### Demo Flow

1. **Startup MCP Servers** (1 min)
   - Review [README.md](./README.md) for quick start commands
   - Bootstrap both MCP servers in separate terminals

   **Terminal 1 - Startup Weather MCP Server (port 8000):**
   ```bash
   cd /home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp
   source .venv/bin/activate
   python servers/weather_server.py --port 8000
   ```

   **Terminal 2 - Startup LangChain Math Tools MCP Server (port 8001):**
   ```bash
   cd /home/donbr/don-aie-cohort8/aie8-s13-langchain-mcp
   source .venv/bin/activate
   python servers/langchain_tools_server.py --port 8001
   ```

   NOTE:  the third option from the README.md is the cool kid on the block, but out of scope for this walkthrough.

2. [**Run the `clients/integration_test.py` Script**](../clients/integration_test.py) (1 min)
   - Execute `python clients/integration_test.py`
   - Show multi-server orchestration in action
   - Point out the deprecation warning (if present on older branch)
   - Leverages the [`clients/display_utils.py`](../clients/display_utils.py) script to format output

3. **Live Migration** (2 min) - **The Pivot**
   - Show the deprecation message details
   - Perform 3-step fix live:
     - Update dependencies
     - Change import
     - Update function call
   - Re-run to show clean execution

4. **Victory Lap** (1 min)
   - Discuss what we learned
   - Highlight the value of clear and concise output and error messages
   - Show how MCP servers continued working throughout

---

## Technical Changes Made

### 1. Dependency Updates (pyproject.toml)

**Before (LangGraph v0.6.7):**
```toml
dependencies = [
    "langchain==0.3.19",
    "langgraph==0.6.7",
    "langchain-openai>=0.3.7",
    # ... other deps
]
```

**After (LangGraph v1.0+):**
```toml
dependencies = [
    "langchain==0.3.19",
    "langgraph==0.6.7",
    "langchain-openai>=0.3.7",
    # ... other deps
]
```

Command used:
```bash
uv add "langchain>=0.3.19" "langgraph>=0.6.7" "langchain-openai>=0.3.7"
```

### 2. Import Statement (integration_test.py line 57)

**Before:**
```python
from langgraph.prebuilt import create_react_agent
```

**After:**
```python
from langchain.agents import create_agent
```

**Why:** LangGraph v1 consolidated agent creation utilities into the broader `langchain.agents` namespace.

### 3. Function Call (integration_test.py line 109)

**Before:**
```python
agent = create_react_agent("openai:gpt-4.1", tools)
```

**After:**
```python
agent = create_agent("openai:gpt-4.1", tools)
```

**Why:** Function renamed from `create_react_agent` to `create_agent` for simplicity.

---

## Key Presentation Talking Points

### Why This Matters

1. **Real-World Engineering**
   - Breaking changes happen in production dependencies
   - Clear deprecation messages make migrations straightforward
   - Well-structured code makes updates simple (2 lines changed)

2. **MCP Architecture Resilience**
   - Servers continued running during migration
   - No changes needed to server code
   - Clean separation of concerns

3. **Educational Value**
   - Script demonstrates multi-server orchestration
   - Clear output formatting shows agent reasoning
   - Easy to extend with new servers

### Demo Advantages

- **Simplicity**: Bootstrap servers from README, run one script
- **Visibility**: See agent + multi-server interaction in real-time
- **Practical**: Handle real deprecation warnings like you would in production
- **Clean**: No warnings after migration, everything works

### What the Script Demonstrates

1. **Multi-Server Connection Pooling**
   - Weather server (port 8000)
   - LangChain tools server (port 8001)
   - Simultaneous tool discovery

2. **Agent Orchestration Patterns**
   - Multi-step reasoning (add then multiply)
   - Cross-server tool invocation
   - Sequential instruction following

3. **Output Formatting Options**
   - Full trace with token metrics
   - Minimal display (final answer only)
   - Programmatic extraction

4. **Error Handling**
   - Graceful degradation
   - Clear error messages
   - State management between tools

---

## Files Affected

### Modified
- `pyproject.toml` - Dependency versions
- `clients/integration_test.py` - Import and function call

### Unchanged
- `servers/weather_server.py` - No changes needed
- `servers/langchain_tools_server.py` - No changes needed
- `clients/display_utils.py` - No changes needed
- `clients/client.ipynb` - Intentionally not updated for this demo

---

## Testing Checklist

- [x] Both servers running (ports 8000, 8001)
- [x] Dependencies updated (`uv pip install -e .`)
- [x] Import statement changed
- [x] Function call updated
- [x] All 4 test cases pass
- [x] No deprecation warnings
- [x] Token usage metrics displayed

---

## Related Resources

- **GitHub Commit**: https://github.com/don-aie-cohort8/langchain-mcp-multiserver-demo/commit/1267d535f526bcf7cdd8bf61846b1f12adcfc1f2
- **LangGraph v1 Migration Guide**: https://langchain-ai.github.io/langgraph/how-tos/migrate-to-v1/
- **Branch**: `feature/langgraph-v1-migration`
