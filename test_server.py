"""Smoke test for the gmail-calendar MCP server over stdio."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_test() -> None:
    """Start gmail-calendar via uv, list tools, and call list_events(days_ahead=1)."""
    if not os.environ.get("GOOGLE_PRIVATE_DIR"):
        raise RuntimeError("Set GOOGLE_PRIVATE_DIR before running test_server.py.")

    project_dir = str(Path(__file__).resolve().parent)
    params = StdioServerParameters(
        command="uv",
        args=["--directory", project_dir, "run", "gmail-calendar"],
        env=dict(os.environ),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            init = await session.initialize()
            print(f"Connected to server: {init.serverInfo.name}")

            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            events_result = await session.call_tool("list_events", {"days_ahead": 1})
            print("\nlist_events(days_ahead=1) output:")
            print(f"isError={events_result.isError}")
            for item in events_result.content:
                text = getattr(item, "text", str(item))
                try:
                    print(json.dumps(json.loads(text), indent=2, ensure_ascii=False))
                except json.JSONDecodeError:
                    print(text)


if __name__ == "__main__":
    asyncio.run(run_test())
