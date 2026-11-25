"""FastMCP server exposing read-only/draft/create Gmail and Calendar tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from . import calendar_tools, gmail_tools

mcp = FastMCP("gmail-calendar")


@mcp.tool(
    description="Search Gmail messages by query string and return matching message summaries."
)
def search_emails(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search Gmail messages matching the given query."""
    return gmail_tools.search_emails(query=query, max_results=max_results)


@mcp.tool(description="Read the full headers and body of a Gmail message by message ID.")
def read_email(message_id: str) -> dict[str, Any]:
    """Read a single email by its Gmail message ID."""
    return gmail_tools.read_email(message_id=message_id)


@mcp.tool(
    description=(
        "Create a Gmail draft without sending it. If 'to' is empty or 'me', "
        "resolves to the authenticated user's email address."
    )
)
def create_draft(to: str, subject: str, body: str) -> dict[str, Any]:
    """Create an email draft in Gmail (never sends)."""
    return gmail_tools.create_draft(to=to, subject=subject, body=body)


@mcp.tool(
    description="List upcoming Google Calendar events for the next N days in Asia/Jerusalem time."
)
def list_events(days_ahead: int = 7) -> list[dict[str, Any]]:
    """List upcoming events from the primary Google Calendar."""
    return calendar_tools.list_events(days_ahead=days_ahead)


@mcp.tool(
    description=(
        "Find free time slots of at least duration_minutes on a YYYY-MM-DD date "
        "(08:00-20:00 Asia/Jerusalem)."
    )
)
def find_free_slots(date: str, duration_minutes: int = 30) -> dict[str, Any]:
    """Find free slots on the given date in Asia/Jerusalem time."""
    return calendar_tools.find_free_slots(
        date=date, duration_minutes=duration_minutes
    )


@mcp.tool(
    description=(
        "Create a new Google Calendar event using ISO-8601 start and end times "
        "(defaults to Asia/Jerusalem)."
    )
)
def create_event(
    title: str, start: str, end: str, description: str = ""
) -> dict[str, Any]:
    """Create an event on the primary Google Calendar."""
    return calendar_tools.create_event(
        title=title, start=start, end=end, description=description
    )


def main() -> None:
    """Run the gmail-calendar MCP server over stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
