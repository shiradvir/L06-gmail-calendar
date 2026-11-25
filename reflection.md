# Reflection

## What did we ask the agent?

We asked the agent to verify our external Google credentials without exposing secrets, build a `FastMCP` server (`gmail-calendar`) with 6 read/draft/create tools using `uv` and `stdio`, write `test_server.py`, and register the server in `.agents/mcp_config.json`. Afterward, we asked the agent to handle natural-language requests: checking tomorrow's schedule, creating a Gmail draft (`"L06 test"`) and a calendar event 4 hours ahead (`"MCP works"`), finding a free slot tomorrow for a `"Study group"` event, testing security boundaries (attempting to send the draft and delete the event), and setting up Git with clean commits.

## How did we check that the result is correct?

We inspected the file tree and tool table, verified `.gitignore` and `git status` to ensure no `token.json`, `client_secret*.json`, or `.env` files were tracked, ran `test_server.py` to check `tools/list` and `list_events`, and verified connection status via `/mcp`. We also confirmed the `"L06 test"` draft in Gmail Drafts, checked the created events (`"MCP works"` and `"Study group"`) in Google Calendar with the `Asia/Jerusalem` time zone, and verified that send and delete commands were refused due to the missing tools.

## Which tool did we leave out, and why?

We intentionally omitted any email-sending tool (`users.messages.send`) as well as any delete or trash tools for emails, drafts, or calendar events. Leaving these out enforces Human-in-the-Loop control so a human reviews every draft before sending, and protects against accidental data loss or indirect prompt injection from untrusted incoming emails.

## L05 vs L06: what changed?

In L05, the agent wrote a single rigid Python script (`main.py`) hardcoded for one fixed workflow. In L06, we built a reusable MCP tool server exposing 6 modular tools, allowing the model to dynamically select and combine tools from natural-language prompts across any MCP-compatible agent without writing new code.
