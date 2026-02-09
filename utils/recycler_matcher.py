import json
import os
import math
from typing import List, Dict, Optional

_RECYCLERS_CACHE = None


def _load_recyclers() -> List[Dict]:
    global _RECYCLERS_CACHE
    if _RECYCLERS_CACHE is not None:
        return _RECYCLERS_CACHE

    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "recyclers.json")
    with open(data_path, "r", encoding="utf-8") as f:
        _RECYCLERS_CACHE = json.load(f)
    return _RECYCLERS_CACHE


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    # Earth radius in km
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _normalize_material(material_type: str) -> str:
    m = (material_type or "").lower()
    if "pet" in m or "bottle" in m:
        return "PET"
    if "hdpe" in m:
        return "HDPE"
    if "ldpe" in m:
        return "LDPE"
    if "pp" in m or "polypropylene" in m:
        return "PP"
    if "ps" in m or "polystyrene" in m:
        return "PS"
    if "paper" in m:
        return "Paper"
    if "cardboard" in m or "corrugated" in m:
        return "Cardboard"
    if "glass" in m:
        return "Glass"
    if "metal" in m or "aluminum" in m or "steel" in m:
        return "Metal"
    if "electronic" in m or "e-waste" in m or "ewaste" in m or "circuit" in m:
        return "Electronics"
    if "battery" in m:
        return "Batteries"
    if "chemical" in m or "pesticide" in m:
        return "Hazardous Chemicals"
    if "medical" in m or "biohazard" in m:
        return "Medical Waste"
    return material_type.strip().title() if material_type else "Mixed"


def match_recyclers(
    material_type: str,
    city: Optional[str] = None,
    user_lat: Optional[float] = None,
    user_lon: Optional[float] = None,
    hazardous: bool = False,
    limit: int = 3
) -> List[Dict]:
    recyclers = _load_recyclers()
    target_material = _normalize_material(material_type)

    # Filter by city if provided
    filtered = recyclers
    if city:
        city_lower = city.strip().lower()
        filtered = [r for r in recyclers if r.get("location", {}).get("city", "").lower() == city_lower]
        if not filtered:
            # Fallback to all cities if none match
            filtered = recyclers

    # Filter by hazardous if needed
    if hazardous:
        hazard_keywords = {"hazardous", "medical", "battery", "e-waste", "pesticide", "chemical"}
        filtered_h = []
        for r in filtered:
            materials = " ".join(r.get("materials", [])).lower()
            if any(k in materials for k in hazard_keywords):
                filtered_h.append(r)
        if filtered_h:
            filtered = filtered_h

    # Score by material match
    scored = []
    for r in filtered:
        materials = r.get("materials", [])
        material_match = any(target_material.lower() == m.lower() for m in materials)
        score = 1 if material_match else 0

        distance_km = None
        if user_lat is not None and user_lon is not None:
            loc = r.get("location", {})
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is not None and lon is not None:
                distance_km = _haversine_km(user_lat, user_lon, lat, lon)

        scored.append((score, distance_km, r))

    # Sort: material match first, then distance if available
    scored.sort(key=lambda x: (-x[0], x[1] if x[1] is not None else 1e9))

    results = []
    for _, distance_km, r in scored[:limit]:
        rate = None
        rates = r.get("rates", {})
        if target_material in rates:
            rate = rates.get(target_material)
        elif rates:
            # Fallback to best available rate for display if exact match not found
            try:
                rate = max(rates.values())
            except Exception:
                rate = list(rates.values())[0]

        loc = r.get("location", {})
        results.append({
            "id": r.get("id"),
            "name": r.get("name"),
            "address": r.get("address"),
            "materials": r.get("materials", []),
            "distance": round(distance_km, 2) if distance_km is not None else None,
            "rate": rate,
            "contact": r.get("contact", {}).get("phone"),
            "latitude": loc.get("latitude"),
            "longitude": loc.get("longitude")
        })

    return results
