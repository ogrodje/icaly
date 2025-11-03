# icaly

icaly is a tiny Flask application that turns the public timeline at `https://goo.ogrodje.si/timeline`
into an auto-updating iCalendar feed. It exposes a Google Calendar–friendly `.ics` endpoint and a
companion web page where you can preview upcoming events before subscribing.

## Production

The service is serving requests at [`https://icaly.ogrodje.si/calendar.ics`](https://icaly.ogrodje.si/calendar.ics)

## Features

- Fetches and caches events from the timeline API every five minutes to minimise upstream traffic.
- Serves a standards-compliant `calendar.ics` feed with sanitised titles, descriptions, and links.
- Provides a `/api/events` JSON endpoint and a lightweight landing page that builds the Google
  Calendar subscription URL for you.
- Adds secure headers (CSP, X-Frame-Options, etc.) and avoids leaking internal error messages.

## Requirements

- Python 3.12 (earlier 3.11+ may work but is not tested)
- `pip` for dependency management

## Setup

```bash
git clone <this-repo-url>
cd dogodki-google-cal
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> You can pin additional dependencies or tweak cache timings by editing `app.py`.

## Running locally

Bind the server to localhost on the default port (3000):

```bash
source .venv/bin/activate
python app.py
```

Visit `http://127.0.0.1:3000/` to preview the events and grab the calendar link.

To run on a custom port, set `PORT` when starting the app:

```bash
PORT=9991 python app.py
```

The `/calendar.ics` path is what Google Calendar (or any CalDAV client) should subscribe to.

## Deployment notes

The built-in Flask development server is convenient for local use but not recommended for
production. For longer-term hosting:

1. Keep the app behind a production WSGI server (e.g., `gunicorn` or `uwsgi`).
2. Terminate TLS in front of the service so calendar clients fetch the feed securely.
3. Configure health checks against `/healthz` to ensure the timeline fetch remains healthy.

## Attribution

This project – architecture, code, and documentation – was fully generated with the help of OpenAI
Codex.
