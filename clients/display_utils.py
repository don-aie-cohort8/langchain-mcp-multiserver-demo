"""
Utility functions for displaying LangChain agent responses.
"""

from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def display_agent_response(
    response: Dict[str, Any],
    show_full_trace: bool = True,
    show_token_usage: bool = False,
    return_final_answer: bool = False
) -> Optional[str]:
    """
    Display formatted agent response with message trace.

    Args:
        response: Agent response dict with 'messages' key
        show_full_trace: If True, show all messages; if False, only final answer
        show_token_usage: If True, show token usage statistics for AI messages
        return_final_answer: If True, return the final answer text

    Returns:
        Final answer text if return_final_answer=True, else None

    Example:
        >>> response = await agent.ainvoke({"messages": "what is 5 + 3?"})
        >>> display_agent_response(response)

        >>> answer = display_agent_response(response, show_full_trace=False, return_final_answer=True)
        >>> print(f"Answer: {answer}")
    """
    messages = response.get("messages", [])
    final_answer = None

    if show_full_trace:
        print("\n" + "="*70)
        print("AGENT RESPONSE TRACE")
        print("="*70 + "\n")

    for i, msg in enumerate(messages, 1):
        msg_type = type(msg).__name__

        if isinstance(msg, AIMessage):
            # Check for tool calls
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                # Modern LangChain format
                tool_names = [tc['name'] for tc in msg.tool_calls]
                if show_full_trace:
                    print(f"{i:02d}. {msg_type} → 🔧 tool_call(s): {', '.join(tool_names)}")
            elif "tool_calls" in msg.additional_kwargs and msg.additional_kwargs["tool_calls"]:
                # Older format via additional_kwargs
                tools = msg.additional_kwargs["tool_calls"]
                tool_names = [t["function"]["name"] for t in tools]
                if show_full_trace:
                    print(f"{i:02d}. {msg_type} → 🔧 tool_call(s): {', '.join(tool_names)}")
            else:
                # Final answer
                final_answer = msg.content.strip()
                if show_full_trace:
                    print(f"{i:02d}. {msg_type}: {final_answer}")

            # Show token usage if requested
            if show_full_trace and show_token_usage and hasattr(msg, 'usage_metadata'):
                usage = msg.usage_metadata
                print(f"     └─ Tokens: input={usage.get('input_tokens', 0)}, "
                      f"output={usage.get('output_tokens', 0)}, "
                      f"total={usage.get('total_tokens', 0)}")

        elif isinstance(msg, ToolMessage):
            content = msg.content.strip()
            is_error = (hasattr(msg, 'status') and msg.status == 'error') or 'Error:' in content

            if show_full_trace:
                if is_error:
                    print(f"{i:02d}. {msg_type} [{msg.name}]: ❌ {content}")
                else:
                    print(f"{i:02d}. {msg_type} [{msg.name}]: ✓ {content}")

        elif isinstance(msg, HumanMessage):
            if show_full_trace:
                print(f"{i:02d}. {msg_type}: {msg.content.strip()}")
        else:
            # Other message types
            if show_full_trace:
                content = getattr(msg, 'content', str(msg))
                print(f"{i:02d}. {msg_type}: {content.strip() if hasattr(content, 'strip') else content}")

    if show_full_trace:
        print("\n" + "="*70 + "\n")
    elif final_answer:
        print(f"\n💡 Final Answer: {final_answer}\n")

    if return_final_answer:
        return final_answer


def get_final_answer(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract just the final answer from an agent response without printing.

    Args:
        response: Agent response dict with 'messages' key

    Returns:
        The final answer text, or None if no answer found

    Example:
        >>> response = await agent.ainvoke({"messages": "what is 5 + 3?"})
        >>> answer = get_final_answer(response)
        >>> print(answer)
        "8"
    """
    messages = response.get("messages", [])

    # Iterate in reverse to get the most recent AI message
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            # Check if this is a tool call or actual answer
            has_tool_calls = (
                (hasattr(msg, 'tool_calls') and msg.tool_calls) or
                ("tool_calls" in msg.additional_kwargs and msg.additional_kwargs["tool_calls"])
            )

            if not has_tool_calls and msg.content.strip():
                return msg.content.strip()

    return None


def print_tools_summary(tools: list) -> None:
    """
    Print a summary of available tools.

    Args:
        tools: List of LangChain tools

    Example:
        >>> tools = await client.get_tools()
        >>> print_tools_summary(tools)
    """
    print("\n" + "="*70)
    print(f"AVAILABLE TOOLS ({len(tools)} total)")
    print("="*70 + "\n")

    for i, tool in enumerate(tools, 1):
        name = tool.name if hasattr(tool, 'name') else str(tool)
        description = tool.description if hasattr(tool, 'description') else "No description"
        print(f"{i:02d}. {name}")
        print(f"    └─ {description}")

    print("\n" + "="*70 + "\n")
