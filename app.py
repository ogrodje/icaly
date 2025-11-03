import hashlib
import os
import re
import time
from datetime import datetime, timezone

import requests
from flask import Flask, Response, jsonify, send_from_directory

TIMELINE_URL = "https://goo.ogrodje.si/timeline"
CACHE_TTL_SECONDS = 5 * 60
USER_AGENT = "dogodki-google-cal-python/1.0"

app = Flask(__name__, static_folder="public", static_url_path="")

_cache_timestamp = 0.0
_cached_events = None


@app.after_request
def _set_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Referrer-Policy",
        "no-referrer-when-downgrade",
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; base-uri 'self'; form-action 'self'",
    )
    return response


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/healthz")
def healthz():
    return "ok", 200


@app.route("/api/events")
def events_endpoint():
    try:
        events = _load_events()
    except RuntimeError as exc:
        app.logger.warning("Failed to load events: %s", exc)
        return jsonify({"error": "Unable to fetch events right now."}), 502
    return jsonify(events)


@app.route("/calendar.ics")
def calendar_endpoint():
    try:
        events = _load_events()
    except RuntimeError as exc:
        app.logger.warning("Failed to build calendar: %s", exc)
        return Response(
            "Unable to build calendar feed right now.",
            status=502,
            mimetype="text/plain",
        )

    payload = _build_calendar(events)
    headers = {
        "Content-Type": "text/calendar; charset=utf-8",
        "Content-Disposition": 'attachment; filename="timeline.ics"',
    }
    return Response(payload, headers=headers)


def _load_events():
    global _cache_timestamp, _cached_events

    now = time.time()
    if _cached_events is not None and now - _cache_timestamp < CACHE_TTL_SECONDS:
        return _cached_events

    try:
        response = requests.get(
            TIMELINE_URL,
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"timeline fetch failed: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("timeline returned invalid JSON") from exc

    if not isinstance(data, list):
        raise RuntimeError("timeline returned unexpected payload")

    _cached_events = data
    _cache_timestamp = now
    return _cached_events


def _build_calendar(events):
    dtstamp = _format_datetime(datetime.now(timezone.utc))
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//dogodki-google-cal-python//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for event in events:
        lines.extend(_event_to_ics(event, dtstamp))

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def _event_to_ics(event, dtstamp):
    output = ["BEGIN:VEVENT"]

    uid = event.get("id")
    if uid:
        safe_uid = _sanitize_uid(uid)
        output.append(_format_line("UID", _escape_text(f"{safe_uid}@dogodki-google-cal")))

    output.append(_format_line("DTSTAMP", dtstamp))

    start = _safely_format_iso(event.get("startDateTime"))
    end = _safely_format_iso(event.get("endDateTime"))

    if start:
        output.append(_format_line("DTSTART", start))
    if end:
        output.append(_format_line("DTEND", end))

    summary = _escape_text(_build_summary(event))
    output.append(_format_line("SUMMARY", summary))

    description = _escape_text(_build_description(event))
    if description:
        output.append(_format_line("DESCRIPTION", description))

    event_url = event.get("eventURL")
    if event_url:
        output.append(_format_line("URL", _escape_text(event_url)))

    location = _build_location(event)
    if location:
        output.append(_format_line("LOCATION", _escape_text(location)))

    output.append("END:VEVENT")
    return output


def _build_summary(event):
    source = event.get("source")
    title = event.get("title") or "Untitled Event"
    return f"[{source}] {title}" if source else title


def _build_description(event):
    parts = []

    raw_description = event.get("description")
    if raw_description:
        parts.append(_strip_html(str(raw_description)))

    event_url = event.get("eventURL")
    if event_url:
        parts.append(f"More info: {event_url}")

    return "\n\n".join(parts)


def _build_location(event):
    name = event.get("locationName")
    address = event.get("locationAddress")

    if name and address:
        return f"{name}, {address}"
    return name or address or ""


def _strip_html(value):
    return re.sub(r"<[^>]+>", "", value)


def _format_line(key, value):
    return _fold_line(f"{key}:{value}")


def _fold_line(line):
    max_length = 75
    if len(line) <= max_length:
        return line

    chunks = [line[:max_length]]
    rest = line[max_length:]

    while rest:
        chunks.append(" " + rest[: max_length - 1])
        rest = rest[max_length - 1 :]

    return "\r\n".join(chunks)


def _escape_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def _sanitize_uid(raw_uid):
    clean = re.sub(r"[^A-Za-z0-9._-]", "", str(raw_uid))
    if clean:
        return clean
    digest = hashlib.sha256(str(raw_uid).encode("utf-8")).hexdigest()
    return digest[:32]


def _safely_format_iso(raw):
    if not raw:
        return ""
    try:
        return _format_datetime(_parse_iso(raw))
    except (ValueError, TypeError):
        return ""


def _parse_iso(raw):
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def _format_datetime(dt):
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
