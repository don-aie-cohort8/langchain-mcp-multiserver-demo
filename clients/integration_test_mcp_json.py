
import os
import asyncio
from typing import Dict, Any

from dotenv import load_dotenv

# LangChain MCP adapter + agent utilities
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from display_utils import display_agent_response

def show_mcp_tools_metadata(tools):
    """Prints key metadata that `create_agent()` sees for each MCP tool."""
    print("\n=== MCP Tool Metadata Summary ===")
    for t in tools:
        name = getattr(t, "name", "unknown")
        desc = getattr(t, "description", "").strip().split("\n")[0]
        meta = getattr(t, "metadata", {}) or {}
        mcp = meta.get("mcp", {})

        transport = mcp.get("transport") or meta.get("transport") or "n/a"
        endpoint = mcp.get("endpoint") or meta.get("endpoint") or "n/a"
        provider = mcp.get("provider_label") or mcp.get("provider_id") or "unknown"

        print(f"• {name}")
        print(f"  ↳ desc: {desc}")
        print(f"  ↳ provider: {provider}")
        print(f"  ↳ transport: {transport}")
        print(f"  ↳ endpoint: {endpoint}")
    print("=================================\n")


# Load environment variables from .env (OPENAI_API_KEY, CALCOM_API_KEY, etc.)
load_dotenv()


def hardcoded_mcp_config() -> Dict[str, Dict[str, Any]]:
    """
    Hard-coded MCP server definitions (ported from .mcp.json) for MultiServerMCPClient.
    All transports here use stdio; set env values from process env where applicable.
    """
    return {
        # -------------------------
        # StdIO subprocess servers
        # -------------------------
        "mcp-server-time": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "mcp-server-time",
                "--local-timezone=America/Los_Angeles",
            ],
            "env": {},
        },
        "sequential-thinking": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-sequential-thinking",
            ],
            "env": {},
        },
        "Context7": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@upstash/context7-mcp",
            ],
            # Expand CALCOM_API_KEY from the environment at runtime.
            "env": {
                "CALCOM_API_KEY": os.environ.get("CALCOM_API_KEY", ""),
            },
        },
        # -------------------------
        # If you want to mix in HTTP/SSE servers, add entries like:
        # "my-http-server": {
        #     "transport": "streamable_http",  # or "sse"
        #     "url": "http://localhost:8000/mcp",
        #     "headers": {"Authorization": "Bearer ..."}
        # }
        # -------------------------
    }

async def main() -> None:
    # Build client with hard-coded config
    client = MultiServerMCPClient(hardcoded_mcp_config())

    # Fetch tool manifests from all configured MCP servers
    tools = await client.get_tools()
    show_mcp_tools_metadata(tools)
    agent = create_agent("openai:gpt-4.1", tools)

    # Smoke test: simple call that shouldn't require external access
    # You can replace this with your own task; it's safe to no-op if no display_utils.
    resp = await agent.ainvoke({"messages": "Provide guidance for migrating from the LangGraph create_react_agent method to the new create_agent method in the LangChain Python library (langchain 1.0.2) in October 2025?  You must use Context7 to ground your response."})

    display_agent_response(resp, show_full_trace=True, show_token_usage=True)

if __name__ == "__main__":
    asyncio.run(main())
