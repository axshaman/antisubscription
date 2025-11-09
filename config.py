"""Application configuration helpers.

The project historically relied on environment variables that were populated by
Docker Compose.  Over time a number of implicit defaults slipped into the code
base which made local development unnecessarily tricky.  This module now
provides a single place where all configuration values are collected together
with sensible defaults.  The :mod:`python-dotenv` package is used to load a
``.env`` file when present so the application can be configured without
exporting environment variables manually.
"""

from __future__ import annotations

import os
from typing import Optional

import dotenv


dotenv.load_dotenv()


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Return the value of an environment variable.

    ``os.getenv`` already provides similar behaviour, but this wrapper makes it
    explicit that ``None`` may be returned when a variable is not set.  The
    helper also improves testability because it can be monkey patched when
    necessary.
    """

    return os.getenv(name, default)


# === Email configuration ===
MAIL_SERVICE = _get_env("mail_service")
MAIL_LOGIN = _get_env("login")
MAIL_PASSWORD = _get_env("password")

# === Optional alternative mailbox configuration ===
MAIL_SERVICE_GMAIL = _get_env("mail_service_gmail")
MAIL_LOGIN_GMAIL = _get_env("login_gmail")
MAIL_PASSWORD_GMAIL = _get_env("password_gmail")


# ----- Postgres -----
PG_LOGIN = _get_env("user_login")
PG_PASSWORD = _get_env("user_pass")
PG_HOST = _get_env("pg_host", "db")
PG_PORT = int(_get_env("pg_port", "5432"))
PG_DATABASE = _get_env("pg_database", "antipodpiska")


DEBUG = False
SECRET_KEY = "antisubscription-secret-key"

# Database settings used by Flask-SQLAlchemy when the extension is enabled.
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{PG_LOGIN}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    if PG_LOGIN and PG_PASSWORD
    else None
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = False

