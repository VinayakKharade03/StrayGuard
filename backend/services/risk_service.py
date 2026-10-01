from shapely.geometry import LineString, shape
from services.zone_service import zones


def analyze_route(route_coords):
    """
    route_coords:
    [
        [lon, lat],
        [lon, lat]
    ]
    """

    route = LineString(route_coords)

    crossed_zones = []

    for zone in zones:
        polygon = shape(zone["geometry"])

        if route.intersects(polygon):
            crossed_zones.append(zone["properties"])

    risk_level = "LOW"

    if len(crossed_zones) >= 3:
        risk_level = "CRITICAL"
    elif len(crossed_zones) == 2:
        risk_level = "HIGH"
    elif len(crossed_zones) == 1:
        risk_level = "MEDIUM"

    return {
        "risk_level": risk_level,
        "danger_zones": crossed_zones,
        "total_zones": len(crossed_zones)
    }