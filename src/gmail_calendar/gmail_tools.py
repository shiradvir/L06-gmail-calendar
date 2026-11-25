"""Gmail API helper functions (search, read, and draft creation only)."""

from __future__ import annotations

import base64
import html
import re
from email.message import EmailMessage
from typing import Any

from .auth import get_gmail_service


def _headers_map(headers: list[dict[str, str]]) -> dict[str, str]:
    """Convert Gmail header list into a case-insensitive lookup map."""
    return {h["name"].lower(): h.get("value", "") for h in headers}


def _decode_b64(data: str) -> str:
    """Decode base64url-encoded Gmail payload data to UTF-8 text."""
    if not data:
        return ""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode(
        "utf-8", errors="replace"
    )


def _strip_html(raw_html: str) -> str:
    """Convert HTML email content to readable plain text."""
    return html.unescape(re.sub(r"<[^>]+>", " ", raw_html)).strip()


def _extract_body(payload: dict[str, Any]) -> str:
    """Extract plain-text body from a Gmail message payload."""
    mime = payload.get("mimeType", "")
    data = payload.get("body", {}).get("data", "")
    if mime == "text/plain" and data:
        return _decode_b64(data)

    html_fallback = ""
    for part in payload.get("parts", []):
        part_mime = part.get("mimeType", "")
        if part_mime == "text/plain" or part_mime.startswith("multipart/"):
            text = _extract_body(part)
            if text:
                return text
        elif part_mime == "text/html" and not html_fallback:
            html_fallback = _strip_html(_decode_b64(part.get("body", {}).get("data", "")))

    if data:
        text = _decode_b64(data)
        return _strip_html(text) if mime == "text/html" else text
    return html_fallback


def search_emails(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """Search Gmail messages matching query and return summary metadata."""
    if max_results < 1:
        raise ValueError("max_results must be at least 1.")

    service = get_gmail_service()
    listing = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=min(max_results, 100))
        .execute()
    )
    results: list[dict[str, Any]] = []
    for item in listing.get("messages", []):
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=item["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )
        hdrs = _headers_map(msg.get("payload", {}).get("headers", []))
        results.append({
            "id": msg["id"],
            "thread_id": msg.get("threadId", ""),
            "subject": hdrs.get("subject", ""),
            "from": hdrs.get("from", ""),
            "date": hdrs.get("date", ""),
            "snippet": msg.get("snippet", ""),
        })
    return results


def read_email(message_id: str) -> dict[str, Any]:
    """Read a full email message by its Gmail message ID."""
    msg = (
        get_gmail_service()
        .users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = msg.get("payload", {})
    hdrs = _headers_map(payload.get("headers", []))
    return {
        "id": msg["id"],
        "thread_id": msg.get("threadId", ""),
        "subject": hdrs.get("subject", ""),
        "from": hdrs.get("from", ""),
        "to": hdrs.get("to", ""),
        "date": hdrs.get("date", ""),
        "snippet": msg.get("snippet", ""),
        "body": _extract_body(payload),
    }


def create_draft(to: str, subject: str, body: str) -> dict[str, Any]:
    """Create a Gmail draft without sending it."""
    service = get_gmail_service()
    recipient = to.strip()
    if not recipient or recipient.lower() == "me":
        recipient = service.users().getProfile(userId="me").execute()["emailAddress"]

    message = EmailMessage()
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")

    draft = (
        service.users()
        .drafts()
        .create(userId="me", body={"message": {"raw": raw}})
        .execute()
    )
    return {
        "draft_id": draft["id"],
        "message_id": draft.get("message", {}).get("id", ""),
        "to": recipient,
        "subject": subject,
        "status": "draft_created",
    }
