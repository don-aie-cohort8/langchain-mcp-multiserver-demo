#!/bin/bash
#
# Minimal Test Orchestrator
#
# Runs all minimal tests in sequence:
# 1. Pydantic models (no server needed)
# 2. FastAPI (starts/stops server)
# 3. FastMCP (starts/stops server)
# 4. PydanticAI (no server needed)
# 5. FastA2A (starts/stops server)
#
# Total time: ~6 minutes

set -e  # Exit on first error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Minimal Test Suite for FastAPI/FastMCP/PydanticAI/FastA2A ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$PROJECT_ROOT"

# Test 1: Pydantic Models (no server needed)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1/5: Pydantic Models"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python tests/test_models_minimal.py
echo ""

# Test 2: FastAPI
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2/5: FastAPI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash tests/test_fastapi_minimal.sh
echo ""

# Test 3: FastMCP
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3/5: FastMCP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Start FastMCP server
python examples/calculator_service/fastmcp_impl.py --port 8100 &
FASTMCP_PID=$!
echo "Started FastMCP server (PID: $FASTMCP_PID)"
sleep 2

# Run test
python tests/test_fastmcp_minimal.py

# Cleanup
kill $FASTMCP_PID
wait $FASTMCP_PID 2>/dev/null || true
echo ""

# Test 4: PydanticAI (no server needed)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4/5: PydanticAI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python tests/test_pydanticai_minimal.py
echo ""

# Test 5: FastA2A
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5/5: FastA2A"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Start FastA2A server
python examples/calculator_service/fasta2a_impl.py --port 8300 &
FASTA2A_PID=$!
echo "Started FastA2A server (PID: $FASTA2A_PID)"
sleep 3  # A2A needs more startup time

# Run test
python tests/test_fasta2a_minimal.py

# Cleanup
kill $FASTA2A_PID
wait $FASTA2A_PID 2>/dev/null || true
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ALL TESTS PASSED! ✓                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Test Summary:"
echo "  ✓ Pydantic Models - Framework-agnostic validation"
echo "  ✓ FastAPI - REST API with curl"
echo "  ✓ FastMCP - MCP protocol with tool discovery"
echo "  ✓ PydanticAI - Natural language agent"
echo "  ✓ FastA2A - Stateful conversation with context"
echo ""
echo "All educational patterns validated successfully!"
