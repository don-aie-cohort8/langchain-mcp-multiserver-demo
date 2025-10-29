#!/usr/bin/env python3
"""
Minimal FastA2A Test

Tests that FastA2A calculator agent:
1. Can create conversation contexts
2. Executes tasks successfully
3. Maintains context across multiple tasks (stateful)

Prerequisites: FastA2A server must be running
  python examples/calculator_service/fasta2a_impl.py --port 8300

Time: ~1.5 minutes (includes waiting for task completion)
"""

import asyncio
import sys
import httpx


async def test_fasta2a():
    print("Testing FastA2A Calculator Agent...")
    print("=" * 50)

    base_url = "http://localhost:8300"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Create context (proves server started)
        print("\nTest 1: Create conversation context...")
        try:
            ctx_resp = await client.post(f"{base_url}/contexts", json={})
            assert ctx_resp.status_code == 200, f"Context creation failed: {ctx_resp.status_code}"
            context_id = ctx_resp.json()["id"]
            print(f"✓ Context created: {context_id}")
        except Exception as e:
            print(f"✗ Failed to create context: {e}")
            raise

        # Test 2: First calculation (15 × 8 = 120)
        print("\nTest 2: First calculation (15 × 8)...")
        task1 = await client.post(f"{base_url}/tasks", json={
            "context_id": context_id,
            "messages": [{"role": "user", "content": "Calculate 15 times 8"}]
        })
        task1_id = task1.json()["id"]
        print(f"  Task created: {task1_id}")

        # Poll for completion (max 10 seconds)
        for attempt in range(10):
            await asyncio.sleep(1)
            result = await client.get(f"{base_url}/tasks/{task1_id}")
            task1_data = result.json()

            if task1_data.get("state") == "completed":
                print(f"  Task completed in {attempt + 1} seconds")
                break
        else:
            raise TimeoutError("Task 1 did not complete within 10 seconds")

        # Verify result contains 120
        response_text = str(task1_data.get("new_messages", ""))
        assert "120" in response_text, f"Expected '120' in response, got: {response_text}"
        print(f"✓ First calculation works: 15 × 8 = 120")

        # Test 3: Context persistence (divide that by 4)
        print("\nTest 3: Context persistence (divide that by 4)...")
        task2 = await client.post(f"{base_url}/tasks", json={
            "context_id": context_id,  # SAME context
            "messages": [{"role": "user", "content": "Now divide that by 4"}]
        })
        task2_id = task2.json()["id"]
        print(f"  Task created: {task2_id}")

        # Poll for completion
        for attempt in range(10):
            await asyncio.sleep(1)
            result = await client.get(f"{base_url}/tasks/{task2_id}")
            task2_data = result.json()

            if task2_data.get("state") == "completed":
                print(f"  Task completed in {attempt + 1} seconds")
                break
        else:
            raise TimeoutError("Task 2 did not complete within 10 seconds")

        # Verify result contains 30 (agent remembered 120 from context)
        response_text = str(task2_data.get("new_messages", ""))
        assert "30" in response_text, \
            f"Expected '30' in response (agent should remember 120), got: {response_text}"
        print(f"✓ Context persistence works: Agent remembered 120, calculated 120 ÷ 4 = 30")

    print("\n" + "=" * 50)
    print("✓ All FastA2A tests passed!")


if __name__ == "__main__":
    try:
        asyncio.run(test_fasta2a())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        print("\nMake sure FastA2A server is running:")
        print("  python examples/calculator_service/fasta2a_impl.py --port 8300")
        print("\nAlso ensure OPENAI_API_KEY is set in .env")
        sys.exit(1)
