"""Google OAuth credential loading and API client factories."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build


def _resolve_private_dir() -> Path:
    """Return the validated directory path from GOOGLE_PRIVATE_DIR."""
    load_dotenv()
    raw_dir = os.environ.get("GOOGLE_PRIVATE_DIR", "").strip()
    if not raw_dir:
        raise RuntimeError(
            "GOOGLE_PRIVATE_DIR environment variable is not set."
        )
    private_dir = Path(raw_dir)
    if not private_dir.is_dir():
        raise RuntimeError(
            "GOOGLE_PRIVATE_DIR does not point to an existing directory."
        )
    return private_dir


def load_credentials() -> Credentials:
    """Load existing Google OAuth credentials without opening a browser."""
    private_dir = _resolve_private_dir()
    if not any(private_dir.glob("client_secret*.json")):
        raise RuntimeError(
            "No client_secret*.json file found in GOOGLE_PRIVATE_DIR."
        )

    token_path = private_dir / "token.json"
    if not token_path.is_file():
        raise RuntimeError("No token.json file found in GOOGLE_PRIVATE_DIR.")

    creds = Credentials.from_authorized_user_file(str(token_path))
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
        else:
            raise RuntimeError(
                "Stored Google token is invalid and cannot be refreshed "
                "without interactive authorization."
            )
    return creds


def get_gmail_service() -> Resource:
    """Build and return an authenticated Gmail API v1 service."""
    return build(
        "gmail", "v1", credentials=load_credentials(), cache_discovery=False
    )


def get_calendar_service() -> Resource:
    """Build and return an authenticated Google Calendar API v3 service."""
    return build(
        "calendar", "v3", credentials=load_credentials(), cache_discovery=False
    )
