"""
Weather Service - FastA2A Implementation

This implementation shows how the SAME weather service can be deployed as
a stateful agent using FastA2A (Agent-to-Agent Protocol), instead of
stateless REST/MCP or direct agent usage.

KEY DIFFERENCES FROM FastAPI/FastMCP/PydanticAI:
1. Stateful: Maintains conversation context across tasks
2. Task Queue: Asynchronous task processing with storage/broker
3. Agent Infrastructure: Requires storage + broker + worker
4. Multi-turn: Designed for ongoing conversations, not one-shot requests
5. Collaboration: Multiple agents can work on same context

WHAT STAYS THE SAME:
- Pydantic models (WeatherQuery, WeatherResponse) - IDENTICAL
- Tool definition (get_weather function) - IDENTICAL
- Business logic - IDENTICAL
- Agent definition (same as pydanticai_impl.py)

NEW CONCEPTS:
- Storage: Persists tasks and conversation context
- Broker: Manages task queue (like Celery)
- Task model: Wraps agent work in async tasks
- Context: Conversation thread spanning multiple tasks

WHEN TO USE THIS:
- Multi-turn conversations with memory
- Chatbots with conversation history
- Agent collaboration (multiple agents, one context)
- Long-running workflows

WHEN NOT TO USE THIS:
- Simple stateless queries (use FastMCP)
- REST API (use FastAPI)
- One-shot agent calls (use PydanticAI directly)
"""

import os
import argparse
from dotenv import load_dotenv
from pydantic_ai import Agent

# Import shared Pydantic models (SAME as all other implementations)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.models import WeatherQuery, WeatherResponse, WeatherForecast

load_dotenv()

# ============================================================================
# Agent Definition (IDENTICAL to pydanticai_impl.py)
# ============================================================================

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt="""You are a helpful weather assistant.

When users ask about weather, use the get_weather tool to fetch information.

Guidelines:
- Always confirm the location if it's ambiguous
- Ask about units preference if not specified
- Offer forecast if the user might find it helpful
- Be concise but informative

IMPORTANT: You maintain conversation context, so you can reference
previous weather queries in the same conversation.
"""
)


@agent.tool_plain
def get_weather(query: WeatherQuery) -> WeatherResponse:
    """
    Get weather information for a location.

    This is the SAME tool as in all other implementations.
    The only difference is it's now used in a stateful A2A context.
    """

    if not query.location or query.location.strip() == "":
        raise ValueError("Location cannot be empty")

    # ========================================================================
    # BUSINESS LOGIC - IDENTICAL TO ALL OTHER IMPLEMENTATIONS
    # ========================================================================

    temp = 72.0 if query.units == "fahrenheit" else 22.2

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
# FastA2A Server Setup
# ============================================================================

# Convert agent to A2A server (automatic infrastructure setup)
app = agent.to_a2a()

"""
What agent.to_a2a() does:
1. Creates Storage (in-memory by default, can use Redis/Postgres)
2. Creates Broker (in-memory by default, can use Redis/RabbitMQ)
3. Creates Worker (executes agent tasks)
4. Wraps agent in A2A protocol

The returned 'app' is an ASGI application (like FastAPI).
"""


