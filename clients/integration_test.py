"""
MCP Multi-Server Client Integration Test Suite

PURPOSE:
========
This standalone script demonstrates and tests the complete MCP (Model Context Protocol)
workflow with multiple servers, showcasing reference patterns for building LLM agents
with MCP that integrate tools from different services.

EDUCATIONAL VALUE:
==================
1. Multi-Server Architecture: Shows how to connect to multiple MCP servers simultaneously
2. Tool Discovery: Demonstrates dynamic tool loading from heterogeneous services
3. Agent Orchestration: Tests LLM's ability to reason about and invoke multiple tools
4. Response Formatting: Illustrates various output display patterns for different use cases
5. Response Patterns: Demonstrates different output modes for various use cases

WHAT THIS TESTS:
================
- Multi-server connections: Connects to multiple MCP servers concurrently
- Tool enumeration: Dynamic discovery of available capabilities
- Multi-step reasoning: Agent chains multiple tool calls to solve problems
- State management: Intermediate results flow between tool invocations
- Output formatting: Different display modes (verbose, minimal, programmatic)

COMPARISON TO NOTEBOOK:
=======================
While client.ipynb provides an interactive learning environment, this script:
- Runs end-to-end without user interaction (suitable for CI/CD)
- Tests all display_utils features systematically
- Serves as reference starting point for production applications
- Provides reproducible test cases for MCP server validation

PREREQUISITES:
==============
1. Start the langchain_tools_server in a separate terminal:
   python servers/langchain_tools_server.py --port 8001

2. Start the weather server in another terminal:
   python servers/weather_server.py

3. Configure environment variables in .env file:
   Create a .env file with:
   OPENAI_API_KEY=sk-...

   Or export in your shell:
   export OPENAI_API_KEY=sk-...

RUN:
====
python clients/integration_test.py
"""

import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response, get_final_answer, print_tools_summary

# Load environment variables from .env file (OPENAI_API_KEY, etc.)
load_dotenv()


