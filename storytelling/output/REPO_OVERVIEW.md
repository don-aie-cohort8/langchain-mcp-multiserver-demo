# 🧭 Project Overview

> **Purpose:** A clear, friendly entry point for anyone exploring this repository.  
> Think of this as your "README for humans" — what someone new needs to understand *why* this project matters and *how* it fits.

---

## 🚀 1. What This Project Does
This repository demonstrates how to integrate multiple MCP (Model Context Protocol) servers with LangChain agents, showing both stdio and streamable-http transport patterns. It's designed for AI engineers learning to orchestrate multiple tool servers and convert LangChain tools to MCP format. The project serves as an educational foundation for understanding how AI agents can seamlessly connect to diverse external services through standardized protocols.

**Example:**  
> This repo demonstrates how to connect multiple MCP servers using LangChain's MCP adapter, showing a practical pattern for hybrid human–AI collaboration.

---

## 🧱 2. Architecture Overview
The system follows a multi-server architecture where LangChain agents orchestrate multiple MCP servers through different transport methods. Each server provides specialized tools (weather, math, custom functions) that agents can discover and use dynamically.

```
Jupyter Notebook/Client → LangChain Agent → MCP Servers (Weather, Math, LangChain Tools) → External APIs/Tools → Formatted Response
```

The architecture supports both stdio (direct process communication) and streamable-http (web-based) transport methods, enabling flexible deployment scenarios.

---

## ⚙️ 3. Tech Stack
| Layer | Component | Purpose |
|--------|------------|----------|
| LLM | `OpenAI GPT-4` | Reasoning & generation |
| Orchestration | `LangChain`, `LangGraph` | Agent flow control & tool routing |
| MCP | `FastMCP`, `LangChain MCP Adapter` | Tool integration & protocol handling |
| Transport | `stdio`, `streamable-http` | Server communication methods |
| Display | `Jupyter Notebook`, `display_utils.py` | Interactive learning & response formatting |
| Environment | `python-dotenv`, `uv` | Configuration & dependency management |

---

## 🧩 4. Key Features
- ✅ **Multi-Server Integration** — Demonstrates connecting multiple MCP servers with different transport methods
- ✅ **Tool Conversion** — Shows how to convert LangChain tools to MCP format using `langchain-mcp-adapters`
- ✅ **Interactive Learning** — Provides Jupyter notebook with step-by-step examples and debugging utilities
- ✅ **Transport Flexibility** — Supports both stdio and streamable-http transport patterns
- ✅ **Response Debugging** — Built-in utilities for tracing agent responses and tool execution

---

## 🚀 5. Quick Start
Get the project running in minutes:

```bash
# 1. Install dependencies
uv sync

# 2. Start the weather server (Terminal 1)
python servers/weather_server.py

# 3. Start the LangChain tools server (Terminal 2)  
python servers/wrap_langchain_tools_server.py --port 8001

# 4. Open the learning notebook
jupyter notebook clients/langchain_mcp_adapter_client.ipynb
```

**Preconditions:** Python 3.13+, OpenAI API key in `.env` file  
**Success verification:** You should see "Available tools: add, multiply" and "Available tools: get_weather" in the server terminals.

---

## 📊 6. Learning Outcomes
What concepts or skills does this repo teach?

- Understanding multi-server MCP connections with different transport methods
- Converting LangChain tools to MCP format using adapters
- Using streamable-http transport for web-based MCP servers
- Building agent orchestration patterns with tool discovery
- Creating debugging utilities for agent response tracing
- Designing educational materials for AI engineering concepts

---

## 🧭 7. Roadmap
| Milestone | Status | Notes |
|------------|---------|-------|
| v1: Basic Integration | ✅ Done | Multi-server MCP with stdio transport |
| v2: Streamable HTTP | ✅ Done | Web-based MCP server communication |
| v3: Tool Conversion | ✅ Done | LangChain tools to MCP format |
| v4: Educational Materials | ✅ Done | Jupyter notebook with learning path |
| v5: Production Patterns | ⏳ Planned | Authentication, error handling, deployment |
| v6: Advanced Orchestration | ⏳ Planned | LangGraph state management examples |

---

## 💡 8. Reflection
This project showed me how the Model Context Protocol can bridge the gap between LangChain's tool ecosystem and external services, creating a standardized way for AI agents to discover and use diverse capabilities. The dual transport approach (stdio + streamable-http) demonstrates the flexibility needed for different deployment scenarios, from local development to cloud-based services.

The educational focus on step-by-step examples and debugging utilities makes complex MCP integration patterns accessible to learners, turning technical concepts into hands-on experience.

> "This project showed me how structure, documentation, and intent can turn AI tools into learning partners."

---

**Next Step:**  
Once this overview feels solid, generate your `ARCHITECTURE_OVERVIEW.md` to dive deeper into *how* it works.
