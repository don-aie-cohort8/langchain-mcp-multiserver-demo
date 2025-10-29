"""
Weather Service - FastAPI Implementation

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
from fastapi.responses import JSONResponse

# Import shared Pydantic models
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.models import WeatherQuery, WeatherResponse, WeatherForecast


# Initialize FastAPI app with OpenAPI metadata
app = FastAPI(
    title="Weather Service API",
    description="REST API for weather information lookup",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.post(
    "/weather",
    response_model=WeatherResponse,
    summary="Get Weather Information",
    description="Retrieve current weather and optional forecast for a location"
)
async def get_weather(query: WeatherQuery) -> WeatherResponse:
    """
    Get weather information for a location.

    This endpoint accepts a WeatherQuery and returns WeatherResponse.

    **Parameters:**
    - **location**: City name (e.g., 'NYC') or coordinates (e.g., '40.7,-74.0')
    - **units**: Temperature units ('celsius' or 'fahrenheit')
    - **include_forecast**: Whether to include 3-day forecast

    **Returns:**
    - Current temperature and conditions
    - Optional 3-day forecast
    """

    # Validate location is not empty
    if not query.location or query.location.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Location cannot be empty"
        )

    # Simulate weather lookup (in production, this would call a real API)
    # Convert temperature based on units
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


@app.get("/health", summary="Health Check")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "weather-api"}


@app.get("/", summary="Service Info")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "Weather Service API",
        "version": "1.0.0",
        "framework": "FastAPI",
        "endpoints": {
            "docs": "/docs",
            "weather": "POST /weather",
            "health": "/health"
        }
    }


# ============================================================================
# Running the Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Weather Service FastAPI Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    print(f"Starting Weather Service (FastAPI) on http://{args.host}:{args.port}")
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
   python examples/weather_service/fastapi_impl.py --port 8000

2. Test with curl:
   curl -X POST http://localhost:8000/weather \\
     -H "Content-Type: application/json" \\
     -D '{"location": "NYC", "units": "fahrenheit", "include_forecast": true}'

3. View OpenAPI docs:
   Open http://localhost:8000/docs in browser

4. Test with Python requests:
   import requests
   response = requests.post(
       "http://localhost:8000/weather",
       json={"location": "NYC", "units": "fahrenheit", "include_forecast": True}
   )
   print(response.json())

COMPARISON TO OTHER IMPLEMENTATIONS:
- FastMCP: Same Pydantic models, different decorator (@mcp.tool instead of @app.post)
- PydanticAI: Same models, agent-centric (tool registered with agent)
- FastA2A: Same models, adds task queue and stateful context
"""
