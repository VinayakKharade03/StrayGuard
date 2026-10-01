position_memory = {}

def get_movement(oid, cx, cy):
    movement = "STATIC"

    if oid in position_memory:
        px, py = position_memory[oid]
        if abs(cx - px) > 10 or abs(cy - py) > 10:
            movement = "MOVING"

    position_memory[oid] = (cx, cy)
    return movement