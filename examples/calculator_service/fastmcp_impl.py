"""
Calculator Service - FastMCP Implementation

This implementation shows how the SAME calculator service can be exposed
as an MCP (Model Context Protocol) server instead of a REST API.

KEY DIFFERENCES FROM FastAPI (fastapi_impl.py):
1. Server initialization: FastMCP() instead of FastAPI()
2. Decorator: @mcp.tool instead of @app.post()
3. Error handling: ToolError instead of HTTPException
4. Transport: MCP protocol instead of HTTP REST
5. Return type: Uses type annotation instead of response_model parameter

WHAT STAYS THE SAME:
- Pydantic models (CalculationRequest, CalculationResponse) - IDENTICAL
- Function signature (async def calculate)
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
from common.models import CalculationRequest, CalculationResponse


# Initialize FastMCP server (compare to: app = FastAPI(...))
mcp = FastMCP("Calculator Service")


@mcp.tool  # Compare to: @app.post("/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest) -> CalculationResponse:  # Return type replaces response_model
    """
    Perform a mathematical calculation.

    This tool accepts a CalculationRequest and returns CalculationResponse.
    The docstring becomes the tool description exposed to LLMs.

    **Parameters:**
    - **operation**: One of 'add', 'subtract', 'multiply', 'divide'
    - **a**: First operand
    - **b**: Second operand

    **Returns:**
    - Result of the calculation or error message
    """

    # Validate operation (compare to: raise HTTPException)
    if request.operation not in ["add", "subtract", "multiply", "divide"]:
        raise ToolError(f"Invalid operation: {request.operation}")  # ToolError instead of HTTPException

    # ========================================================================
    # BUSINESS LOGIC - IDENTICAL TO FASTAPI VERSION
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

    # Return validated response (Pydantic ensures type safety)
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
# Running the Server
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculator Service FastMCP Server")
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
        print(f"Starting Calculator Service (FastMCP) on http://{args.host}:{args.port}/mcp")
        print(f"Transport: streamable-http (HTTP POST + Server-Sent Events)")
        print(f"\nMCP endpoint: http://{args.host}:{args.port}/mcp")
        print(f"To discover tools: POST to /mcp with MCP list_tools message")

        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port
        )
    else:
        print(f"Starting Calculator Service (FastMCP) with {args.transport} transport")
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
│ Function Decorator   │ @app.post("/calculate") │ @mcp.tool               │
│ Response Model       │ response_model=Calc     │ -> CalculationResponse  │
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
   python examples/calculator_service/fastmcp_impl.py --port 8100 --transport streamable-http

2. stdio Transport (for Claude Desktop, subprocess integration):
   python examples/calculator_service/fastmcp_impl.py --transport stdio

TESTING WITH MCP CLIENT:

from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "calculator": {
        "url": "http://localhost:8100/mcp",
        "transport": "streamable_http"
    }
})

tools = await client.get_tools()
# Tools include: calculate with CalculationRequest schema

INTEGRATION WITH LANGCHAIN:

from langchain.agents import create_agent

agent = create_agent("openai:gpt-4.1", tools)
response = await agent.ainvoke({
    "messages": "What's 42 multiplied by 7?"
})

The agent will automatically call the calculate tool with proper parameters.

KEY INSIGHT:
If you know FastAPI, you already understand 95% of FastMCP.
The only changes are:
- Decorator (@mcp.tool vs @app.post)
- Error type (ToolError vs HTTPException)
- Transport (MCP vs HTTP REST)

Everything else (Pydantic, validation, async, business logic) is IDENTICAL.

EXAMPLE TOOL CALLS:

1. Addition:
   {"operation": "add", "a": 15.0, "b": 27.0}
   → {"operation": "add", "operands": [15.0, 27.0], "result": 42.0, "error": null}

2. Division:
   {"operation": "divide", "a": 100.0, "b": 4.0}
   → {"operation": "divide", "operands": [100.0, 4.0], "result": 25.0, "error": null}

3. Division by zero (error handling):
   {"operation": "divide", "a": 10.0, "b": 0.0}
   → {"operation": "divide", "operands": [10.0, 0.0], "result": null, "error": "Division by zero is not allowed"}

4. Subtraction:
   {"operation": "subtract", "a": 50.0, "b": 8.0}
   → {"operation": "subtract", "operands": [50.0, 8.0], "result": 42.0, "error": null}
"""
