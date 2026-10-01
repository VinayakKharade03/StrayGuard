from app.config import REAL_HEIGHTS, FOCAL_LENGTH, DANGER_DIST, WARNING_DIST

distance_memory = {}

def get_distance(label, h, oid):
    if h <= 0:
        return 999

    real_h = REAL_HEIGHTS.get(label, 100)
    raw = (real_h * FOCAL_LENGTH) / h / 100

    if oid not in distance_memory:
        distance_memory[oid] = raw

    dist = 0.7 * distance_memory[oid] + 0.3 * raw
    distance_memory[oid] = dist

    return dist


def get_risk(dist):
    if dist < DANGER_DIST:
        return "DANGER", (0, 0, 255)
    elif dist < WARNING_DIST:
        return "WARNING", (0, 255, 255)
    return "SAFE", (0, 255, 0)