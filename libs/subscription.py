import base64
import logging
import re
from typing import Iterable


LOGGER = logging.getLogger(__name__)


def subscription(raw_data_of_mail: str, keys_list: Iterable[str]) -> int:
    """Return the number of subscription related keyword matches."""

    marker = "X-Antivirus-Status:"
    start_index = raw_data_of_mail.find(marker)
    if start_index != -1:
        main_content = raw_data_of_mail[start_index + len("X-Antivirus-Status: Clean"):]
    else:
        main_content = raw_data_of_mail

    try:
        decoded = base64.b64decode(main_content)
        main_content = decoded.decode("utf-8")
    except Exception:  # pragma: no cover - defensive decoding
        LOGGER.debug("Unable to decode message body, continuing with raw content")

    def scan_text(keys: Iterable[str]) -> int:
        subscription_count = 0
        for value in keys:
            matches = re.findall(value, main_content, flags=re.IGNORECASE)
            subscription_count += len(matches)
        return subscription_count

    if re.search("text/(html|plain)", raw_data_of_mail):
        return scan_text(keys_list)

    LOGGER.debug("Skipping message without textual payload")
    return 0
