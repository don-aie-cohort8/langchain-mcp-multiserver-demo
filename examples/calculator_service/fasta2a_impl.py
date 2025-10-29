"""
Calculator Service - FastA2A Implementation

This implementation shows how the SAME calculator service can be deployed as
a stateful agent using FastA2A (Agent-to-Agent Protocol), instead of
stateless REST/MCP or direct agent usage.

KEY DIFFERENCES FROM FastAPI/FastMCP/PydanticAI:
1. Stateful: Maintains conversation context across tasks
2. Task Queue: Asynchronous task processing with storage/broker
3. Agent Infrastructure: Requires storage + broker + worker
4. Multi-turn: Designed for ongoing conversations, not one-shot requests
5. Collaboration: Multiple agents can work on same context

WHAT STAYS THE SAME:
- Pydantic models (CalculationRequest, CalculationResponse) - IDENTICAL
- Tool definition (calculate function) - IDENTICAL
- Business logic - IDENTICAL
- Agent definition (same as pydanticai_impl.py)

NEW CONCEPTS:
- Storage: Persists tasks and conversation context
- Broker: Manages task queue (like Celery)
- Task model: Wraps agent work in async tasks
- Context: Conversation thread spanning multiple tasks

WHEN TO USE THIS:
- Multi-turn calculator sessions with memory
- Chatbots that remember previous calculations
- Educational tutoring bots (step-by-step math help)
- Collaborative calculation workflows

WHEN NOT TO USE THIS:
- Simple one-off calculations (use FastMCP)
- REST API (use FastAPI)
- Single calculation requests (use PydanticAI directly)
"""

import os
import argparse
from dotenv import load_dotenv
from pydantic_ai import Agent

# Import shared Pydantic models (SAME as all other implementations)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.models import CalculationRequest, CalculationResponse

load_dotenv()

# ============================================================================
# Agent Definition (IDENTICAL to pydanticai_impl.py)
# ============================================================================

agent = Agent(
    'openai:gpt-4o-mini',
    system_prompt="""You are a helpful calculator assistant with memory.

When users ask about mathematical calculations, use the calculate tool.

Guidelines:
- Parse user requests into appropriate operations
- Handle multiple calculations in sequence
- **Remember previous calculations** in the conversation
- Reference earlier results when relevant
- Help users understand multi-step problems
- Be precise with numerical results

IMPORTANT: You maintain conversation context, so you can reference
previous calculations and build on earlier results.
"""
)


@agent.tool_plain
def calculate(request: CalculationRequest) -> CalculationResponse:
    """
    Perform a mathematical calculation.

    This is the SAME tool as in all other implementations.
    The only difference is it's now used in a stateful A2A context.
    """

    if request.operation not in ["add", "subtract", "multiply", "divide"]:
        raise ValueError(f"Invalid operation: {request.operation}")

    # ========================================================================
    # BUSINESS LOGIC - IDENTICAL TO ALL OTHER IMPLEMENTATIONS
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

    parser = argparse.ArgumentParser(description="Calculator Service FastA2A Server")
    parser.add_argument("--port", type=int, default=8300, help="Port to run server on")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()

    print("="*80)
    print("Calculator Agent (FastA2A) - Stateful Agent with Task Queue")
    print("="*80)
    print(f"\nServer: http://{args.host}:{args.port}")
    print(f"Protocol: Agent-to-Agent (A2A)")
    print("\nCapabilities:")
    print("  - Stateful conversations (maintains context)")
    print("  - Asynchronous task queue")
    print("  - Multi-turn dialogues")
    print("  - Remembers previous calculations in conversation")
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
│ Use Case     │ REST API     │ LLM tools    │ Agent tasks  │ Calc tutor   │
│ Pydantic     │ ✓ SAME       │ ✓ SAME       │ ✓ SAME       │ ✓ SAME       │
│ Business Logic│ ✓ SAME      │ ✓ SAME       │ ✓ SAME       │ ✓ SAME       │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

RUNNING THE SERVER:

python examples/calculator_service/fasta2a_impl.py --port 8300

This starts an A2A server with in-memory storage/broker.

TESTING WITH A2A CLIENT:

import httpx

# Create a conversation context
response = httpx.post("http://localhost:8300/contexts", json={})
context_id = response.json()["id"]

# Task 1: First calculation
task1 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "Calculate 15 times 8"}]
})
task1_id = task1.json()["id"]

# Poll for completion
result1 = httpx.get(f"http://localhost:8300/tasks/{task1_id}")
print(result1.json()["new_messages"])  # Agent: "15 times 8 equals 120"

# Task 2: Reference previous result (context is preserved!)
task2 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,  # SAME context
    "messages": [{"role": "user", "content": "Now divide that by 4"}]
})

# Agent remembers "that" = 120 from previous task
# Result: "120 divided by 4 equals 30"

# Task 3: Another follow-up
task3 = httpx.post("http://localhost:8300/tasks", json={
    "context_id": context_id,
    "messages": [{"role": "user", "content": "And add 12 to that"}]
})

# Agent remembers "that" = 30 from task 2
# Result: "30 plus 12 equals 42"

MULTI-TURN CONVERSATION EXAMPLE:

User: "Calculate 50 plus 30"
Agent: [Uses calculate tool] "50 plus 30 equals 80."

User: "Now divide that by 4"
Agent: [Knows "that" = 80 from context] [Uses calculate tool] "80 divided by 4 equals 20."

User: "What was my first calculation?"
Agent: [References conversation context] "Your first calculation was 50 plus 30, which equaled 80."

User: "Multiply the final result by 2"
Agent: [Knows final result = 20] [Uses calculate tool] "20 multiplied by 2 equals 40."

All of this happens in ONE context_id, maintaining full conversation state.

KEY INSIGHT:

FastA2A adds TWO major features:
1. Stateful Context: Calculations and conversation persist across tasks
2. Async Task Queue: Long-running computations, background processing

The trade-off is infrastructure complexity:
- FastAPI/FastMCP: Single server, stateless, simple
- FastA2A: Storage + Broker + Worker, stateful, complex

Use FastA2A when you NEED conversation memory or multi-step workflows.
Otherwise, stick with FastAPI (REST), FastMCP (MCP tools), or PydanticAI (direct agent).

USE CASES FOR FastA2A:

1. Math Tutoring Bot:
   User: "What's 7 times 8?"
   Bot: "56! Want to try another?"
   User: "What's that minus 14?"  # Bot remembers 56
   Bot: "56 minus 14 equals 42!"

2. Spreadsheet Calculator:
   User: "Calculate cell A1: 100 + 50"
   Bot: "Cell A1 = 150"
   User: "Calculate cell A2: A1 times 2"  # Bot remembers A1 = 150
   Bot: "Cell A2 = 300"

3. Recipe Scaling:
   User: "I need 3 cups times 1.5"
   Bot: "That's 4.5 cups"
   User: "And 2 teaspoons times the same"  # Bot remembers 1.5
   Bot: "That's 3 teaspoons"

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
"""
