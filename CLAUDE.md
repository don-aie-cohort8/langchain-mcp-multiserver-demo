# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Educational repository demonstrating Model Context Protocol (MCP) integration with LangChain and LangGraph. Created for AI Engineering Bootcamp Cohort 8, Session 13.

**Core Concepts:**
- Multi-server MCP architecture (connecting to multiple MCP servers simultaneously)
- Transport types (stdio vs streamable-http)
- LangChain → MCP tool conversion
- LangGraph agent orchestration with MCP tools

## Repository Structure

```
├── servers/                    # MCP server implementations
│   ├── langchain_tools_server.py  # LangChain tools → MCP (port 8001)
│   ├── weather_server.py          # Weather API mock (port 8000)
│   └── math_server.py             # stdio transport example
├── clients/                    # Client code and utilities
│   ├── integration_test.py        # Automated test suite
│   ├── client.ipynb               # Interactive examples
│   └── display_utils.py           # Response formatting utilities
├── docs/
│   └── TRANSPORT_COMPARISON.md    # stdio vs streamable-http guide
├── storytelling/               # Documentation generation
│   ├── templates/                 # Output templates
│   └── output/                    # Generated docs
├── .cursor/                    # Cursor AI rules/prompts
│   ├── rules/                     # Documentation generation rules
│   └── prompts/                   # Quick-start commands
├── .mcp.json                   # External MCP server registry
├── pyproject.toml              # Dependencies (uv format)
└── README.md                   # Quick start guide
```

**Key Teaching Files:**
- `servers/langchain_tools_server.py` — Demonstrates LangChain → MCP tool conversion
- `clients/integration_test.py` — Complete working example with all display modes
- `clients/display_utils.py` — Reusable response formatting (import this in your code)
- `docs/TRANSPORT_COMPARISON.md` — When to use stdio vs streamable-http

## Environment Setup

```bash
# Create and activate virtual environment (Python 3.13)
uv venv --python 3.13
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Create .env file with required variables
cp .env.example .env
# Edit .env and add OPENAI_API_KEY
```

**Required Environment Variables:**
- `OPENAI_API_KEY` — Required for LLM operations
- `LANGCHAIN_API_KEY` — Optional, for LangSmith tracing
- `LANGSMITH_TRACING` — Optional, set to "true" for tracing

## Common Development Commands

### Starting MCP Servers

**IMPORTANT:** MCP servers must run in separate terminal windows BEFORE starting clients.

```bash
# Terminal 1 - Weather Server (port 8000)
source .venv/bin/activate
python servers/weather_server.py

# Terminal 2 - LangChain Tools Server (port 8001)
source .venv/bin/activate
python servers/langchain_tools_server.py --port 8001

# Custom port/host options
python servers/langchain_tools_server.py --port 8002 --host 0.0.0.0
```

### Running Client Examples

```bash
# Integration test suite (requires servers running)
source .venv/bin/activate
python clients/integration_test.py

# Jupyter notebook
source .venv/bin/activate
jupyter notebook clients/client.ipynb
```

### Port Management

```bash
# Check if port is in use
lsof -i :8000
lsof -i :8001

# Kill process on port
kill -9 <PID>
```

## LLM Application Stack Layers

This repository demonstrates components across multiple LLM application stack layers:

| **Layer** | **Components in This Project** |
|-----------|-------------------------------|
| **Data Pipelines** | N/A (mock data in weather_server.py) |
| **Embeddings** | N/A (focus is on tool orchestration) |
| **Vector DB** | N/A (not used in this demo) |
| **Orchestrator** | LangGraph (create_react_agent), LangChain |
| **APIs/Tools** | MCP servers (weather, math, langchain_tools), FastMCP |
| **Caches** | N/A |
| **Monitoring/Eval** | LangSmith tracing (optional), display_utils.py for response inspection |
| **Validators** | N/A (could be added to tool inputs/outputs) |
| **UI/Hosting** | Jupyter notebooks (client.ipynb), Python scripts |

**Key Focus:** This project primarily demonstrates the **Orchestrator** and **APIs/Tools** layers through MCP multi-server integration with LangGraph.

## Key Architecture Patterns

### 0. Critical: Server Lifecycle Management

**MCP servers MUST run as independent processes.** Do not attempt to start servers programmatically from client code.

**Server Startup Pattern:**
```bash
# Separate terminal for each server
python servers/weather_server.py          # Port 8000
python servers/langchain_tools_server.py  # Port 8001
```

**Client Connection Pattern:**
```python
# Client connects to running servers via HTTP
client = MultiServerMCPClient({
    "server_name": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    }
})
```

**Why This Matters:**
- Attempting `mcp.run()` in Jupyter causes `RuntimeError: Already running asyncio`
- Servers must be independently restartable without affecting clients
- Multiple clients can connect to the same server instance
- Port conflicts indicate a server is already running (not necessarily an error)

### 1. MCP Transport Types

**stdio Transport** (`math_server.py`):
- Client spawns server as subprocess
- Communication via stdin/stdout pipes
- Single client connection only
- Cannot run in Jupyter (asyncio conflict)
- Good for: CLI tools, single-user applications

