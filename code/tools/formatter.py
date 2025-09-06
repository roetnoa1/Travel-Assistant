import json

def format_weather(w: dict) -> str:
    if not w:
        return "No reliable climate data found."
    return (f"{w['place']} in {w['month']} typically averages around "
            f"{w['avg_temp_c']} °C with {w['rain_mm']} mm of rain "
            f"(ERA5 climate normals).")

def format_budget(b: dict) -> str:
    if not b:
        return "No budget estimate available."
    return (f"From {b['origin']} to {b['region_bucket']}: flights ≈${b['flight']} "
            f"+ ${b['per_day_applied']}/day × {b['days']} days "
            f"≈ ${b['estimate_total']} (±10%).")

def format_events(evts: list) -> str:
    if not evts:
        return "No events found for that time/place."
    lines = [f"- {e['title']} ({e['date_hint']} at {e['where']})" for e in evts[:3]]
    return "Upcoming events:\n" + "\n".join(lines)
