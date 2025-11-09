"""Utilities to ingest messages from IMAP mailboxes."""

from __future__ import annotations

import datetime as dt
import email
import logging
import re
from email.message import Message
from email.utils import parsedate_tz
from typing import Iterable, Sequence

import dateparser
import imaplib

from connect_db import add_to_base
from libs.subscription import subscription


LOGGER = logging.getLogger(__name__)


def get_data(
    mail_service: str,
    mail_login: str,
    mail_password: str,
    keys_list: Sequence[str],
    *,
    lookback_days: int = 730,
    max_messages: int | None = 200,
) -> int:
    """Fetch recent emails and persist subscription related messages.

    Parameters
    ----------
    mail_service:
        IMAP server hostname.
    mail_login:
        Login name of the mailbox.
    mail_password:
        Password or application token.
    keys_list:
        Keywords used to detect subscription related content.
    lookback_days:
        How many days of history should be inspected.  Defaults to two years to
        keep backwards compatibility with the original behaviour.
    max_messages:
        An optional hard limit for the number of e-mails to analyse.  This makes
        the endpoint more predictable for very large inboxes.

    Returns
    -------
    int
        The number of messages that were persisted to the database.
    """

    mail = imaplib.IMAP4_SSL(mail_service)
    try:
        mail.login(mail_login, mail_password)
        mail.select("INBOX")

        _, data = mail.search(None, "ALL")
        numbers_mails = data[0].decode()
        numbers_mails_list = numbers_mails.split()

        cutoff_date = dt.datetime.now() - dt.timedelta(days=lookback_days)
        stored_messages = 0

        for counter, message_id in enumerate(reversed(numbers_mails_list), start=1):
            if max_messages and counter > max_messages:
                break

            result, data = mail.fetch(message_id, "(RFC822)")
            if result != "OK" or not data or not data[0]:
                LOGGER.warning("Unable to fetch message %s: %s", message_id, result)
                continue

            raw_data = data[0][1].decode("latin-1", errors="ignore")
            msg = email.message_from_string(raw_data)
            parsed = parsedate_tz(msg.get("Date"))
            if not parsed:
                LOGGER.debug("Skipping message %s because the date header is missing", message_id)
                continue

            date_str = f"{parsed[0]} {parsed[1]} {parsed[2]}"
            current_mail_date = dateparser.parse(date_str)
            if not current_mail_date or current_mail_date < cutoff_date:
                continue

            data_dict = raw_data_convert(msg, raw_data, keys_list, date_str)
            if data_dict["Subscription"]:
                add_to_base(data_dict)
                stored_messages += 1

        return stored_messages
    finally:
        try:
            mail.logout()
        except Exception:
            LOGGER.debug("Failed to close IMAP session cleanly")


def raw_data_convert(
    msg: Message,
    raw_data_of_mail: str,
    keys_list: Iterable[str],
    date_str: str,
) -> dict:
    sender = msg.get("From", "Unknown")
    index_of_finish = sender.find("<")
    name = sender[:index_of_finish] if index_of_finish > 0 else sender

    def extract_email(value: str | None) -> str:
        if not value:
            return "not@found.net"
        match = re.findall(r"<.*?>", value)
        if match:
            return match[0][1:-1]
        return value

    sender_email = extract_email(sender)
    recipient_email = extract_email(msg.get("To"))

    subscription_check = subscription(raw_data_of_mail, keys_list)

    return {
        "Sender": name.strip() or sender_email,
        "Email": sender_email,
        "Date": date_str,
        "Recipient": recipient_email,
        "Subscription": subscription_check or 0,
    }


__all__ = ["get_data", "raw_data_convert"]