**streamable-http Transport** (`weather_server.py`, `langchain_tools_server.py`):
- Server runs independently as HTTP service
- Multiple concurrent client connections
- Network-accessible
- Jupyter-compatible
- Good for: Multi-user services, distributed systems

See [docs/TRANSPORT_COMPARISON.md](docs/TRANSPORT_COMPARISON.md) for detailed comparison.

### 2. Multi-Server Client Pattern

Connect to multiple heterogeneous MCP servers simultaneously:

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
    "math": {  # stdio example
        "command": "python",
        "args": ["servers/math_server.py"],
        "transport": "stdio",
    }
})

# Get tools from all servers
tools = await client.get_tools()
```

### 3. LangChain → MCP Tool Conversion

Pattern demonstrated in `langchain_tools_server.py`:

```python
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    return result

# Convert to FastMCP format
fastmcp_tool = to_fastmcp(my_tool)

# Create and run server
mcp = FastMCP("Server Name", tools=[fastmcp_tool])
mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)
```

**When to Create New Servers:**
- **Create new server:** When you need persistent, reusable tools accessible to multiple clients
- **Add to existing server:** When extending capabilities of current service domain
- **Direct LangChain tools:** When tools are client-specific or single-use (no server needed)

**Port Assignment Convention:**
- `8000` — weather_server.py
- `8001` — langchain_tools_server.py
- `8002+` — Your custom servers

### 4. LangGraph Agent Creation

Pattern for creating ReAct agents with MCP tools:

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Get tools from MCP client
tools = await client.get_tools()

# Create LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create agent graph
agent = create_react_agent(llm, tools)

# Invoke agent
response = await agent.ainvoke({"messages": "your query here"})
```

**Key Points:**
- Tools come from `client.get_tools()` (aggregates all connected MCP servers)
- Agent automatically selects and chains tools based on query
- Response includes full message trace (human → AI → tool → AI → ...)
- Use display utilities to format the response

### 5. Display Utilities (clients/display_utils.py)

Three key functions for formatting agent responses:

```python
from display_utils import display_agent_response, get_final_answer, print_tools_summary

# Full trace with token usage
display_agent_response(response, show_full_trace=True, show_token_usage=True)

# Minimal output (final answer only)
display_agent_response(response, show_full_trace=False)

# Extract answer programmatically
answer = get_final_answer(response)

# Display tool inventory
tools = await client.get_tools()
print_tools_summary(tools)
```

## Import Patterns

```python
# When in clients/ directory or project root
from display_utils import display_agent_response, get_final_answer, print_tools_summary

# When display_utils not in path
import sys
sys.path.append('clients')
from display_utils import display_agent_response
```

## Common Issues and Solutions

### RuntimeError: Already running asyncio
**Cause:** Attempting to run `mcp.run()` inside Jupyter notebook

**Solution:** MCP servers must run in separate terminal processes. Use client code in notebooks to connect to running servers.

### Connection closed / Connection refused
**Cause:** Server not running or incorrect port

**Solution:**
1. Verify server is running in separate terminal
2. Check port numbers: 8000 (weather), 8001 (langchain_tools)
3. Review server startup logs for errors
4. Look for the startup message: `Starting LangChain MCP Server on 127.0.0.1:8001`

### Import Error: cannot import display_utils
**Cause:** Running code from wrong directory or package not installed

**Solution:**
```bash
# If in project root, run from clients/ directory
cd clients
python integration_test.py

# Or add to sys.path
import sys
sys.path.append('clients')
from display_utils import display_agent_response

# Or install package in editable mode
uv pip install -e .
```

### Address Already in Use (Port Conflict)
**Cause:** Server already running on that port (may be from previous session)

**Solution:**
```bash
# Check what's using the port
lsof -i :8001

# Kill the existing process
kill -9 <PID>

# Or use a different port
python servers/langchain_tools_server.py --port 8002
```

### OPENAI_API_KEY not found
**Cause:** Environment variable not set or .env file missing

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
echo "OPENAI_API_KEY=sk-..." >> .env

