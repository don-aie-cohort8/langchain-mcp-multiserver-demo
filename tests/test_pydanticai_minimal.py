#!/usr/bin/env python3
"""
Minimal PydanticAI Test

Tests that PydanticAI calculator agent:
1. Can parse natural language to tool calls
2. Basic operations work
3. Error cases are handled gracefully

No server needed - direct agent invocation.

Time: ~1 minute
"""

import asyncio
import sys
from pathlib import Path

# Add calculator_service to path
sys.path.insert(0, str(Path(__file__).parent.parent / "examples" / "calculator_service"))

from pydanticai_impl import agent


async def test_pydanticai():
    print("Testing PydanticAI Calculator Agent...")
    print("=" * 50)

    # Test 1: Natural language query (5 + 3)
    print("\nTest 1: Natural language (What is 5 plus 3?)...")
    result = await agent.run("What is 5 plus 3?")
    assert "8" in result.data, f"Expected '8' in response, got: {result.data}"
    print(f"✓ Natural language works: '{result.data}'")

    # Test 2: Explicit calculation
    print("\nTest 2: Explicit calculation (42 × 7)...")
    result = await agent.run("Calculate 42 multiplied by 7")
    assert "294" in result.data, f"Expected '294' in response, got: {result.data}"
    print(f"✓ Multiplication works: '{result.data}'")

    # Test 3: Error case (divide by zero)
    print("\nTest 3: Error handling (10 ÷ 0)...")
    result = await agent.run("Divide 10 by 0")
    error_indicators = ["not allowed", "cannot", "impossible", "error", "zero"]
    has_error = any(indicator in result.data.lower() for indicator in error_indicators)
    assert has_error, f"Expected error message, got: {result.data}"
    print(f"✓ Error handling works: '{result.data}'")

    print("\n" + "=" * 50)
    print("✓ All PydanticAI tests passed!")


if __name__ == "__main__":
    try:
        asyncio.run(test_pydanticai())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("\nMake sure OPENAI_API_KEY is set in .env")
        sys.exit(1)
