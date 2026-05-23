from __future__ import annotations

import re
from datetime import datetime


def parse_aflas_label(label: str):
    """
    Robust parser for Aflas.dk labels.

    Supports formats:
    - "x\n(2026-05-22 00:00:00 - 2026-05-23 00:00:00)"
    - "x (2026-05-22 00:00:00 - 2026-05-23 00:00:00)"
    - "(2026-05-22 00:00:00 - 2026-05-23 00:00:00)"
    - "2026-05-22 00:00:00 - 2026-05-23 00:00:00"
    - "22-05-2026 00:00 - 23-05-2026 00:00" (Danish format)

    Returns:
        (start_datetime, end_datetime) or None
    """

    if not label:
        return None

    # Extract the date range part
    match = re.search(r"\((.*?)\)", label)
    if match:
        date_range = match.group(1)
    else:
        # No parentheses → try whole string
        date_range = label.strip()

    # Normalize whitespace
    date_range = " ".join(date_range.split())

    # Split on dash
    if " - " not in date_range:
        return None

    start_str, end_str = date_range.split(" - ", 1)

    # Try ISO format first
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            start = datetime.strptime(start_str, fmt)
            end = datetime.strptime(end_str, fmt)
            return start, end
        except Exception:
            pass

    # Try Danish format
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M"):
        try:
            start = datetime.strptime(start_str, fmt)
            end = datetime.strptime(end_str, fmt)
            return start, end
        except Exception:
            pass

    return None

