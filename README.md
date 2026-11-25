# gmail-calendar MCP Server

A Python MCP server built with the official MCP Python SDK (`FastMCP`) and `uv` over `stdio` transport. It provides safe Gmail and Google Calendar tools in the `Asia/Jerusalem` timezone without any send or delete capabilities.

## Exposed Tools

1. `search_emails(query, max_results)` — Search Gmail messages by query string and return matching message summaries.
2. `read_email(message_id)` — Read the full headers and body of a Gmail message by message ID.
3. `create_draft(to, subject, body)` — Create a Gmail **draft only** (never sends). When `to` is empty or `"me"`, automatically resolves to the authenticated user's email address via `users().getProfile(userId="me")`.
4. `list_events(days_ahead)` — List upcoming Google Calendar events for the next `days_ahead` days (`Asia/Jerusalem`).
5. `find_free_slots(date, duration_minutes)` — Find free time slots of at least `duration_minutes` on a `YYYY-MM-DD` date (`08:00–20:00 Asia/Jerusalem`).
6. `create_event(title, start, end, description)` — Create a new Google Calendar event using ISO-8601 `start` and `end` timestamps (defaulting naive timestamps to `Asia/Jerusalem`).

## Security & Credential Handling

- Credentials (`client_secret*.json` and `token.json`) are **never copied** into this repository.
- The server reads the external credential folder path from the `GOOGLE_PRIVATE_DIR` environment variable (and optionally `.env` via `python-dotenv`, which is gitignored).
- The server **never prints secrets** and **never opens a browser**. If `token.json` is expired and has a `refresh_token`, it refreshes silently; otherwise it fails with an error message.
- No tool sends emails or deletes emails/drafts/events.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed.
- An existing `GOOGLE_PRIVATE_DIR` directory containing `client_secret*.json` and a pre-authorized `token.json` with Gmail and Calendar scopes.

## Setup & Running

1. Install dependencies:
   ```powershell
   uv sync
   ```

2. Set `GOOGLE_PRIVATE_DIR` to the folder containing your Google OAuth files:
   ```powershell
   $env:GOOGLE_PRIVATE_DIR = "C:\Users\Shira\Documents\Uni\שנה 'ג\בינה מלאכותית יוצרת"
   ```
   *(Alternatively, place `GOOGLE_PRIVATE_DIR=...` in a local `.env` file, which is excluded by `.gitignore`.)*

3. Run the MCP server over `stdio`:
   ```powershell
   uv run gmail-calendar
   ```
   Or from another directory:
   ```powershell
   uv --directory C:\BIU01\L06 run gmail-calendar
   ```

## Example MCP Client Configuration

```json
{
  "mcpServers": {
    "gmail-calendar": {
      "command": "uv",
      "args": ["--directory", "C:\\BIU01\\L06", "run", "gmail-calendar"],
      "env": {
        "GOOGLE_PRIVATE_DIR": "C:\\Users\\Shira\\Documents\\Uni\\שנה 'ג\\בינה מלאכותית יוצרת"
      }
    }
  }
}
```
