history = {}

def update_trajectory(obj_id, cx, cy):
    if obj_id not in history:
        history[obj_id] = []

    history[obj_id].append((cx, cy))

    if len(history[obj_id]) > 10:
        history[obj_id].pop(0)

def predict_collision(obj_id, frame_center_x):
    points = history.get(obj_id, [])
    if len(points) < 3:
        return False

    dx = points[-1][0] - points[0][0]

    # moving towards center
    if abs(points[-1][0] - frame_center_x) < 80 and abs(dx) > 10:
        return True

    return False