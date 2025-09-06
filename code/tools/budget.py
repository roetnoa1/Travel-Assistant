from typing import Dict

_PER_DAY_BASE: Dict[str, int] = {
    "western europe": 160,
    "eastern europe": 120,
    "greece": 110,
    "cyprus": 110,
    "bulgaria": 90,
    "romania": 95,
    "slovenia": 100,
    "japan": 160,
    "southeast asia": 85,
}

_FLIGHT_FROM_TLV: Dict[str, int] = {
    "western europe": 450,
    "eastern europe": 350,
    "greece": 300,
    "cyprus": 200,
    "bulgaria": 300,
    "romania": 300,
    "slovenia": 350,
    "japan": 1000,
    "southeast asia": 900,
}

# Map common city/area names to our pricing buckets
_ALIAS_TO_BUCKET: Dict[str, str] = {
    # Eastern Europe cities
    "prague": "eastern europe", "budapest": "eastern europe", "krakow": "eastern europe",
    "vienna": "western europe",  # Vienna is actually more expensive
    "sofia": "bulgaria", "plovdiv": "bulgaria",
    "bucharest": "romania", "cluj": "romania",
    
    # Western Europe
    "barcelona": "western europe", "spain": "western europe",
    "lisbon": "western europe", "portugal": "western europe", 
    "amsterdam": "western europe", "paris": "western europe", "rome": "western europe",
    "berlin": "western europe", "madrid": "western europe", "porto":"western europe",
    
    # Greece / Cyprus
    "athens": "greece", "crete": "greece", "rhodes": "greece",
    "limassol": "cyprus", "larnaca": "cyprus", "paphos": "cyprus",
    
    # Balkans
    "ljubljana": "slovenia", "slovenia": "slovenia",
    
    # Japan
    "tokyo": "japan", "kyoto": "japan", "japan": "japan",
    
    # Regional shorthands
    "baltics": "eastern europe",
    
    # Southeast Asia
    "bangkok": "southeast asia", "bali": "southeast asia", "hanoi": "southeast asia",
}

# Countries we should not suggest (business rule for this project)
_EXCLUDED_DESTINATIONS = {"turkey", "istanbul", "antalya", "izmir"}


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _comfort_multiplier(level: str) -> float:
    level = _normalize(level)
    if level == "budget":
        return 0.8
    if level == "comfort":
        return 1.3
    # default
    return 1.0


def _resolve_bucket(region_or_city: str) -> str:
    key = _normalize(region_or_city)
    # Exclude Turkey up-front
    if key in _EXCLUDED_DESTINATIONS:
        # fallback to a similar price class so we still compute something if called directly
        return "eastern europe"

    # Direct bucket name
    if key in _PER_DAY_BASE:
        return key

    # Alias mapping (cities/regions)
    if key in _ALIAS_TO_BUCKET:
        return _ALIAS_TO_BUCKET[key]

    # Heuristic fallback: if unknown, lean to Eastern Europe (conservative)
    return "eastern europe"


def rough_budget(
    region_or_city: str,
    days: int,
    origin: str = "Tel Aviv",
    comfort: str = "standard",
) -> Dict[str, object]:
    """
    Return a coarse USD estimate for a trip.

    Args:
        region_or_city: city or region label (e.g., "Prague", "Greece", "Eastern Europe")
        days: number of trip days (int >= 1)
        origin: origin city (informational only)
        comfort: "budget" | "standard" | "comfort" -> applies multiplier to per-day costs

    Returns:
        {
          "origin": str,
          "region_bucket": str,
          "days": int,
          "flight": int,
          "per_day_base": int,
          "comfort_level": str,
          "comfort_multiplier": float,
          "per_day_applied": int,
          "estimate_total": int,
          "range_low": int,
          "range_high": int,
          "breakdown": {"lodging_food_activities": int, "flight": int},
          "disclaimer": str
        }
    """
    try:
        d = max(1, int(days))
    except Exception:
        d = 1

    bucket = _resolve_bucket(region_or_city)
    per_day_base = _PER_DAY_BASE.get(bucket, 120)
    flight = _FLIGHT_FROM_TLV.get(bucket, 350)

    mult = _comfort_multiplier(comfort)
    per_day_applied = int(round(per_day_base * mult))

    variable_cost = per_day_applied * d
    total = int(flight + variable_cost)

    low = int(total * 0.9)
    high = int(total * 1.1)

    return {
        "origin": origin,
        "region_bucket": bucket,
        "days": d,
        "flight": flight,
        "per_day_base": per_day_base,
        "comfort_level": comfort,
        "comfort_multiplier": mult,
        "per_day_applied": per_day_applied,
        "estimate_total": total,
        "range_low": low,
        "range_high": high,
        "breakdown": {
            "lodging_food_activities": variable_cost,
            "flight": flight,
        },
        "disclaimer": (
            "Heuristic estimate based on regional price bands and a rough flight cost from Tel Aviv. "
            "Real prices vary by dates, booking timing, and hotel/airline choices."
        ),
    }
