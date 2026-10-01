from shapely.geometry import Point, LineString, shape
from services.zone_service import zones


# ---------------------------------------------------
# 📍 LIVE GPS RISK
# ---------------------------------------------------
def get_live_risk(lat, lon):

    point = Point(lon, lat)

    nearby_zones = []

    risk_level = "LOW"
    recommended_speed = 80

    animals = []

    for zone in zones:

        polygon = shape(zone["geometry"])

        # inside zone
        if polygon.contains(point):

            props = zone["properties"]

            nearby_zones.append(props)

            # collect animals
            if "animals" in props:
                animals.extend(props["animals"])

            # risk escalation
            zone_risk = props.get("risk", "LOW")

            if zone_risk == "HIGH":
                risk_level = "HIGH"
                recommended_speed = min(
                    recommended_speed,
                    props.get("recommended_speed", 40)
                )

            elif zone_risk == "MEDIUM" and risk_level != "HIGH":
                risk_level = "MEDIUM"
                recommended_speed = min(
                    recommended_speed,
                    props.get("recommended_speed", 50)
                )

    animals = list(set(animals))

    return {
        "risk_level": risk_level,
        "recommended_speed": recommended_speed,
        "nearby_zones": nearby_zones,
        "animals": animals
    }


# ---------------------------------------------------
# 🛣️ ROUTE RISK ANALYSIS
# ---------------------------------------------------
def get_route_dashboard(route_coords):

    """
    route_coords format:
    [
        [lon, lat],
        [lon, lat]
    ]
    """

    route = LineString(route_coords)

    crossed_zones = []

    total_risk_score = 0

    recommended_speed = 80

    animals = []

    for zone in zones:

        polygon = shape(zone["geometry"])

        if route.intersects(polygon):

            props = zone["properties"]

            crossed_zones.append(props)

            if "animals" in props:
                animals.extend(props["animals"])

            risk = props.get("risk", "LOW")

            if risk == "HIGH":
                total_risk_score += 3

            elif risk == "MEDIUM":
                total_risk_score += 2

            else:
                total_risk_score += 1

            recommended_speed = min(
                recommended_speed,
                props.get("recommended_speed", 40)
            )

    # final risk level
    risk_level = "LOW"

    if total_risk_score >= 8:
        risk_level = "CRITICAL"

    elif total_risk_score >= 5:
        risk_level = "HIGH"

    elif total_risk_score >= 2:
        risk_level = "MEDIUM"

    animals = list(set(animals))

    return {
        "risk_level": risk_level,
        "crossed_zones": crossed_zones,
        "total_zones": len(crossed_zones),
        "recommended_speed": recommended_speed,
        "animals": animals
    }


# ---------------------------------------------------
# 🌍 REGION / DISTRICT RISK
# ---------------------------------------------------
def get_region_dashboard(region_name):

    region_name = region_name.lower()

    matched_zones = []

    animals = []

    high_risk_count = 0

    for zone in zones:

        props = zone["properties"]

        zone_name = props.get("name", "").lower()

        if region_name in zone_name:

            matched_zones.append(props)

            if "animals" in props:
                animals.extend(props["animals"])

            if props.get("risk") == "HIGH":
                high_risk_count += 1

    # overall risk
    risk_level = "LOW"

    if high_risk_count >= 5:
        risk_level = "CRITICAL"

    elif high_risk_count >= 3:
        risk_level = "HIGH"

    elif high_risk_count >= 1:
        risk_level = "MEDIUM"

    animals = list(set(animals))

    return {
        "region": region_name,
        "risk_level": risk_level,
        "total_zones": len(matched_zones),
        "zones": matched_zones,
        "dominant_animals": animals
    }