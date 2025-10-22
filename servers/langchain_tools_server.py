import argparse
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_mcp_adapters.tools import to_fastmcp
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()


@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


# Convert LangChain tools to FastMCP
fastmcp_add = to_fastmcp(add)
fastmcp_multiply = to_fastmcp(multiply)


if __name__ == "__main__":
    # Parse arguments for streamable-http configuration
    parser = argparse.ArgumentParser(description="LangChain MCP Server")
    parser.add_argument("--port", type=int, default=8001, help="Port to run server on (default: 8001)")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1 for local access only, use 0.0.0.0 for network access)"
    )
    args = parser.parse_args()

    print(f"Starting LangChain MCP Server on {args.host}:{args.port}")
    print("Available tools: add, multiply")

    # Create FastMCP instance (with host/port for streamable-http)
    mcp = FastMCP(
        "LangChain Math Server",
        tools=[fastmcp_add, fastmcp_multiply],
        host=args.host,
        port=args.port
    )

    # Run with streamable-http transport (instead of stdio)
    mcp.run(transport="streamable-http")
