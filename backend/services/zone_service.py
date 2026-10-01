import json
from shapely.geometry import shape, Point
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR.parent / "data" / "wildlife_zones.geojson"

with open(FILE_PATH, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

zones = geojson_data["features"]


def get_all_zones():
    return geojson_data


def get_zones_for_location(lat, lon):
    point = Point(lon, lat)

    matched = []

    for zone in zones:
        polygon = shape(zone["geometry"])

        if polygon.contains(point):
            matched.append(zone["properties"])

    return matched