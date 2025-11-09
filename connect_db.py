"""Database helper functions."""

from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
from typing import Dict, Generator

import psycopg2
from psycopg2.extras import execute_values

from config import PG_DATABASE, PG_HOST, PG_LOGIN, PG_PASSWORD, PG_PORT


@contextmanager
def get_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """Return a PostgreSQL connection with automatic cleanup."""

    if not PG_LOGIN or not PG_PASSWORD:
        raise RuntimeError(
            "Database credentials are missing. Set 'user_login' and 'user_pass' "
            "environment variables or populate the .env file."
        )

    conn = psycopg2.connect(
        user=PG_LOGIN,
        password=PG_PASSWORD,
        database=PG_DATABASE,
        host=PG_HOST,
        port=PG_PORT,
    )
    try:
        yield conn
    finally:
        conn.close()


def add_to_base(message: Dict[str, str]) -> None:
    """Persist a message dictionary to the ``public.anti`` table."""

    fmt = "%Y %m %d"
    send_date = dt.datetime.strptime(message["Date"], fmt)

    # psycopg2 does not support named parameters when used with execute_values,
    # therefore the payload is converted to an ordered tuple.
    values = [
        (
            message["Sender"],
            message["Email"],
            send_date,
            message["Recipient"],
            message["Subscription"],
        )
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO public.anti (sender, email, send_date, recipient, subscription) VALUES %s",
                values,
            )
        conn.commit()


__all__ = ["add_to_base", "get_connection"]
