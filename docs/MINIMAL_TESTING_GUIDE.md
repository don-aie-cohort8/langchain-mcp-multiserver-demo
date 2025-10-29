# Minimal Testing Guide

**Philosophy:** Test only what's essential to validate the educational patterns. No comprehensive coverage, no security testing, no edge cases—just prove the concept works.

**Total Time:** ~6 minutes for all tests

---

## Quick Start

```bash
# Run all tests at once
./tests/run_all_tests.sh

# Or run individually
python tests/test_models_minimal.py
bash tests/test_fastapi_minimal.sh
python tests/test_fastmcp_minimal.py
python tests/test_pydanticai_minimal.py
python tests/test_fasta2a_minimal.py
```

---

## Test Overview

| Test | What It Validates | Time | Server Needed? |
|------|-------------------|------|----------------|
| Pydantic Models | Shared models work correctly | 30s | No |
| FastAPI | REST API basics | 1min | Yes (auto-started) |
| FastMCP | MCP tool discovery & invocation | 2min | Yes (auto-started) |
| PydanticAI | Natural language → tool calls | 1min | No |
| FastA2A | Stateful conversation | 1.5min | Yes (auto-started) |

---

## Individual Test Details

### 1. Pydantic Models (`test_models_minimal.py`)

**Purpose:** Validate shared Pydantic models work framework-agnostic

**Tests:**
- Valid request model instantiation
- Valid response model (success case)
- Valid response model (error case)
- Invalid operation rejected by Pydantic validation
- JSON serialization works

**Run:**
```bash
python tests/test_models_minimal.py
```

**Expected Output:**
```
Testing Pydantic Models...
--------------------------------------------------
✓ Valid request model
✓ Valid response model (success)
✓ Valid response model (error)
✓ Pydantic validation works (invalid operation rejected)
✓ JSON serialization works
--------------------------------------------------
✓ All model tests passed!
```

**Validates:** Core Pydantic models (`CalculationRequest`, `CalculationResponse`) used across all frameworks

---

### 2. FastAPI (`test_fastapi_minimal.sh`)

**Purpose:** Validate FastAPI REST API basics

**Tests:**
- Health check (server started)
- Basic operation: 5 + 3 = 8
- Error case: 10 ÷ 0 returns error message

**Run:**
```bash
bash tests/test_fastapi_minimal.sh
```

**Expected Output:**
```
Testing FastAPI Calculator Service...
======================================
Started FastAPI server (PID: 12345)

Test 1: Health check...
✓ Server is healthy

Test 2: Basic operation (5 + 3)...
✓ Addition works: 5 + 3 = 8

Test 3: Error handling (10 ÷ 0)...
✓ Division by zero handled correctly

Cleaning up...
======================================
✓ All FastAPI tests passed!
```

**Validates:** HTTP REST endpoints with Pydantic request/response models

---

### 3. FastMCP (`test_fastmcp_minimal.py`)

**Purpose:** Validate MCP protocol tool discovery and invocation

**Prerequisites:**
```bash
# Start FastMCP server in another terminal
python examples/calculator_service/fastmcp_impl.py --port 8100
```

**Tests:**
- Tool discovery (list_tools returns calculate)
- Basic operation: 5 + 3 = 8
- Error case: 10 ÷ 0 returns error message

**Run:**
```bash
python tests/test_fastmcp_minimal.py
```

**Expected Output:**
```
Testing FastMCP Calculator Service...
==================================================

Test 1: Tool discovery...
✓ Discovered 1 tool(s)
✓ Found tool: calculate

Test 2: Basic operation (5 + 3)...
✓ Addition works: 5 + 3 = 8.0

Test 3: Error handling (10 ÷ 0)...
✓ Division by zero handled: Division by zero is not allowed

==================================================
✓ All FastMCP tests passed!
```

**Validates:** MCP protocol with MultiServerMCPClient integration

---

### 4. PydanticAI (`test_pydanticai_minimal.py`)

**Purpose:** Validate AI agent can parse natural language and use tools

**Prerequisites:**
- Set `OPENAI_API_KEY` in `.env`

**Tests:**
- Natural language: "What is 5 plus 3?"
- Explicit calculation: "Calculate 42 multiplied by 7"
- Error case: "Divide 10 by 0"

**Run:**
```bash
python tests/test_pydanticai_minimal.py
```

**Expected Output:**
```
Testing PydanticAI Calculator Agent...
==================================================

Test 1: Natural language (What is 5 plus 3?)...
✓ Natural language works: '5 plus 3 equals 8.'

Test 2: Explicit calculation (42 × 7)...
✓ Multiplication works: '42 multiplied by 7 equals 294.'

Test 3: Error handling (10 ÷ 0)...
✓ Error handling works: 'I cannot divide 10 by 0 because division by zero is not allowed.'

==================================================
✓ All PydanticAI tests passed!
```

**Validates:** Agent reasoning with tool invocation

---

### 5. FastA2A (`test_fasta2a_minimal.py`)

**Purpose:** Validate stateful conversation with context persistence

**Prerequisites:**
```bash
# Start FastA2A server in another terminal
python examples/calculator_service/fasta2a_impl.py --port 8300
```

- Set `OPENAI_API_KEY` in `.env`

**Tests:**
- Context creation
- First calculation: 15 × 8 = 120
- Second calculation with context: "divide that by 4" (agent remembers 120 → 30)

**Run:**
```bash
python tests/test_fasta2a_minimal.py
```

