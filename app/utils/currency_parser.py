"""Currency / amount parsing utilities."""
import re
import logging
from typing import Optional
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

# Matches numbers like 1.234,56 or 1,234.56 or 1234.56 or 1234,56
_AMOUNT_RE = re.compile(r"[\$\s]*([\d.,]+)")


def parse_amount(raw: Optional[str]) -> Optional[float]:
    """
    Parse a monetary amount string to float.
    Handles both Argentine (1.234,56) and US (1,234.56) formats.
    Returns None if cannot be parsed.
    """
    if not raw:
        return None
    raw = str(raw).strip()
    m = _AMOUNT_RE.search(raw)
    if not m:
        return None
    text = m.group(1)
    # Determine decimal separator: if last separator is comma → Argentine format
    last_dot = text.rfind(".")
    last_comma = text.rfind(",")
    if last_comma > last_dot:
        # Argentine format: dots as thousands, comma as decimal
        text = text.replace(".", "").replace(",", ".")
    else:
        # US or plain format: commas as thousands, dot as decimal
        text = text.replace(",", "")
    try:
        return float(Decimal(text))
    except InvalidOperation:
        logger.debug("Could not parse amount: %r", raw)
        return None