# ============================================================================
# Running the Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Weather Service FastA2A Server")
    parser.add_argument("--port", type=int, default=8300, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    print("="*80)
    print("Weather Agent (FastA2A) - Stateful Agent with Task Queue")
    print("="*80)
    print(f"\nServer: http://{args.host}:{args.port}")
    print(f"Protocol: Agent-to-Agent (A2A)")
    print("\nCapabilities:")
    print("  - Stateful conversations (maintains context)")
    print("  - Asynchronous task queue")
    print("  - Multi-turn dialogues")
    print("  - Agent collaboration (multiple agents can share context)")
    print("\nStorage: In-memory (tasks/context cleared on restart)")
    print("Broker: In-memory (use Redis/RabbitMQ for production)")
    print("="*80 + "\n")

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
COMPARISON: FastAPI vs FastMCP vs PydanticAI vs FastA2A

┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Aspect       │ FastAPI      │ FastMCP      │ PydanticAI   │ FastA2A      │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ State        │ Stateless    │ Stateless    │ Stateless    │ ✓ Stateful   │
│ Protocol     │ HTTP REST    │ MCP          │ Direct calls │ A2A          │
│ Execution    │ Synchronous  │ Synchronous  │ Synchronous  │ Async queue  │
│ Memory       │ None         │ None         │ Per-call     │ ✓ Context    │
│ Multi-turn   │ ✗            │ ✗            │ ✗            │ ✓ Yes        │
│ Infrastructure│ Simple      │ Simple       │ Simple       │ ✓ Complex    │
│ Use Case     │ REST API     │ LLM tools    │ Agent tasks  │ Chatbots     │
│ Pydantic     │ ✓ SAME       │ ✓ SAME       │ ✓ SAME       │ ✓ SAME       │
│ Business Logic│ ✓ SAME      │ ✓ SAME       │ ✓ SAME       │ ✓ SAME       │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

RUNNING THE SERVER:

python examples/weather_service/fasta2a_impl.py --port 8300

This starts an A2A server with in-memory storage/broker.

TESTING WITH A2A CLIENT:

import httpx

# Create a conversation context
response = httpx.post("http://localhost:8300/contexts", json={})
context_id = response.json()["id"]

# Create first task in the conversation
task1 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "What's the weather in NYC?"}]
})
task1_id = task1.json()["id"]

# Poll for completion
result1 = httpx.get(f"http://localhost:8300/tasks/{task1_id}")
print(result1.json()["new_messages"])  # Agent response

# Continue conversation (context is preserved!)
task2 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,  # SAME context
    "messages": [{"role": "user", "content": "How about tomorrow?"}]
})

# Agent remembers we asked about NYC and can provide tomorrow's forecast

MULTI-TURN CONVERSATION EXAMPLE:

User: "What's the weather in NYC?"
Agent: [Uses get_weather tool] "It's 72°F and sunny in NYC."

User: "How about tomorrow?"
Agent: [Uses context, knows we're talking about NYC] "Tomorrow will be 74°F and partly cloudy."

User: "Thanks! What about London?"
Agent: [New location, uses get_weather again] "In London, it's 22°C and sunny."

All of this happens in ONE context_id, maintaining conversation state.

KEY INSIGHT:

FastA2A adds TWO major features:
1. Stateful Context: Conversations persist across tasks
2. Async Task Queue: Long-running workflows, background processing

The trade-off is infrastructure complexity:
- FastAPI/FastMCP: Single server, stateless, simple
- FastA2A: Storage + Broker + Worker, stateful, complex

Use FastA2A when you NEED conversation memory or async workflows.
Otherwise, stick with FastAPI (REST), FastMCP (MCP tools), or PydanticAI (direct agent).

PRODUCTION CONSIDERATIONS:

For production FastA2A deployments:
- Use Redis/Postgres for storage (not in-memory)
- Use Redis/RabbitMQ for broker (not in-memory)
- Deploy workers separately (horizontal scaling)
- Add monitoring/observability
- Implement context cleanup (old conversations)

Example with Redis:

from fasta2a import FastA2A, Worker
from fasta2a.storage import RedisStorage
from fasta2a.broker import RedisBroker

storage = RedisStorage(redis_url="redis://localhost:6379")
broker = RedisBroker(redis_url="redis://localhost:6379")
app = FastA2A(storage=storage, broker=broker)

COMPARISON TO CHATBOTS:

FastA2A is ideal for:
- Slack bots (multi-turn conversations)
- Discord bots (persistent context per channel)
- Customer support agents (conversation history)
- Multi-agent systems (agents collaborate on same context)

FastAPI/FastMCP is ideal for:
- Tool integrations (stateless function calls)
- Webhooks (one-shot requests)
- REST APIs (standard web services)
"""
