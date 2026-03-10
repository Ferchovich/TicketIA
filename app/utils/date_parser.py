"""Date parsing utilities."""
import re
import logging
from typing import Optional
from datetime import date, datetime

logger = logging.getLogger(__name__)

# Common date patterns found in Argentine receipts/invoices
_DATE_PATTERNS = [
    # DD/MM/YYYY or DD-MM-YYYY
    (re.compile(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})"), "%d/%m/%Y"),
    # YYYY/MM/DD or YYYY-MM-DD (ISO)
    (re.compile(r"(\d{4})[/\-](\d{2})[/\-](\d{2})"), "%Y/%m/%d"),
    # DD/MM/YY
    (re.compile(r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2})$"), "%d/%m/%y"),
]


def parse_date(raw: Optional[str]) -> Optional[str]:
    """
    Parse a date string into YYYY-MM-DD format.
    Returns None if the date cannot be parsed.
    """
    if not raw:
        return None
    raw = raw.strip()
    for pattern, fmt in _DATE_PATTERNS:
        m = pattern.search(raw)
        if m:
            try:
                if fmt in ("%d/%m/%Y", "%d/%m/%y"):
                    d = datetime.strptime(m.group(0).replace("-", "/"), fmt)
                elif fmt == "%Y/%m/%d":
                    d = datetime.strptime(m.group(0).replace("-", "/"), fmt)
                else:
                    d = datetime.strptime(m.group(0), fmt)
                return d.date().isoformat()
            except ValueError:
                continue
    # Try ISO direct
    try:
        d = date.fromisoformat(raw[:10])
        return d.isoformat()
    except ValueError:
        pass
    logger.debug("Could not parse date: %r", raw)
    return None
