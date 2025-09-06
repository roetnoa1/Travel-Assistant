# utils/date_utils.py
from datetime import datetime
from typing import Optional

# Map month names → numbers
MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

ALIASES = {
    "jan":"January","january":"January",
    "feb":"February","february":"February",
    "mar":"March","march":"March",
    "apr":"April","april":"April",
    "may":"May",
    "jun":"June","june":"June",
    "jul":"July","july":"July",
    "aug":"August","august":"August",
    "sep":"September","sept":"September","september":"September",
    "oct":"October","october":"October",
    "nov":"November","november":"November",
    "dec":"December","december":"December",
}

def normalize_month(value: Optional[str]) -> Optional[str]:
    """Normalize free-text month input into 'January'..'December' or None."""
    if not value:
        return None
    v = str(value).strip().lower().replace(".", "")
    return ALIASES.get(v)

def month_number(name: str) -> Optional[int]:
    """Return month number (1–12) for normalized month name."""
    return MONTHS.get(name)

def choose_year_for_month(month_name: str, preferred_year: Optional[int] = None) -> int:
    """If month has already passed this year, roll to next year."""
    now = datetime.utcnow()
    y = preferred_year or now.year
    m = month_number(month_name)
    if not m:
        return y
    if (y < now.year) or (y == now.year and m < now.month):
        return now.year + 1
    return y

def normalize_entities(entities: dict) -> dict:
    """Light cleanup used by your route() handler:
       - Normalize 'when' to a canonical month name if possible.
       - Trim strings, keep None for unknowns.
    """
    e = dict(entities or {})
    for k in ("where", "budget", "party", "origin"):
        if isinstance(e.get(k), str):
            e[k] = e[k].strip() or None

    # Normalize month-ish 'when'
    e["when"] = normalize_month(e.get("when")) or (e.get("when") or None)

    # Normalize constraints array
    if e.get("constraints") is None:
        e["constraints"] = []
    elif isinstance(e.get("constraints"), list):
        e["constraints"] = [str(x).strip() for x in e["constraints"] if str(x).strip()]
    else:
        e["constraints"] = []

    # Coerce days to int if possible
    try:
        if e.get("days") is not None:
            e["days"] = int(e["days"])
    except Exception:
        e["days"] = None

    return e