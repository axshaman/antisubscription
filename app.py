"""Flask entry point for the Antisubscription API."""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Sequence

import dateparser
from flask import Flask, jsonify, render_template, request
from psycopg2.extras import RealDictCursor

import config
from app_yandex import get_data
from connect_db import get_connection


APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(APP_DIR, "static_html/js/")
TEMPLATE_FOLDER = os.path.join(APP_DIR, "static_html/")

MIN_PERIOD_DAYS = 22


app = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config.from_object(config)


def _parse_keywords(payload: Dict[str, Any]) -> List[str]:
    """Extract a normalised list of keywords from the request payload."""

    keywords = payload.get("keywords") or payload.get("keyWords") or []
    if isinstance(keywords, str):
        return [value for value in keywords.split() if value]
    if isinstance(keywords, Sequence):
        return [str(value).strip() for value in keywords if str(value).strip()]
    return []


def _parse_date(value: str | None) -> datetime | None:
    """Parse an ISO or natural language date string."""

    if not value:
        return None
    parsed = dateparser.parse(value)
    if not parsed:
        raise ValueError(f"Unable to parse date: {value}")
    return parsed


def fetch_subscriptions(
    *,
    recipient: str | None = None,
    sender: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int | None = None,
) -> List[Dict[str, Any]]:
    """Query subscription records from the database."""

    clauses = ["subscription > 0"]
    params: List[Any] = []

    if recipient:
        clauses.append("recipient = %s")
        params.append(recipient)
    if sender:
        clauses.append("email = %s")
        params.append(sender)
    if start_date:
        clauses.append("send_date >= %s")
        params.append(start_date)
    if end_date:
        clauses.append("send_date <= %s")
        params.append(end_date)

    where_clause = " AND ".join(clauses)
    query = (
        "SELECT sender, email, recipient, send_date, subscription "
        "FROM public.anti WHERE "
        f"{where_clause} ORDER BY send_date DESC"
    )

    if limit:
        query += " LIMIT %s"
        params.append(limit)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            records = cursor.fetchall()

    return [
        {
            "sender": record["sender"],
            "email": record["email"],
            "recipient": record["recipient"],
            "send_date": record["send_date"].isoformat(),
            "subscription": record["subscription"],
        }
        for record in records
    ]


