"""CUIT/CUIL parsing and normalization utilities."""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_CUIT_RE = re.compile(r"\b(\d{2})[\s\-]?(\d{8})[\s\-]?(\d{1})\b")


def normalize_cuit(raw: Optional[str]) -> Optional[str]:
    """
    Normalize a CUIT/CUIL to plain 11-digit string without separators.
    Returns None if invalid.
    """
    if not raw:
        return None
    raw = str(raw).strip()
    m = _CUIT_RE.search(raw)
    if m:
        cuit = m.group(1) + m.group(2) + m.group(3)
        if _validate_cuit(cuit):
            return cuit
    # Try stripping all non-digits
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and _validate_cuit(digits):
        return digits
    logger.debug("Could not normalize CUIT: %r", raw)
    return None


def _validate_cuit(cuit: str) -> bool:
    """Validate CUIT check digit using the Argentine algorithm."""
    if len(cuit) != 11 or not cuit.isdigit():
        return False
    weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = sum(int(cuit[i]) * weights[i] for i in range(10))
    remainder = total % 11
    check = 0 if remainder == 0 else (11 - remainder if remainder != 1 else 9)
    return check == int(cuit[10])


def format_cuit(cuit: Optional[str]) -> Optional[str]:
    """Format a normalized CUIT as XX-XXXXXXXX-X."""
    if not cuit or len(cuit) != 11:
        return cuit
    return f"{cuit[:2]}-{cuit[2:10]}-{cuit[10]}"
