#!/usr/bin/env python3
"""
Minimal FastMCP Test

Tests that FastMCP calculator service:
1. Tools can be discovered
2. Basic operation works (add)
3. Error case works (divide by zero)

Prerequisites: FastMCP server must be running
  python examples/calculator_service/fastmcp_impl.py --port 8100

Time: ~2 minutes
"""

import asyncio
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient


async def test_fastmcp():
    print("Testing FastMCP Calculator Service...")
    print("=" * 50)

    # Configure client for HTTP transport
    client = MultiServerMCPClient({
        "calculator": {
            "url": "http://localhost:8100/mcp",
            "transport": "streamable_http"
        }
    })

    # Test 1: Tool discovery (proves server is running)
    print("\nTest 1: Tool discovery...")
    tools = await client.get_tools()
    assert len(tools) > 0, "No tools discovered"
    print(f"✓ Discovered {len(tools)} tool(s)")

    # Find the calculate tool
    calc_tool = None
    for tool in tools:
        if "calculate" in tool.name.lower():
            calc_tool = tool
            break

    assert calc_tool is not None, "Calculate tool not found"
    print(f"✓ Found tool: {calc_tool.name}")

    # Test 2: Basic operation (add 5 + 3)
    print("\nTest 2: Basic operation (5 + 3)...")
    result = await calc_tool.ainvoke({
        "request": {
            "operation": "add",
            "a": 5.0,
            "b": 3.0
        }
    })

    assert result.get("result") == 8.0, f"Expected 8.0, got {result.get('result')}"
    assert result.get("error") is None, f"Unexpected error: {result.get('error')}"
    print(f"✓ Addition works: 5 + 3 = {result['result']}")

    # Test 3: Error case (divide by zero)
    print("\nTest 3: Error handling (10 ÷ 0)...")
    result = await calc_tool.ainvoke({
        "request": {
            "operation": "divide",
            "a": 10.0,
            "b": 0.0
        }
    })

    assert result.get("error") is not None, "Expected error for division by zero"
    assert result.get("result") is None, f"Expected null result, got {result.get('result')}"
    assert "zero" in result["error"].lower(), f"Error message doesn't mention zero: {result['error']}"
    print(f"✓ Division by zero handled: {result['error']}")

    print("\n" + "=" * 50)
    print("✓ All FastMCP tests passed!")


if __name__ == "__main__":
    try:
        asyncio.run(test_fastmcp())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("\nMake sure FastMCP server is running:")
        print("  python examples/calculator_service/fastmcp_impl.py --port 8100")
        sys.exit(1)