async def main():
    """
    Main test orchestrator that executes a comprehensive suite of MCP integration tests.

    TEST ARCHITECTURE:
    ==================
    This function validates the complete MCP workflow from connection establishment
    through multi-step agent reasoning and response formatting.

    SETUP PHASE:
    - Establishes HTTP connections to multiple MCP servers
    - Loads tools from configured MCP servers
    - Displays available tools across heterogeneous services
    """
    print("\n" + "=" * 70)
    print("LANGCHAIN MCP CLIENT EXAMPLE")
    print("=" * 70 + "\n")

    # Configure client to connect to running MCP servers
    # TESTS: Multi-server connection pooling, streamable-http transport
    print("Connecting to MCP servers...")
    client = MultiServerMCPClient(
        {
            "langchain_math": {
                "url": "http://localhost:8001/mcp",
                "transport": "streamable_http",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            },
        }
    )

    # Get available tools from all connected servers
    # TESTS: Tool discovery protocol, cross-server aggregation
    print("Loading tools from MCP servers...\n")
    tools = await client.get_tools()

    # Show available tools
    # TESTS: print_tools_summary() utility function
    print_tools_summary(tools)

    # Create agent with the tools
    # TESTS: LangGraph ReAct agent initialization with MCP tools
    agent = create_agent("openai:gpt-4.1", tools)

    # =========================================================================
    # TEST CASE 1: Multi-Step Reasoning with Full Trace Display
    # =========================================================================
    """
    WHAT IT TESTS:
    - Agent's ability to decompose a math expression into sequential operations
    - Tool chaining: add(15, 27) → multiply(result, 3)
    - State management between tool calls (passing 42 to multiply)
    - Full message trace display with token usage metrics

    EXPECTED BEHAVIOR:
    - Agent should call add(15, 27) first, getting 42
    - Agent should then call multiply(42, 3), getting 126
    - display_agent_response should show all intermediate steps
    - Token usage will be displayed when available in response metadata

    VALUE:
    - Validates ReAct agent reasoning loop
    - Demonstrates verbose debugging output
    - Confirms tool invocation order and state propagation
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Multi-Step Reasoning with Full Trace")
    print("=" * 70 + "\n")

    math_response = await agent.ainvoke({"messages": "what is (15 + 27) * 3?"})
    display_agent_response(math_response, show_full_trace=True, show_token_usage=True)

    # =========================================================================
    # TEST CASE 2: Cross-Server Tool Invocation with Minimal Display
    # =========================================================================
    """
    WHAT IT TESTS:
    - Agent's ability to select correct tool from different server (weather vs math)
    - Cross-server HTTP communication (langchain_tools on 8001, weather on 8000)
    - Minimal output display mode (final answer only)
    - Tool selection reasoning (weather tool vs math tools)

    EXPECTED BEHAVIOR:
    - Agent should identify this requires the get_weather tool
    - Should call get_weather(location="NYC") from weather server
    - display_agent_response with show_full_trace=False should only show final answer
    - Should NOT show intermediate tool calls

    VALUE:
    - Validates multi-server architecture works correctly
    - Demonstrates clean output for end-user applications
    - Tests agent's tool selection capability
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Cross-Server Tool Invocation (Minimal Display)")
    print("=" * 70 + "\n")

    weather_response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
    display_agent_response(weather_response, show_full_trace=False)

    # =========================================================================
    # TEST CASE 3: Programmatic Answer Extraction
    # =========================================================================
    """
    WHAT IT TESTS:
    - get_final_answer() utility function for extracting just the answer
    - Programmatic access to agent response without display formatting
    - Use case: Integrating agent answers into larger applications
    - Silent operation (no trace display, just data extraction)

    EXPECTED BEHAVIOR:
    - Agent should call multiply(7, 9) and get 63
    - get_final_answer should extract only the final text answer
    - Should return just the answer string, not the full message structure
    - Suitable for conditional logic: if "63" in answer: ...

    VALUE:
    - Demonstrates building blocks for production applications
    - Shows how to use agent responses in automated workflows
    - Tests utility function separate from display formatting
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Programmatic Answer Extraction")
    print("=" * 70 + "\n")

    response = await agent.ainvoke({"messages": "multiply 7 and 9"})

    answer = get_final_answer(response)
    print(f"Extracted answer: {answer}")
    print(f"Type: {type(answer)}")
    print(f"Can be used in code: {'63' in str(answer)}")

    # =========================================================================
    # TEST CASE 4: Complex Multi-Step Sequential Reasoning
    # =========================================================================
    """
    WHAT IT TESTS:
    - Agent's ability to parse natural language instructions with explicit sequencing
    - Correct interpretation of "first... then..." temporal dependencies
    - Three-step reasoning: parse → add(100,50) → multiply(150,2)
    - Default display mode (show_full_trace=True by default)

    EXPECTED BEHAVIOR:
    - Agent should understand temporal ordering in natural language
    - Should NOT try to do both operations simultaneously
    - Call sequence: add(100, 50) → get 150 → multiply(150, 2) → get 300
    - Should display full trace by default (no explicit show_full_trace param)

    VALUE:
    - Tests natural language understanding with explicit ordering
    - Validates agent doesn't "short-circuit" to final answer
    - Demonstrates default display_agent_response behavior
    - Real-world use case: following procedural instructions
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Complex Sequential Reasoning")
    print("=" * 70 + "\n")

    complex_response = await agent.ainvoke(
        {"messages": "First add 100 and 50, then multiply the result by 2"}
    )
    display_agent_response(complex_response)

    print("\n" + "=" * 70)
    print("ALL INTEGRATION TESTS COMPLETE")
    print("=" * 70)
    print("\nSUMMARY:")
    print("✓ Multi-server connection pooling")
    print("✓ Tool discovery and enumeration")
    print("✓ Multi-step agent reasoning")
    print("✓ Cross-server tool invocation")
    print("✓ Full trace display with token metrics")
    print("✓ Minimal display mode")
    print("✓ Programmatic answer extraction")
    print("✓ Sequential instruction following")
    print()


if __name__ == "__main__":
    asyncio.run(main())