def summarize_subscriptions(records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return aggregated statistics for the provided records."""

    summary: Dict[str, Dict[str, Any]] = {}
    for record in records:
        key = record["email"]
        send_date = (
            dateparser.parse(record["send_date"]) if isinstance(record["send_date"], str) else record["send_date"]
        )
        if key not in summary:
            summary[key] = {
                "email": key,
                "sender": record.get("sender"),
                "count": 0,
                "recipients": set(),
                "last_seen": send_date,
            }
        summary[key]["count"] += 1
        summary[key]["recipients"].add(record["recipient"])
        if send_date and (not summary[key]["last_seen"] or send_date > summary[key]["last_seen"]):
            summary[key]["last_seen"] = send_date

    formatted: List[Dict[str, Any]] = []
    for item in summary.values():
        formatted.append(
            {
                "email": item["email"],
                "sender": item["sender"],
                "count": item["count"],
                "recipients": sorted(item["recipients"]),
                "last_seen": item["last_seen"].isoformat() if item["last_seen"] else None,
            }
        )

    formatted.sort(key=lambda entry: entry["count"], reverse=True)
    return formatted


def detect_periodic_senders(
    records: Iterable[Dict[str, Any]],
    *,
    min_gap_days: int = MIN_PERIOD_DAYS,
    min_events: int = 2,
) -> List[Dict[str, Any]]:
    """Identify senders that contact the recipient on a recurring basis."""

    grouped: Dict[str, List[datetime]] = defaultdict(list)
    for record in records:
        send_date = record["send_date"]
        parsed = dateparser.parse(send_date) if isinstance(send_date, str) else send_date
        if parsed:
            grouped[record["email"]].append(parsed)

    periodic_senders: List[Dict[str, Any]] = []
    for email, dates in grouped.items():
        if len(dates) < min_events:
            continue
        dates.sort(reverse=True)
        gaps = [
            (dates[index - 1] - current).days
            for index, current in enumerate(dates[1:], start=1)
        ]
        qualifying_gaps = [gap for gap in gaps if gap >= min_gap_days]
        if not qualifying_gaps:
            continue
        periodic_senders.append(
            {
                "email": email,
                "occurrences": len(dates),
                "largest_gap_days": max(qualifying_gaps),
                "last_seen": dates[0].isoformat(),
            }
        )

    periodic_senders.sort(key=lambda item: item["occurrences"], reverse=True)
    return periodic_senders


@app.route("/", methods=["GET"])
def index() -> str:
    """Return the static dashboard entry point."""

    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health() -> Any:
    """Simple health check endpoint used by monitoring probes."""

    return jsonify({"status": "ok"})


@app.route("/account", methods=["POST"])
def register_account() -> Any:
    """Trigger mailbox synchronisation for a given account."""

    payload = request.get_json(force=True)
    keywords = _parse_keywords(payload)

    lookback_days = int(payload.get("lookback_days", 730))
    max_messages = payload.get("max_messages")
    max_messages = int(max_messages) if max_messages is not None else None

    stored_messages = get_data(
        payload["mail_service"],
        payload["login"],
        payload["password"],
        keywords,
        lookback_days=lookback_days,
        max_messages=max_messages,
    )

    return jsonify({"status": "ok", "stored_messages": stored_messages}), 200


@app.route("/subscriptions", methods=["GET"])
def list_subscriptions() -> Any:
    """Return stored subscription e-mails with optional filtering."""

    recipient = request.args.get("recipient")
    sender = request.args.get("sender")
    try:
        start = _parse_date(request.args.get("start"))
        end = _parse_date(request.args.get("end"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    limit = request.args.get("limit")
    limit_value = int(limit) if limit else None

    records = fetch_subscriptions(
        recipient=recipient,
        sender=sender,
        start_date=start,
        end_date=end,
        limit=limit_value,
    )

    return jsonify({"records": records})


@app.route("/subscriptions/summary", methods=["GET"])
def subscription_summary() -> Any:
    """Return aggregated metrics grouped by sender."""

    records = fetch_subscriptions()
    return jsonify({"summary": summarize_subscriptions(records)})


@app.route("/subscriptions/periodic", methods=["GET"])
def periodic_subscriptions() -> Any:
    """Return senders that contacted the recipient on a predictable schedule."""

    try:
        min_gap_days = int(request.args.get("min_gap_days", MIN_PERIOD_DAYS))
        min_events = int(request.args.get("min_events", 2))
    except ValueError:
        return jsonify({"error": "min_gap_days and min_events must be integers"}), 400
    recipient = request.args.get("recipient")

    records = fetch_subscriptions(recipient=recipient)
    return jsonify(
        {
            "periodic_senders": detect_periodic_senders(
                records, min_gap_days=min_gap_days, min_events=min_events
            )
        }
    )


@app.route("/senders", methods=["GET"])
def legacy_senders_endpoint() -> Any:
    """Backwards compatible version of the original `/senders` endpoint."""

    recipient = request.args.get("login")
    try:
        min_gap_days = int(request.args.get("min_gap_days", MIN_PERIOD_DAYS))
        min_events = int(request.args.get("min_events", 2))
    except ValueError:
        return jsonify({"error": "min_gap_days and min_events must be integers"}), 400

    records = fetch_subscriptions(recipient=recipient)
    periodic = detect_periodic_senders(records, min_gap_days=min_gap_days, min_events=min_events)

    return jsonify({"records": records, "periodic_senders": periodic})


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
