"""
Calculator Service - PydanticAI Implementation

This implementation shows how the SAME calculator service can be built as
a PydanticAI agent with tools, instead of a REST API or MCP server.

KEY DIFFERENCES FROM FastAPI/FastMCP:
1. Agent-centric: Initialize Agent() instead of FastAPI() or FastMCP()
2. Decorator: @agent.tool_plain instead of @app.post() or @mcp.tool
3. System prompt: Guides agent behavior (not present in API/MCP servers)
4. Usage: Can be used directly OR exposed as MCP/A2A server
5. LLM integration: Agent uses tools to fulfill user requests

WHAT STAYS THE SAME:
- Pydantic models (CalculationRequest, CalculationResponse) - IDENTICAL
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
from common.models import CalculationRequest, CalculationResponse

load_dotenv()

# Initialize PydanticAI agent (compare to: app = FastAPI(...) or mcp = FastMCP(...))
agent = Agent(
    'openai:gpt-4o-mini',  # Model to use for agent reasoning
    system_prompt="""You are a helpful calculator assistant.

When users ask about mathematical calculations, use the calculate tool.

Guidelines:
- Parse user requests into appropriate operations
- Handle multiple calculations in sequence if requested
- Explain results clearly
- Suggest alternative approaches when helpful
- Be precise with numerical results
"""
)


@agent.tool_plain  # Compare to: @app.post() or @mcp.tool
def calculate(request: CalculationRequest) -> CalculationResponse:
    """
    Perform a mathematical calculation.

    This tool accepts a CalculationRequest and returns CalculationResponse.
    The agent will call this tool when users ask about calculations.

    **Parameters:**
    - **operation**: One of 'add', 'subtract', 'multiply', 'divide'
    - **a**: First operand
    - **b**: Second operand

    **Returns:**
    - Result of the calculation or error message
    """

    # Validate operation
    if request.operation not in ["add", "subtract", "multiply", "divide"]:
        raise ValueError(f"Invalid operation: {request.operation}")

    # ========================================================================
    # BUSINESS LOGIC - IDENTICAL TO FASTAPI AND FASTMCP VERSIONS
    # ========================================================================

    result = None
    error = None

    try:
        if request.operation == "add":
            result = request.a + request.b
        elif request.operation == "subtract":
            result = request.a - request.b
        elif request.operation == "multiply":
            result = request.a * request.b
        elif request.operation == "divide":
            if request.b == 0:
                error = "Division by zero is not allowed"
            else:
                result = request.a / request.b

    except Exception as e:
        error = f"Calculation error: {str(e)}"

    # Return validated response
    return CalculationResponse(
        operation=request.operation,
        operands=[request.a, request.b],
        result=result,
        error=error
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
    print("Calculator Agent (PydanticAI) - Interactive Mode")
    print("Ask me to perform calculations!")
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
    mcp = FastMCP("Calculator Agent")

    # Expose agent as MCP tool
    @mcp.tool
    async def ask_calculator_agent(question: str) -> str:
        """Ask the calculator agent a question (uses AI reasoning + tools)"""
        result = await agent.run(question)
        return result.data

    print(f"Starting Calculator Agent (PydanticAI) as MCP server")
    print(f"Endpoint: http://{host}:{port}/mcp")
    print("This exposes the agent's capabilities as MCP tools\n")

    mcp.run(transport="streamable-http", host=host, port=port)


if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="Calculator Service PydanticAI Agent")
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
   python examples/calculator_service/pydanticai_impl.py --mode interactive

   You: What's 15 times 8?
   Agent: [Agent uses calculate tool] 15 times 8 equals 120.

   You: Calculate 100 divided by 4
   Agent: [Agent uses calculate tool] 100 divided by 4 equals 25.

2. MCP Server Mode (expose agent as MCP tools):
   python examples/calculator_service/pydanticai_impl.py --mode mcp --port 8200

   The agent becomes an MCP tool that other systems can call.

PROGRAMMATIC USAGE:

import asyncio
from pydanticai_impl import agent

async def main():
    # Direct agent usage with natural language
    result = await agent.run("Calculate 42 multiplied by 7")
    print(result.data)  # "42 multiplied by 7 equals 294."

    # Complex multi-step calculation
    result = await agent.run("What's (50 + 30) divided by 4?")
    print(result.data)  # Agent will calculate 50+30=80, then 80/4=20

asyncio.run(main())

INTEGRATION WITH MCP:

The agent can be exposed as an MCP server, making it callable by:
- Claude Desktop
- LangChain agents
- Other MCP clients

This creates a hybrid: AI agent capabilities + MCP protocol interoperability.

EXAMPLE INTERACTIONS:

User: "What's the square root of 144?"
Agent: "I can help with that! Let me break it down: the square root of 144 is 12,
        because 12 × 12 = 144."
        [Agent might use calculate tool: 12 * 12 = 144 to verify]

User: "Calculate 1000 divided by 25"
Agent: [Uses calculate tool with divide, 1000, 25]
       "1000 divided by 25 equals 40."

User: "What's 5 plus 7 minus 3?"
Agent: [Uses calculate tool twice: (5+7)=12, then (12-3)=9]
       "5 plus 7 is 12, and 12 minus 3 equals 9."

User: "Divide 10 by 0"
Agent: [Uses calculate tool, receives error]
       "I cannot divide 10 by 0 because division by zero is not allowed in mathematics."

KEY INSIGHT:
PydanticAI adds agent reasoning (via LLM) on top of the same tool pattern.
The tool definition (calculate) is IDENTICAL to FastAPI/FastMCP,
but now the agent can:
- Understand natural language queries
- Call tools automatically
- Handle multi-step calculations
- Provide conversational responses

Think of it as: FastAPI = REST endpoints, FastMCP = MCP tools, PydanticAI = AI agent with tools
"""
