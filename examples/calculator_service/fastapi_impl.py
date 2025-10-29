"""
Calculator Service - FastAPI Implementation

This is the BASELINE implementation using FastAPI (REST API).
Students should already be familiar with this pattern.

Key FastAPI concepts demonstrated:
- App initialization with metadata
- POST endpoint with Pydantic request/response models
- Automatic OpenAPI schema generation
- HTTPException for error handling
- Async route handlers

Compare this to:
- fastmcp_impl.py (MCP server with tools)
- pydanticai_impl.py (AI agent with tools)
- fasta2a_impl.py (Stateful agent with task queue)
"""

import argparse
from fastapi import FastAPI, HTTPException

# Import shared Pydantic models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.models import CalculationRequest, CalculationResponse


# Initialize FastAPI app with OpenAPI metadata
app = FastAPI(
    title="Calculator Service API",
    description="REST API for mathematical calculations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.post(
    "/calculate",
    response_model=CalculationResponse,
    summary="Perform Calculation",
    description="Execute a mathematical operation on two operands"
)
async def calculate(request: CalculationRequest) -> CalculationResponse:
    """
    Perform a mathematical calculation.

    This endpoint accepts a CalculationRequest and returns CalculationResponse.

    **Parameters:**
    - **operation**: One of 'add', 'subtract', 'multiply', 'divide'
    - **a**: First operand
    - **b**: Second operand

    **Returns:**
    - Result of the calculation or error message
    """

    # Validate operation
    if request.operation not in ["add", "subtract", "multiply", "divide"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation: {request.operation}"
        )

    # Perform calculation
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


@app.get("/health", summary="Health Check")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "calculator-api"}


@app.get("/", summary="Service Info")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "Calculator Service API",
        "version": "1.0.0",
        "framework": "FastAPI",
        "operations": ["add", "subtract", "multiply", "divide"],
        "endpoints": {
            "docs": "/docs",
            "calculate": "POST /calculate",
            "health": "/health"
        }
    }


# ============================================================================
# Running the Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Calculator Service FastAPI Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    print(f"Starting Calculator Service (FastAPI) on http://{args.host}:{args.port}")
    print(f"OpenAPI docs available at: http://{args.host}:{args.port}/docs")
    print(f"ReDoc available at: http://{args.host}:{args.port}/redoc")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


# ============================================================================
# Usage Examples
# ============================================================================

"""
1. Start the server:
   python examples/calculator_service/fastapi_impl.py --port 8000

2. Test with curl:
   curl -X POST http://localhost:8000/calculate \\
     -H "Content-Type: application/json" \\
     -d '{"operation": "add", "a": 5.0, "b": 3.0}'

3. View OpenAPI docs:
   Open http://localhost:8000/docs in browser

4. Test with Python requests:
   import requests
   response = requests.post(
       "http://localhost:8000/calculate",
       json={"operation": "multiply", "a": 7.0, "b": 6.0}
   )
   print(response.json())

5. Test division by zero error handling:
   curl -X POST http://localhost:8000/calculate \\
     -H "Content-Type: application/json" \\
     -d '{"operation": "divide", "a": 10.0, "b": 0.0}'

   Response: {"operation": "divide", "operands": [10.0, 0.0], "result": null, "error": "Division by zero is not allowed"}

COMPARISON TO OTHER IMPLEMENTATIONS:
- FastMCP: Same Pydantic models, different decorator (@mcp.tool instead of @app.post)
- PydanticAI: Same models, agent-centric (tool registered with agent)
- FastA2A: Same models, adds task queue and stateful context
"""