# Or export directly
export OPENAI_API_KEY=sk-...
```

## Testing Patterns

The [clients/integration_test.py](clients/integration_test.py) demonstrates:
1. Multi-step reasoning (agent chaining tool calls)
2. Cross-server invocation (tools from different MCP servers)
3. Display mode variations (verbose, minimal, programmatic)
4. Programmatic answer extraction (integration into larger applications)

Each test case includes detailed docstrings explaining expected behavior and educational value.

## MCP Server Registry (.mcp.json)

Configures MCP servers for external MCP clients (e.g., Claude Desktop):
- `mcp-server-time` — Time utilities
- `sequential-thinking` — Chain-of-thought reasoning
- `Context7` — Documentation lookup
- `ai-docs-server` — Curated docs (LangChain, LangGraph, MCP, Anthropic)
- `ai-docs-server-full` — Full documentation mirrors

## Key Dependencies

- `langchain==0.3.19` — Core LangChain framework
- `langchain-mcp-adapters>=0.1.11` — MCP integration
- `langchain-openai==0.3.7` — OpenAI model support
- `langgraph==0.6.7` — Agent orchestration
- `mcp[cli]>=1.6.0` — Model Context Protocol implementation
- `python-dotenv>=1.1.0` — Environment variable management

All dependencies managed via `uv` package manager (Python 3.13 required).

## Documentation Generation Philosophy

This repository follows a **"Build • Ship • Share"** documentation workflow using the Repository Storytelling Suite.

**Write Permissions:**
- ✅ Documentation files: `README.md`, `PROJECT_CONTEXT.md`, `ARCHITECTURE_OVERVIEW.md`, `SLIDES.md`, `VIDEO_SCRIPT.md`, `LINKEDIN_POST.md`, `LEARNING_REFLECTION.md`
- ✅ Directories: `docs/`, `storytelling/` (output and templates)
- ❌ Code changes require explicit user approval

**Documentation Workflow:**

The Storytelling Suite generates seven interconnected artifacts:
1. **Project Context** → Foundation (WHY/WHAT)
2. **Repo Overview** → Newcomer onboarding
3. **Architecture Summary** → HOW it works (with LLM stack mapping + MCP/LangGraph diagrams)
4. **Slides** → 5-minute presentation
5. **Video Script** → Narration with screen cues
6. **LinkedIn Post** → Social sharing
7. **Learning Reflection** → Meta-learning and next sprint planning

Each rule handles errors gracefully (missing templates, incomplete context) and maintains continuity across artifacts.

See **Cursor Integration** section below for detailed trigger commands.

## Development Workflow

### Standard Workflow

1. **Activate environment:** `source .venv/bin/activate`
2. **Start MCP servers** (in separate terminals):
   ```bash
   # Terminal 1
   python servers/weather_server.py

   # Terminal 2
   python servers/langchain_tools_server.py --port 8001
   ```
3. **Run client code:**
   - Interactive: `jupyter notebook clients/client.ipynb`
   - Testing: `python clients/integration_test.py`
4. **Verify output:** Use display utilities for formatted traces

### Cursor Integration

The `.cursor/` and `storytelling/` directories provide automated documentation generation using a **Repository Storytelling Suite**.

**Cursor Rules** (`.cursor/rules/`):

1. **repo-storytelling-suite.mdc** — Template-aware documentation generation workflow
   - Natural language triggers (no file paths needed)
   - Dependency-based rule chaining
   - Automatic output directory creation (`storytelling/output/`)
   - Error handling with graceful degradation

2. **llm-stack-alignment.mdc** — LLM application stack mapping
   - Maps components to layers: Data Pipelines, Embeddings, Vector DB, Orchestrator, APIs/Tools, Caches, Monitoring/Eval, Validators, UI/Hosting
   - Generates stack alignment tables in ARCHITECTURE_OVERVIEW.md
   - Validates component categorization

3. **mcp-langgraph-context.mdc** — MCP and LangGraph pattern extraction
   - Analyzes graph nodes, state definitions, and tool bindings
   - Generates Mermaid diagrams (flowchart and state)
   - Documents MCP server inventory and tool mappings
   - Extracts integration patterns and error handling strategies

**Storytelling Suite Triggers** (use in Cursor chat):

Execute in sequence for complete documentation:
1. **"Generate project context doc"** → `PROJECT_CONTEXT.md`
2. **"Generate repo overview"** → `REPO_OVERVIEW.md` (complements root README)
3. **"Generate architecture summary"** → `ARCHITECTURE_OVERVIEW.md` (includes stack mapping + MCP/LangGraph diagrams)
4. **"Generate presentation slides"** → `SLIDES.md` (7-9 slides, <5 min presentation)
5. **"Generate video script"** → `VIDEO_SCRIPT.md` (650-800 words, includes [SCREEN]/[DEMO] cues)
6. **"Generate LinkedIn post"** → `LINKEDIN_POST.md` (conversational, invites discussion)
7. **"Generate learning reflection"** → `LEARNING_REFLECTION.md` (meta-learning, next sprint TODOs)

**Tone:** Coaching, peer-friendly; favors concise bullets (~5-8 words) and short paragraphs.

All outputs automatically saved to `storytelling/output/`

**Templates** (`storytelling/templates/`):
Templates provide structure when available; if missing, rules use built-in outlines:
- `REPO_OVERVIEW_TEMPLATE.md`
- `ARCHITECTURE_OVERVIEW_TEMPLATE.md`
- `PROJECT_CONTEXT_TEMPLATE.md`
- `SLIDES_TEMPLATE.md`
- `VIDEO_SCRIPT_TEMPLATE.md`
- `LINKEDIN_POST_TEMPLATE.md`
- `LEARNING_REFLECTION_TEMPLATE.md`

**Key Features:**
- Dependency-aware: Rules execute in order, reusing earlier outputs
- Error resilient: Missing templates/outputs trigger graceful fallbacks
- Context-rich: Reads notebooks (.ipynb), scripts, configs, images for comprehensive docs
- Continuity: Maintains consistent phrasing across artifacts