"""
Weather Service - PydanticAI Implementation

This implementation shows how the SAME weather service can be built as
a PydanticAI agent with tools, instead of a REST API or MCP server.

KEY DIFFERENCES FROM FastAPI/FastMCP:
1. Agent-centric: Initialize Agent() instead of FastAPI() or FastMCP()
2. Decorator: @agent.tool_plain instead of @app.post() or @mcp.tool
3. System prompt: Guides agent behavior (not present in API/MCP servers)
4. Usage: Can be used directly OR exposed as MCP/A2A server
5. LLM integration: Agent uses tools to fulfill user requests

WHAT STAYS THE SAME:
- Pydantic models (WeatherQuery, WeatherResponse) - IDENTICAL
- Function body (business logic) - IDENTICAL
- Validation (automatic from Pydantic)
- Docstrings (become tool descriptions for LLM)

This demonstrates that PydanticAI follows the same patterns as FastAPI/FastMCP,
just with an agent wrapper around the tools.
"""

import os
import argparse
from dotenv import load_dotenv
from pydantic_ai import Agent

# Import shared Pydantic models (SAME as FastAPI and FastMCP versions)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.models import WeatherQuery, WeatherResponse, WeatherForecast

load_dotenv()

# Initialize PydanticAI agent (compare to: app = FastAPI(...) or mcp = FastMCP(...))
agent = Agent(
    'openai:gpt-4o-mini',  # Model to use for agent reasoning
    system_prompt="""You are a helpful weather assistant.

When users ask about weather, use the get_weather tool to fetch information.

Guidelines:
- Always confirm the location if it's ambiguous
- Ask about units preference if not specified
- Offer forecast if the user might find it helpful
- Be concise but informative
"""
)


@agent.tool_plain  # Compare to: @app.post() or @mcp.tool
def get_weather(query: WeatherQuery) -> WeatherResponse:
    """
    Get weather information for a location.

    This tool accepts a WeatherQuery and returns WeatherResponse.
    The agent will call this tool when users ask about weather.

    **Parameters:**
    - **location**: City name (e.g., 'NYC') or coordinates (e.g., '40.7,-74.0')
    - **units**: Temperature units ('celsius' or 'fahrenheit')
    - **include_forecast**: Whether to include 3-day forecast

    **Returns:**
    - Current temperature and conditions
    - Optional 3-day forecast
    """

    # Validate location
    if not query.location or query.location.strip() == "":
        raise ValueError("Location cannot be empty")

    # ========================================================================
    # BUSINESS LOGIC - IDENTICAL TO FASTAPI AND FASTMCP VERSIONS
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

    # Return validated response
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
# Running the Agent
# ============================================================================

async def run_interactive():
    """
    Run the agent in interactive mode (direct agent usage).
    """
    print("Weather Agent (PydanticAI) - Interactive Mode")
    print("Ask about weather in any location!")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            # Run agent with user input
            result = await agent.run(user_input)

            # Display response
            print(f"Agent: {result.data}\n")

        except Exception as e:
            print(f"Error: {e}\n")


async def run_as_mcp_server(host: str, port: int):
    """
    Expose the agent as an MCP server.

    This shows how PydanticAI agents can become MCP tools
    for integration with other systems.
    """
    from mcp.server.fastmcp import FastMCP

    # Create MCP server
    mcp = FastMCP("Weather Agent")

    # Expose agent as MCP tool
    @mcp.tool
    async def ask_weather_agent(question: str) -> str:
        """Ask the weather agent a question (uses AI reasoning + tools)"""
        result = await agent.run(question)
        return result.data

    print(f"Starting Weather Agent (PydanticAI) as MCP server")
    print(f"Endpoint: http://{host}:{port}/mcp")
    print("This exposes the agent's capabilities as MCP tools\n")

    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="Weather Service PydanticAI Agent")
    parser.add_argument(
        "--mode",
        type=str,
        default="interactive",
        choices=["interactive", "mcp"],
        help="Run mode: interactive (direct agent usage) or mcp (expose as MCP server)"
    )
    parser.add_argument("--port", type=int, default=8200, help="Port for MCP server mode")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for MCP server mode")
    args = parser.parse_args()

    if args.mode == "interactive":
        asyncio.run(run_interactive())
    else:
        asyncio.run(run_as_mcp_server(args.host, args.port))


# ============================================================================
# Usage Examples
# ============================================================================

"""
COMPARISON: FastAPI vs FastMCP vs PydanticAI

┌──────────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Aspect               │ FastAPI          │ FastMCP          │ PydanticAI       │
├──────────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ Server Init          │ FastAPI(...)     │ FastMCP(...)     │ Agent(...)       │
│ Function Decorator   │ @app.post()      │ @mcp.tool        │ @agent.tool_plain│
│ System Prompt        │ N/A              │ N/A              │ ✓ Guides LLM     │
│ Error Handling       │ HTTPException    │ ToolError        │ ValueError       │
│ Direct Usage         │ HTTP clients     │ MCP clients      │ ✓ agent.run()    │
│ Pydantic Models      │ ✓ SAME           │ ✓ SAME           │ ✓ SAME           │
│ Validation           │ ✓ SAME           │ ✓ SAME           │ ✓ SAME           │
│ Business Logic       │ ✓ SAME           │ ✓ SAME           │ ✓ SAME           │
└──────────────────────┴──────────────────┴──────────────────┴──────────────────┘

RUNNING THE AGENT:

1. Interactive Mode (direct agent usage):
   python examples/weather_service/pydanticai_impl.py --mode interactive

   You: What's the weather in NYC?
   Agent: [Agent uses get_weather tool and responds]

2. MCP Server Mode (expose agent as MCP tools):
   python examples/weather_service/pydanticai_impl.py --mode mcp --port 8200

   The agent becomes an MCP tool that other systems can call.

PROGRAMMATIC USAGE:

import asyncio
from pydanticai_impl import agent

async def main():
    # Direct agent usage
    result = await agent.run("What's the weather in Tokyo with forecast?")
    print(result.data)  # Agent's natural language response

asyncio.run(main())

INTEGRATION WITH MCP:

The agent can be exposed as an MCP server, making it callable by:
- Claude Desktop
- LangChain agents
- Other MCP clients

This creates a hybrid: AI agent capabilities + MCP protocol interoperability.

KEY INSIGHT:
PydanticAI adds agent reasoning (via LLM) on top of the same tool pattern.
The tool definition (get_weather) is IDENTICAL to FastAPI/FastMCP,
but now the agent can:
- Understand natural language queries
- Call tools automatically
- Combine multiple tool calls
- Provide conversational responses

Think of it as: FastAPI = REST endpoints, FastMCP = MCP tools, PydanticAI = AI agent with tools
"""
