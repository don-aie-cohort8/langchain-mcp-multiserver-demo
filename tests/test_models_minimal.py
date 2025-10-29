#!/usr/bin/env python3
"""
Minimal Pydantic Model Validation Test

Tests that shared Pydantic models work correctly across all frameworks.
This is framework-agnostic - just validates the models themselves.

Time: ~30 seconds
"""

import sys
from pathlib import Path

# Add examples to path
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

from common.models import CalculationRequest, CalculationResponse
from pydantic import ValidationError


def test_valid_request():
    """Test valid calculation request instantiation."""
    req = CalculationRequest(operation="add", a=5.0, b=3.0)
    assert req.operation == "add"
    assert req.a == 5.0
    assert req.b == 3.0
    print("✓ Valid request model")


def test_valid_response_success():
    """Test valid response model (success case)."""
    resp = CalculationResponse(
        operation="add",
        operands=[5.0, 3.0],
        result=8.0,
        error=None
    )
    assert resp.result == 8.0
    assert resp.error is None
    print("✓ Valid response model (success)")


def test_valid_response_error():
    """Test valid response model (error case)."""
    resp_err = CalculationResponse(
        operation="divide",
        operands=[10.0, 0.0],
        result=None,
        error="Division by zero is not allowed"
    )
    assert resp_err.result is None
    assert resp_err.error is not None
    print("✓ Valid response model (error)")


def test_invalid_operation():
    """Test Pydantic validation rejects invalid operation."""
    try:
        CalculationRequest(operation="invalid", a=1.0, b=2.0)
        assert False, "Should have raised ValidationError"
    except ValidationError:
        print("✓ Pydantic validation works (invalid operation rejected)")


def test_serialization():
    """Test JSON serialization works."""
    req = CalculationRequest(operation="multiply", a=7.0, b=6.0)
    json_str = req.model_dump_json()
    assert "multiply" in json_str
    assert "7.0" in json_str
    print("✓ JSON serialization works")


if __name__ == "__main__":
    print("Testing Pydantic Models...")
    print("-" * 50)

    test_valid_request()
    test_valid_response_success()
    test_valid_response_error()
    test_invalid_operation()
    test_serialization()

    print("-" * 50)
    print("✓ All model tests passed!")
