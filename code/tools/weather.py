from typing import Optional, Tuple
import requests
from meteostat import Normals, Point
import pandas as pd
from datetime import datetime
from utils.date_utils import normalize_month, month_number, choose_year_for_month

def geocode(place: str) -> Optional[Tuple[float, float, str]]:
    """Open-Meteo free geocoder: place -> (lat, lon, resolved_name)"""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        r = requests.get(
            url,
            params={"name": place, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        j = r.json()
        if not j or "results" not in j or not j["results"]:
            return None
        res = j["results"][0]
        lat = float(res["latitude"])
        lon = float(res["longitude"])
        name = res.get("name") or place
        return lat, lon, name
    except Exception:
        return None

def safe_get(df: pd.DataFrame, col: str):
    if col in df.columns and not df[col].empty:
        try:
            return float(df[col].values[0])
        except Exception:
            return None
    return None

def get_weather_summary(place: str, when: str, year: Optional[int] = None) -> Optional[dict]:
    """
    Return climate-normal summary for (place, month):
    {
        "place": "<resolved place>",
        "month": <int 1..12>,
        "year_context": <int>,  # chosen year for narrative (not used in normals)
        "avg_temp_c": <float|None>,  # monthly mean temperature
        "rain_mm": <float|None>,  # monthly total precipitation (mm)
        "notes": "Climate normals 1991–2020",
        "source": "Meteostat (normals), Open-Meteo geocoding"
    }
    Returns None if inputs can't be resolved.
    """
    month_name = normalize_month(when)
    if not place or not month_name:
        return None

    yc = choose_year_for_month(month_name, preferred_year=year)
    geo = geocode(place)
    if not geo:
        return None

    lat, lon, resolved = geo

    try:
        # Meteostat monthly climate normals (1991–2020)
        loc = Point(lat, lon)
        normals = Normals(loc, 1991, 2020).fetch()
        
        m_idx = month_number(month_name)
        if not m_idx:
            return None


        # Try different approaches to filter by month
        row = None
        
        # Method 1: If index has month attribute
        try:
            if hasattr(normals.index, 'month'):
                row = normals[normals.index.month == m_idx]
        except Exception as e:
            pass

        # Method 2: If normals has a month column
        if row is None or row.empty:
            try:
                if 'month' in normals.columns:
                    row = normals[normals['month'] == m_idx]
            except Exception as e:
                pass

        # Method 3: Try iloc if normals has 12 rows (one per month)
        if row is None or row.empty:
            try:
                if len(normals) == 12:
                    row = normals.iloc[m_idx - 1:m_idx]  # month 1 = index 0
            except Exception as e:
                pass

        # Method 4: Try direct indexing if normals index is 1-12
        if row is None or row.empty:
            try:
                if m_idx in normals.index:
                    row = normals.loc[[m_idx]]
            except Exception as e:
                pass

        if row is None or row.empty:
            return None


        tavg = safe_get(row, "tavg")  # °C
        prcp = safe_get(row, "prcp")  # mm
        

        return {
            "place": resolved,
            "month": m_idx,
            "year_context": yc,
            "avg_temp_c": round(tavg, 1) if tavg is not None else None,
            "rain_mm": round(prcp, 1) if prcp is not None else None,
            "notes": "Climate normals 1991–2020",
            "source": "Meteostat (normals), Open-Meteo geocoding",
        }

    except Exception:
        return None