"""
Shared Pydantic models for educational examples.

These models are designed to work identically across:
- FastAPI (REST endpoints)
- FastMCP (MCP servers)
- PydanticAI (agent tools)
- FastA2A (agent-to-agent tasks)

Key principle: Define domain models once, use everywhere.

The models in this file have NO framework-specific dependencies.
They are pure domain models that leverage Pydantic's validation,
serialization, and schema generation capabilities.
"""

from pydantic import BaseModel, Field
from typing import Literal


# ============================================================================
# Weather Service Models
# ============================================================================


class WeatherQuery(BaseModel):
    """
    Weather lookup parameters.

    This model works identically in:
    - FastAPI: Request body parameter
    - FastMCP: Tool parameter (automatically unpacked)
    - PydanticAI: Agent tool parameter
    - FastA2A: Task payload
    """

    location: str = Field(
        description="City name (e.g., 'NYC', 'London') or coordinates (e.g., '40.7,-74.0')",
        examples=["NYC", "London", "Tokyo", "40.7128,-74.0060"]
    )
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature units for the response"
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 3-day forecast in response"
    )


class WeatherForecast(BaseModel):
    """
    Single day forecast entry.

    Nested model used in WeatherResponse.
    """

    day: str = Field(
        description="Day label",
        examples=["Tomorrow", "Day 2", "Day 3"]
    )
    temp: float = Field(
        description="Forecasted temperature in specified units"
    )
    conditions: str = Field(
        description="Weather conditions",
        examples=["Sunny", "Partly Cloudy", "Rainy", "Cloudy"]
    )


class WeatherResponse(BaseModel):
    """
    Weather information response.

    This model works identically as:
    - FastAPI: response_model parameter
    - FastMCP: Return type annotation
    - PydanticAI: Tool return type
    - FastA2A: Task result
    """

    location: str = Field(description="Location that was queried")
    current_temp: float = Field(description="Current temperature")
    units: str = Field(description="Temperature units used")
    conditions: str = Field(
        description="Current weather conditions",
        examples=["Sunny", "Cloudy", "Rainy"]
    )
    forecast: list[WeatherForecast] | None = Field(
        default=None,
        description="Optional 3-day forecast (only if requested)"
    )


# ============================================================================
# Calculator Service Models
# ============================================================================


class CalculationRequest(BaseModel):
    """
    Calculation parameters.

    This model demonstrates:
    - Enum-like literal types (operation)
    - Multiple numeric parameters
    - Automatic validation (Pydantic ensures types match)
    """

    operation: Literal["add", "subtract", "multiply", "divide"] = Field(
        description="Math operation to perform"
    )
    a: float = Field(description="First operand")
    b: float = Field(description="Second operand")


class CalculationResponse(BaseModel):
    """
    Calculation result.

    This model demonstrates:
    - Handling both success and error states
    - Optional fields (result can be None if error)
    - Clear error messaging
    """

    operation: str = Field(description="Operation that was performed")
    operands: list[float] = Field(description="Input values used")
    result: float | None = Field(
        default=None,
        description="Calculation result (None if error occurred)"
    )
    error: str | None = Field(
        default=None,
        description="Error message if operation failed (e.g., division by zero)"
    )


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    """
    Demonstrate that these models work independently of any framework.
    """

    # Example 1: Weather query with validation
    weather_query = WeatherQuery(
        location="NYC",
        units="fahrenheit",
        include_forecast=True
    )
    print("Weather Query:", weather_query.model_dump_json(indent=2))

    # Example 2: Weather response with nested forecast
    weather_response = WeatherResponse(
        location="NYC",
        current_temp=72.5,
        units="fahrenheit",
        conditions="Sunny",
        forecast=[
            WeatherForecast(day="Tomorrow", temp=74.0, conditions="Partly Cloudy"),
            WeatherForecast(day="Day 2", temp=71.0, conditions="Sunny"),
            WeatherForecast(day="Day 3", temp=68.0, conditions="Cloudy")
        ]
    )
    print("\nWeather Response:", weather_response.model_dump_json(indent=2))

    # Example 3: Calculator request
    calc_request = CalculationRequest(
        operation="add",
        a=5.0,
        b=3.0
    )
    print("\nCalculation Request:", calc_request.model_dump_json(indent=2))

    # Example 4: Calculator response (success)
    calc_response_success = CalculationResponse(
        operation="add",
        operands=[5.0, 3.0],
        result=8.0,
        error=None
    )
    print("\nCalculation Response (Success):", calc_response_success.model_dump_json(indent=2))

    # Example 5: Calculator response (error)
    calc_response_error = CalculationResponse(
        operation="divide",
        operands=[5.0, 0.0],
        result=None,
        error="Division by zero is not allowed"
    )
    print("\nCalculation Response (Error):", calc_response_error.model_dump_json(indent=2))

    # Example 6: Schema generation (same schemas used by all frameworks)
    print("\n" + "="*80)
    print("JSON Schema for WeatherQuery (used by FastAPI, FastMCP, etc.):")
    print("="*80)
    import json
    print(json.dumps(WeatherQuery.model_json_schema(), indent=2))
