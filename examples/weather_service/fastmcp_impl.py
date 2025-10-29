"""
Weather Service - FastMCP Implementation

This implementation shows how the SAME weather service can be exposed
as an MCP (Model Context Protocol) server instead of a REST API.

KEY DIFFERENCES FROM FastAPI (fastapi_impl.py):
1. Server initialization: FastMCP() instead of FastAPI()
2. Decorator: @mcp.tool instead of @app.post()
3. Error handling: ToolError instead of HTTPException
4. Transport: MCP protocol instead of HTTP REST
5. Return type: Uses type annotation instead of response_model parameter

WHAT STAYS THE SAME:
- Pydantic models (WeatherQuery, WeatherResponse) - IDENTICAL
- Function signature (async def get_weather)
- Function body (business logic) - IDENTICAL
- Validation (automatic from Pydantic)
- Docstrings (become tool descriptions)

This demonstrates that FastMCP feels like "FastAPI for AI tools."
"""

import argparse
from mcp.server.fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# Import shared Pydantic models (SAME as FastAPI version)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.models import WeatherQuery, WeatherResponse, WeatherForecast


# Initialize FastMCP server (compare to: app = FastAPI(...))
mcp = FastMCP("Weather Service")


@mcp.tool  # Compare to: @app.post("/weather", response_model=WeatherResponse)
async def get_weather(query: WeatherQuery) -> WeatherResponse:  # Return type replaces response_model
    """
    Get weather information for a location.

    This tool accepts a WeatherQuery and returns WeatherResponse.
    The docstring becomes the tool description exposed to LLMs.

    **Parameters:**
    - **location**: City name (e.g., 'NYC') or coordinates (e.g., '40.7,-74.0')
    - **units**: Temperature units ('celsius' or 'fahrenheit')
    - **include_forecast**: Whether to include 3-day forecast

    **Returns:**
    - Current temperature and conditions
    - Optional 3-day forecast
    """

    # Validate location (compare to: raise HTTPException)
    if not query.location or query.location.strip() == "":
        raise ToolError("Location cannot be empty")  # ToolError instead of HTTPException

    # ========================================================================
    # BUSINESS LOGIC - IDENTICAL TO FASTAPI VERSION
    # ========================================================================

    # Simulate weather lookup
    temp = 72.0 if query.units == "fahrenheit" else 22.2

    # Build forecast if requested
    forecast = None
    if query.include_forecast:
        forecast = [
            WeatherForecast(
                day="Tomorrow",
                temp=temp + 2,
                conditions="Partly Cloudy"
            ),
            WeatherForecast(
                day="Day 2",
                temp=temp + 1,
                conditions="Sunny"
            ),
            WeatherForecast(
                day="Day 3",
                temp=temp - 1,
                conditions="Cloudy"
            )
        ]

    # Return validated response (Pydantic ensures type safety)
    return WeatherResponse(
        location=query.location,
        current_temp=temp,
        units=query.units,
        conditions="Sunny",
        forecast=forecast
    )

    # ========================================================================
    # END BUSINESS LOGIC
    # ========================================================================


# ============================================================================
# Running the Server
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Service FastMCP Server")
    parser.add_argument("--port", type=int, default=8100, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    parser.add_argument(
        "--transport",
        type=str,
        default="streamable-http",
        choices=["streamable-http", "stdio", "sse"],
        help="MCP transport protocol"
    )
    args = parser.parse_args()

    if args.transport == "streamable-http":
        print(f"Starting Weather Service (FastMCP) on http://{args.host}:{args.port}/mcp")
        print(f"Transport: streamable-http (HTTP POST + Server-Sent Events)")
        print(f"\nMCP endpoint: http://{args.host}:{args.port}/mcp")
        print(f"To discover tools: POST to /mcp with MCP list_tools message")

        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port
        )
    else:
        print(f"Starting Weather Service (FastMCP) with {args.transport} transport")
        print(f"This transport is for subprocess/local integrations")

        mcp.run(transport=args.transport)


# ============================================================================
# Usage Examples
# ============================================================================

"""
COMPARISON: FastAPI vs FastMCP

┌──────────────────────┬─────────────────────────┬─────────────────────────┐
│ Aspect               │ FastAPI                 │ FastMCP                 │
├──────────────────────┼─────────────────────────┼─────────────────────────┤
│ Server Init          │ app = FastAPI(...)      │ mcp = FastMCP(...)      │
│ Function Decorator   │ @app.post("/weather")   │ @mcp.tool               │
│ Response Model       │ response_model=Weather  │ -> WeatherResponse      │
│ Error Handling       │ HTTPException           │ ToolError               │
│ Transport            │ HTTP REST               │ MCP (stdio/HTTP/SSE)    │
│ Client Discovery     │ OpenAPI /docs           │ MCP list_tools()        │
│ Pydantic Models      │ ✓ SAME                  │ ✓ SAME                  │
│ Validation           │ ✓ SAME                  │ ✓ SAME                  │
│ Async/Await          │ ✓ SAME                  │ ✓ SAME                  │
│ Business Logic       │ ✓ SAME                  │ ✓ SAME                  │
└──────────────────────┴─────────────────────────┴─────────────────────────┘

RUNNING THE SERVER:

1. HTTP Transport (for web services):
   python examples/weather_service/fastmcp_impl.py --port 8100 --transport streamable-http

2. stdio Transport (for Claude Desktop, subprocess integration):
   python examples/weather_service/fastmcp_impl.py --transport stdio

TESTING WITH MCP CLIENT:

from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "weather": {
        "url": "http://localhost:8100/mcp",
        "transport": "streamable_http"
    }
})

tools = await client.get_tools()
# Tools include: get_weather with WeatherQuery schema

INTEGRATION WITH LANGCHAIN:

from langchain.agents import create_agent

agent = create_agent("openai:gpt-4.1", tools)
response = await agent.ainvoke({
    "messages": "What's the weather in NYC with forecast?"
})

The agent will automatically call the get_weather tool with proper parameters.

KEY INSIGHT:
If you know FastAPI, you already understand 95% of FastMCP.
The only changes are:
- Decorator (@mcp.tool vs @app.post)
- Error type (ToolError vs HTTPException)
- Transport (MCP vs HTTP REST)

Everything else (Pydantic, validation, async, business logic) is IDENTICAL.
"""
