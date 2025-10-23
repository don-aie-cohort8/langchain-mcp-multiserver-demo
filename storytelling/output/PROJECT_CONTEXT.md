# Project Context

- **Problem & Audience:** AI engineers and developers learning to integrate multiple MCP (Model Context Protocol) servers with LangChain agents need a clear, working example that demonstrates both stdio and streamable-http transport patterns.

- **Goal/Outcomes:** 
  - Demonstrate multi-server MCP integration patterns with LangChain
  - Show both stdio and streamable-http transport methods
  - Provide working examples of tool conversion from LangChain to MCP format
  - Create educational materials for AIE Cohort 8 students
  - Enable hands-on learning of MCP server orchestration

- **Stack (LLM App Stack):** 
  - **LLM:** OpenAI GPT models via LangChain
  - **Orchestration:** LangChain agents with LangGraph integration
  - **Protocol:** Model Context Protocol (MCP) with FastMCP
  - **Transport:** Both stdio and streamable-http
  - **Tools:** Custom MCP servers (weather, math, LangChain tools)
  - **UI:** Jupyter notebooks for interactive learning
  - **Monitoring:** Display utilities for agent response tracing

- **Patterns:** 
  - Multi-server MCP integration
  - Tool conversion from LangChain to MCP format using `langchain-mcp-adapters`
  - Streamable HTTP transport for web-based MCP servers
  - Agent orchestration with tool discovery and execution
  - Response formatting and debugging utilities

- **Key Artifacts:** 
  - `servers/weather_server.py` - Mock weather MCP server (streamable-http)
  - `servers/langchain_tools_server.py` - LangChain tools converted to MCP format
  - `servers/math_server.py` - Math operations MCP server (stdio)
  - `clients/client.ipynb` - Interactive learning notebook
  - `clients/display_utils.py` - Agent response formatting utilities
  - `clients/integration_test.py` - Complete working example
  - `pyproject.toml` - Project dependencies and configuration

- **Milestones/Results:** 
  - ✅ Successfully integrated multiple MCP servers with different transport methods
  - ✅ Created working examples of LangChain tool conversion to MCP format
  - ✅ Built comprehensive display utilities for agent response debugging
  - ✅ Developed educational notebook with step-by-step learning path
  - ✅ Demonstrated both stdio and streamable-http transport patterns
  - ✅ Created reusable server templates with command-line configuration

- **Gaps & TODOs:** 
  - TODO: Add more complex tool examples (file operations, API integrations)
  - TODO: Implement error handling and retry logic for server connections
  - TODO: Add authentication/authorization patterns for production use
  - TODO: Create deployment examples (Docker, cloud services)
  - TODO: Add performance monitoring and metrics collection
  - TODO: Expand LangGraph integration examples with state management
  - TODO: Create production-ready server configurations
  - TODO: Add comprehensive testing suite for MCP server interactions
