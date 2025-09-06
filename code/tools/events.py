import os
import requests
from datetime import datetime
from calendar import monthrange
from dotenv import load_dotenv
from typing import Optional, List, Dict
from utils.date_utils import normalize_month, month_number, choose_year_for_month

load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")
DEBUG = False  # set True to see debug prints in terminal

# Optional: helps Ticketmaster disambiguate city searches
CITY_COUNTRY: Dict[str, str] = {
    "london": "GB",
    "amsterdam": "NL",
    "prague": "CZ",
    "paris": "FR",
    "berlin": "DE",
    "rome": "IT",
    "new york": "US",
    "tokyo": "JP",
    "athens": "GR",
    "sofia": "BG",
    "bucharest": "RO",
}

def _log(*args):
    if DEBUG:
        print("[events]", *args)

def _month_range(year: int, m_idx: int):
    start = datetime(year, m_idx, 1, 0, 0, 0)
    end_day = monthrange(year, m_idx)[1]
    end = datetime(year, m_idx, end_day, 23, 59, 59)
    return start, end

def _extract_events(j: dict, fallback_city: str) -> List[dict]:
    out = []
    data = j.get("_embedded", {}).get("events", [])
    for e in data:
        name = e.get("name")
        url_e = e.get("url")
        venues = e.get("_embedded", {}).get("venues", [])
        where = (venues[0].get("name") if venues else None) or fallback_city
        dates = e.get("dates", {}).get("start", {}).get("localDate") or ""
        out.append({"title": name, "where": where, "date_hint": dates, "url": url_e})
    return out

def get_events(place: str, when: str, year: Optional[int] = None) -> List[dict]:
    """
    Query Ticketmaster Discovery API for events.
    Returns list of dicts: [{"title","where","date_hint","url"}].
    Rolls past months to next year automatically.
    """
    if not API_KEY:
        _log("No Ticketmaster API key loaded.")
        return []

    city = (place or "").strip()
    month_name = normalize_month(when)
    if not city or not month_name:
        _log("Bad inputs", {"city": city, "when": when})
        return []

    # Pick a future-looking year if necessary
    y = choose_year_for_month(month_name, preferred_year=year)
    m_idx = month_number(month_name)
    if not m_idx:
        _log("Unknown month", month_name)
        return []

    start, end = _month_range(y, m_idx)

    base_params = {
        "apikey": API_KEY,
        "startDateTime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size": 10,
        "sort": "date,asc",
        "locale": "*",
    }
    cc = CITY_COUNTRY.get(city.lower())

    # Attempt 1: city filter
    params = dict(base_params)
    params["city"] = city
    if cc:
        params["countryCode"] = cc

    try:
        r = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params, timeout=10)
        j = r.json()
        _log("HTTP", r.status_code, "page", j.get("page", {}))
        events = _extract_events(j, fallback_city=city)
        if events:
            return events
    except Exception as exc:
        _log("City query failed", exc)

    # Attempt 2: keyword fallback
    params_fb = dict(base_params)
    params_fb["keyword"] = city
    if cc:
        params_fb["countryCode"] = cc

    try:
        r2 = requests.get("https://app.ticketmaster.com/discovery/v2/events.json", params=params_fb, timeout=10)
        j2 = r2.json()
        _log("Fallback HTTP", r2.status_code, "page", j2.get("page", {}))
        events2 = _extract_events(j2, fallback_city=city)
        return events2
    except Exception as exc:
        _log("Keyword fallback failed", exc)
        return []
