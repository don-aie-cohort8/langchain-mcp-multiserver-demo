"""
Weather MCP Server

A simple MCP server that provides mock weather information using the streamable-http transport.

This server demonstrates:
- FastMCP server setup with streamable-http transport
- Tool definition with async functions
- Command-line argument handling for port configuration

Usage:
    # Default port (8000)
    python weather_server.py

    # Custom port
    python weather_server.py --port 8080

    # Custom host and port
    python weather_server.py --host 0.0.0.0 --port 8080
"""

import argparse
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location.

    Args:
        location: The location to get weather for (e.g., "NYC", "London", "Tokyo")

    Returns:
        str: Weather description for the requested location
    """
    return f"It's always sunny in {location}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run server on (default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 for local access only, use 0.0.0.0 for network access)"
    )
    args = parser.parse_args()

    # ✅ set host/port on the instance
    mcp.host = args.host
    mcp.port = args.port

    print(f"Starting Weather MCP Server on http://{args.host}:{args.port}/mcp")
    mcp.run(transport="streamable-http")
