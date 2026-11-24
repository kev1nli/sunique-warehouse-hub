"""Address -> coordinates, and drive times between points.

Uses free public services (no API key):
- US Census geocoder, then OpenStreetMap Nominatim as a fallback
- OSRM public server for drive times
If a service is down, falls back to a city-center table and straight-line distance.
"""
from __future__ import annotations

import math
import re

import requests
import streamlit as st

UA = {"User-Agent": "SuniqueWarehouseHub/1.0 (delivery planner)"}

# approximate city centers, used only when the geocoders fail
CITY_CENTERS = {
    "dallas": (32.7767, -96.7970), "garland": (32.9126, -96.6389), "princeton": (33.1801, -96.4980),
    "seagoville": (32.6393, -96.5383), "forney": (32.7482, -96.4719), "fort worth": (32.7555, -97.3308),
    "mckinney": (33.1972, -96.6398), "plano": (33.0198, -96.6989), "irving": (32.8140, -96.9489),
    "richardson": (32.9483, -96.7299), "carrollton": (32.9756, -96.8899), "grand prairie": (32.7460, -96.9978),
    "arlington": (32.7357, -97.1081), "frisco": (33.1507, -96.8236), "allen": (33.1032, -96.6706),
    "mesquite": (32.7668, -96.5992), "rowlett": (32.9029, -96.5639), "rockwall": (32.9312, -96.4597),
    "wylie": (33.0151, -96.5389), "denton": (33.2148, -97.1331), "lewisville": (33.0462, -96.9942),
    "flower mound": (33.0146, -97.0970), "coppell": (32.9546, -97.0150), "farmers branch": (32.9265, -96.8961),
    "addison": (32.9618, -96.8292), "desoto": (32.5899, -96.8570), "duncanville": (32.6518, -96.9083),
    "cedar hill": (32.5885, -96.9561), "lancaster": (32.5921, -96.7561), "mansfield": (32.5632, -97.1417),
    "cleburne": (32.3476, -97.3867), "haslet": (32.9746, -97.3478), "godley": (32.4490, -97.5267),
    "terrell": (32.7357, -96.2753), "euless": (32.8371, -97.0820), "bedford": (32.8440, -97.1431),
    "grapevine": (32.9343, -97.0781), "keller": (32.9346, -97.2520), "southlake": (32.9412, -97.1342),
    "little elm": (33.1626, -96.9375), "prosper": (33.2362, -96.8011), "celina": (33.3246, -96.7844),
    "anna": (33.3490, -96.5486), "melissa": (33.2859, -96.5728), "sachse": (32.9762, -96.5953),
    "murphy": (33.0151, -96.6128), "midlothian": (32.4824, -96.9945), "waxahachie": (32.3866, -96.8483),
    "burleson": (32.5421, -97.3208), "weatherford": (32.7593, -97.7973), "royse city": (32.9751, -96.3325),
    "fate": (32.9415, -96.3814), "the colony": (33.0890, -96.8864), "balch springs": (32.7287, -96.6228),
    "sunnyvale": (32.7965, -96.5608), "crandall": (32.6279, -96.4558), "kaufman": (32.5890, -96.3089),
}


def clean_address(a: str) -> str:
    a = str(a or "").replace("/", ",").replace("–", " ").replace("—", " ")
    a = re.sub(r"\s+", " ", a).strip(" ,-")
    return a


def _city_of(a: str):
    m = re.search(r"([A-Za-z .]+?),?\s+(?:TX|Texas)\b", a, re.I)
    if not m:
        return None
    city = m.group(1).split(",")[-1].strip().lower()
    for name in sorted(CITY_CENTERS, key=len, reverse=True):
        if city.endswith(name):
            return name
    return None


@st.cache_data(ttl=30 * 86400, show_spinner=False)
def geocode(address: str):
    """Return (lat, lon, source) or None."""
    a = clean_address(address)
    try:
        r = requests.get(
            "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress",
            params={"address": a, "benchmark": "Public_AR_Current", "format": "json"}, timeout=15)
        m = r.json()["result"]["addressMatches"]
        if m:
            c = m[0]["coordinates"]
            return (c["y"], c["x"], "census")
    except Exception:
        pass
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": a, "format": "json", "limit": 1, "countrycodes": "us"},
                         headers=UA, timeout=15)
        j = r.json()
        if j:
            return (float(j[0]["lat"]), float(j[0]["lon"]), "osm")
    except Exception:
        pass
    city = _city_of(a)
    if city:
        lat, lon = CITY_CENTERS[city]
        return (lat, lon, "city")
    return None


def _haversine_min(a, b):
    r = 3958.8
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    miles = 2 * r * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))
    return miles * 1.3 / 40 * 60  # road factor 1.3, 40 mph average


@st.cache_data(ttl=7 * 86400, show_spinner=False)
def drive_matrix(points: tuple):
    """points = tuple of (lat, lon). Returns (minutes matrix, source)."""
    try:
        coords = ";".join(f"{lon:.6f},{lat:.6f}" for lat, lon in points)
        r = requests.get(f"https://router.project-osrm.org/table/v1/driving/{coords}",
                         params={"annotations": "duration"}, headers=UA, timeout=20)
        j = r.json()
        if j.get("code") == "Ok":
            return [[(v or 0) / 60 for v in row] for row in j["durations"]], "osrm"
    except Exception:
        pass
    return [[_haversine_min(a, b) for b in points] for a in points], "estimate"


def make_dur(points: list):
    """Build a dur(a, b) function over a fixed set of points (one matrix request)."""
    uniq = list(dict.fromkeys((round(p[0], 6), round(p[1], 6)) for p in points))
    mat, src = drive_matrix(tuple(uniq))
    idx = {p: i for i, p in enumerate(uniq)}

    def dur(a, b):
        ka, kb = (round(a[0], 6), round(a[1], 6)), (round(b[0], 6), round(b[1], 6))
        if ka in idx and kb in idx:
            return mat[idx[ka]][idx[kb]]
        return _haversine_min(a, b)

    return dur, src
