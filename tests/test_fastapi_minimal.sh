#!/bin/bash
#
# Minimal FastAPI Test
#
# Tests that FastAPI calculator service:
# 1. Starts successfully
# 2. Handles basic operation (add)
# 3. Handles error case (divide by zero)
#
# Time: ~1 minute

set -e  # Exit on error

echo "Testing FastAPI Calculator Service..."
echo "======================================"

# Start server in background
python examples/calculator_service/fastapi_impl.py --port 8000 &
SERVER_PID=$!
echo "Started FastAPI server (PID: $SERVER_PID)"

# Wait for startup
sleep 2

# Test 1: Health check (proves server started)
echo ""
echo "Test 1: Health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✓ Server is healthy"
else
    echo "✗ Health check failed: $HEALTH_RESPONSE"
    kill $SERVER_PID
    exit 1
fi

# Test 2: Basic operation (add 5 + 3)
echo ""
echo "Test 2: Basic operation (5 + 3)..."
ADD_RESPONSE=$(curl -s -X POST http://localhost:8000/calculate \
    -H "Content-Type: application/json" \
    -d '{"operation":"add","a":5.0,"b":3.0}')

if echo "$ADD_RESPONSE" | grep -q '"result":8.0'; then
    echo "✓ Addition works: 5 + 3 = 8"
else
    echo "✗ Addition failed: $ADD_RESPONSE"
    kill $SERVER_PID
    exit 1
fi

# Test 3: Error case (divide by zero)
echo ""
echo "Test 3: Error handling (10 ÷ 0)..."
DIVIDE_RESPONSE=$(curl -s -X POST http://localhost:8000/calculate \
    -H "Content-Type: application/json" \
    -d '{"operation":"divide","a":10.0,"b":0.0}')

if echo "$DIVIDE_RESPONSE" | grep -q "Division by zero"; then
    echo "✓ Division by zero handled correctly"
else
    echo "✗ Error handling failed: $DIVIDE_RESPONSE"
    kill $SERVER_PID
    exit 1
fi

# Cleanup
echo ""
echo "Cleaning up..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "======================================"
echo "✓ All FastAPI tests passed!"