**Expected Output:**
```
Testing FastA2A Calculator Agent...
==================================================

Test 1: Create conversation context...
✓ Context created: ctx_abc123

Test 2: First calculation (15 × 8)...
  Task created: task_xyz456
  Task completed in 2 seconds
✓ First calculation works: 15 × 8 = 120

Test 3: Context persistence (divide that by 4)...
  Task created: task_def789
  Task completed in 2 seconds
✓ Context persistence works: Agent remembered 120, calculated 120 ÷ 4 = 30

==================================================
✓ All FastA2A tests passed!
```

**Validates:** Stateful conversation context across multiple tasks

---

## Running All Tests Together

Use the orchestrator script:

```bash
./tests/run_all_tests.sh
```

**What it does:**
1. Runs Pydantic model tests (no server)
2. Starts FastAPI server → runs tests → stops server
3. Starts FastMCP server → runs tests → stops server
4. Runs PydanticAI tests (no server)
5. Starts FastA2A server → runs tests → stops server

**Expected Output:**
```
╔════════════════════════════════════════════════════════════╗
║  Minimal Test Suite for FastAPI/FastMCP/PydanticAI/FastA2A ║
╚════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 1/5: Pydantic Models
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... model test output ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 2/5: FastAPI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... FastAPI test output ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 3/5: FastMCP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... FastMCP test output ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 4/5: PydanticAI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... PydanticAI test output ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 5/5: FastA2A
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[... FastA2A test output ...]

╔════════════════════════════════════════════════════════════╗
║                    ALL TESTS PASSED! ✓                     ║
╚════════════════════════════════════════════════════════════╝

Test Summary:
  ✓ Pydantic Models - Framework-agnostic validation
  ✓ FastAPI - REST API with curl
  ✓ FastMCP - MCP protocol with tool discovery
  ✓ PydanticAI - Natural language agent
  ✓ FastA2A - Stateful conversation with context

All educational patterns validated successfully!
```

---

## Troubleshooting

### "Port already in use"

**Problem:** Server won't start because port is occupied

**Solution:**
```bash
# Find process using port 8100
lsof -i :8100

# Kill it
kill -9 <PID>
```

### "No tools discovered" (FastMCP)

**Problem:** FastMCP server not running or wrong port

**Solution:**
```bash
# Make sure server is running on correct port
python examples/calculator_service/fastmcp_impl.py --port 8100

# Check server is accessible
curl http://localhost:8100/mcp
```

### "OPENAI_API_KEY not set"

**Problem:** PydanticAI and FastA2A tests need OpenAI API key

**Solution:**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your key
OPENAI_API_KEY=sk-...
```

### "Context creation failed" (FastA2A)

**Problem:** FastA2A server not fully started or crashed

**Solution:**
```bash
# Restart server and wait longer for startup
python examples/calculator_service/fasta2a_impl.py --port 8300
sleep 5  # A2A needs more startup time

# Check server logs for errors
```

### Tests hang or timeout

**Problem:** Server process didn't start or crashed

**Solution:**
```bash
# Check if processes are running
ps aux | grep python

# Kill any hung processes
pkill -f "calculator_service"

# Restart tests
```

---

## What These Tests DON'T Cover

This is intentional - we're validating educational concepts, not building production-ready software.

**Not Tested:**
- Security (authentication, authorization, rate limiting)
- Performance (load testing, concurrency, latency)
- Edge cases (extreme values, Unicode, special characters, malformed input)
- Network failures (timeouts, retries, circuit breakers)
- Complex workflows (multi-step calculations, conditional logic)
- Database persistence (for FastA2A production scenarios)
- Production infrastructure (Redis broker, Postgres storage)
- Cross-framework integration (e.g., PydanticAI calling FastMCP tools)

**Why Not:**
- Educational focus: Prove the pattern works
- Time-boxed: ~6 minutes total
- Parsimonious: Only test essentials
- Effective: Validate core concepts, not comprehensive coverage

---

## Test Philosophy

### What We Test

1. **Service Lifecycle** - Does it start? Does it respond?
2. **Core Functionality** - Basic operation works (5 + 3 = 8)
3. **Error Handling** - One error case works (divide by zero)
4. **Framework-Specific Features**
   - FastAPI: HTTP REST
   - FastMCP: MCP tool discovery
   - PydanticAI: Natural language
   - FastA2A: Stateful context

### What We Validate

- Pydantic models work identically across all frameworks
- Business logic is portable (same calculation code)
- Only decorators and protocols change
- Error handling is consistent

### Success Criteria

✓ All services start successfully
✓ Basic operations return correct results
✓ Error cases are handled gracefully
✓ Pydantic validation works
✓ Framework-specific features work (tool discovery, context, etc.)

---

## Files

```
tests/
├── test_models_minimal.py       # Pydantic model validation
├── test_fastapi_minimal.sh      # FastAPI REST API tests
├── test_fastmcp_minimal.py      # FastMCP MCP protocol tests
├── test_pydanticai_minimal.py   # PydanticAI agent tests
├── test_fasta2a_minimal.py      # FastA2A stateful agent tests
└── run_all_tests.sh             # Orchestrator (runs all tests)
```

---

## See Also

- [Examples README](../examples/README.md) - Educational examples overview
- [Calculator Service README](../examples/calculator_service/README.md) - Implementation comparison
- [MCP vs A2A Decision Guide](MCP_VS_A2A_DECISION_GUIDE.md) - When to use which

---

**Document Version:** 1.0
**Last Updated:** October 2025
**Author:** AIE Cohort 8 Educational Materials
