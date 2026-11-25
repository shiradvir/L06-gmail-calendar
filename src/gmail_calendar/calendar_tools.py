"""Google Calendar API helper functions in Asia/Jerusalem timezone."""

from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from .auth import get_calendar_service

TZ_NAME = "Asia/Jerusalem"
TZ = ZoneInfo(TZ_NAME)


def _parse_iso_in_tz(value: str) -> datetime:
    """Parse an ISO-8601 string, defaulting naive values to Asia/Jerusalem."""
    dt = datetime.fromisoformat(value.strip())
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt.astimezone(TZ)


def _parse_event_dt(raw: dict[str, str]) -> datetime:
    """Parse a Google Calendar start/end dict into an Asia/Jerusalem datetime."""
    if "dateTime" in raw:
        return _parse_iso_in_tz(raw["dateTime"])
    if "date" in raw:
        return datetime.combine(date_cls.fromisoformat(raw["date"]), time.min, tzinfo=TZ)
    raise ValueError("Calendar event missing start/end dateTime or date.")


def _format_event(event: dict[str, Any]) -> dict[str, Any]:
    """Return a concise representation of a Google Calendar event."""
    start, end = event.get("start", {}), event.get("end", {})
    return {
        "id": event.get("id", ""),
        "title": event.get("summary", "(No title)"),
        "start": start.get("dateTime") or start.get("date", ""),
        "end": end.get("dateTime") or end.get("date", ""),
        "location": event.get("location", ""),
        "description": event.get("description", ""),
        "html_link": event.get("htmlLink", ""),
    }


def _fetch_events(start_dt: datetime, end_dt: datetime) -> list[dict[str, Any]]:
    """Query primary calendar events within [start_dt, end_dt] in Asia/Jerusalem."""
    response = (
        get_calendar_service()
        .events()
        .list(
            calendarId="primary",
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            timeZone=TZ_NAME,
        )
        .execute()
    )
    return response.get("items", [])


def list_events(days_ahead: int = 7) -> list[dict[str, Any]]:
    """List upcoming primary calendar events for the next days_ahead days."""
    if days_ahead < 0:
        raise ValueError("days_ahead must be zero or positive.")
    now = datetime.now(TZ)
    return [_format_event(ev) for ev in _fetch_events(now, now + timedelta(days=days_ahead))]


def find_free_slots(date: str, duration_minutes: int = 30) -> dict[str, Any]:
    """Find available time slots on a YYYY-MM-DD date between 08:00 and 20:00."""
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive.")

    target_date = date_cls.fromisoformat(date.strip())
    win_start = datetime.combine(target_date, time(8, 0), tzinfo=TZ)
    win_end = datetime.combine(target_date, time(20, 0), tzinfo=TZ)

    busy: list[tuple[datetime, datetime]] = []
    for ev in _fetch_events(win_start, win_end):
        if ev.get("transparency") == "transparent":
            continue
        ev_start = max(_parse_event_dt(ev["start"]), win_start)
        ev_end = min(_parse_event_dt(ev["end"]), win_end)
        if ev_end > ev_start:
            if busy and ev_start <= busy[-1][1]:
                busy[-1] = (busy[-1][0], max(busy[-1][1], ev_end))
            else:
                busy.append((ev_start, ev_end))

    min_delta = timedelta(minutes=duration_minutes)
    slots: list[dict[str, Any]] = []
    cursor = win_start
    for b_start, b_end in [*busy, (win_end, win_end)]:
        if b_start - cursor >= min_delta:
            slots.append({
                "start": cursor.isoformat(),
                "end": b_start.isoformat(),
                "duration_minutes": int((b_start - cursor).total_seconds() // 60),
            })
        cursor = max(cursor, b_end)

    return {
        "date": target_date.isoformat(),
        "timezone": TZ_NAME,
        "window": {"start": win_start.isoformat(), "end": win_end.isoformat()},
        "requested_duration_minutes": duration_minutes,
        "free_slots": slots,
    }


def create_event(
    title: str, start: str, end: str, description: str = ""
) -> dict[str, Any]:
    """Create a Google Calendar event in the primary calendar."""
    start_dt, end_dt = _parse_iso_in_tz(start), _parse_iso_in_tz(end)
    if end_dt <= start_dt:
        raise ValueError("Event end time must be after start time.")

    body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": TZ_NAME},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": TZ_NAME},
    }
    created = get_calendar_service().events().insert(calendarId="primary", body=body).execute()
    return _format_event(created)
