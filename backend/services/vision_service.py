import cv2
import threading
import time

from core.detector import Detector
from core.tracker import Tracker
from core.trajectory import (
    update_trajectory,
    predict_collision
)

from utils.distance import (
    get_distance,
    get_risk
)

from utils.geometry import centroid
from utils.unknown import unknown_object_shape
from utils.terminal_dashboard import display_dashboard

from app.config import *

detector = Detector()
tracker = Tracker()

lock = threading.Lock()

# ---------------------------------
# CACHED DATA
# ---------------------------------
last_frame = None
last_processed_frame = None

last_output = []
last_collision = False

last_display_time = 0
DISPLAY_INTERVAL = 0.5


# ---------------------------------
# YOLO THREAD
# ---------------------------------
def start_yolo(camera):

    def yolo_thread():

        global last_frame
        global last_processed_frame

        global last_output
        global last_collision

        global last_display_time

        while True:

            try:

                frame = camera.get_frame()

                if frame is None:
                    time.sleep(0.01)
                    continue

                frame = cv2.resize(
                    frame,
                    (FRAME_W, FRAME_H)
                )

                # original frame
                clean_frame = frame.copy()

                # frame for drawing
                processed_frame = frame.copy()

                small = cv2.resize(
                    frame,
                    (320, 240)
                )

                results = detector.model(
                    small,
                    imgsz=320,
                    conf=CONFIDENCE,
                    device=0,
                    max_det=5,
                    verbose=False,
                    amp=True
                )

                detections = []
                meta = []

                for r in results:

                    for box in r.boxes:

                        conf = float(box.conf[0])

                        if conf < CONFIDENCE:
                            continue

                        cls = int(box.cls[0])

                        label = detector.model.names[cls]

                        x1, y1, x2, y2 = map(
                            int,
                            box.xyxy[0]
                        )

                        # scale 320→640
                        x1 *= 2
                        y1 *= 2
                        x2 *= 2
                        y2 *= 2

                        h = max(y2 - y1, 20)
                        w = x2 - x1

                        # ignore garbage detections
                        if (
                            w > FRAME_W * 0.9
                            and
                            h > FRAME_H * 0.9
                        ):
                            continue

                        cx, cy = centroid(
                            x1,
                            y1,
                            x2,
                            y2
                        )

                        detections.append((cx, cy))

                        meta.append((
                            x1,
                            y1,
                            x2,
                            y2,
                            label,
                            h,
                            w,
                            cx,
                            cy
                        ))

                tracked = tracker.update(
                    detections
                )

                output = []
                collision = False

                for item in meta:

                    (
                        x1,
                        y1,
                        x2,
                        y2,
                        label,
                        h,
                        w,
                        cx,
                        cy
                    ) = item

                    oid = None

                    for tid, (
                        tx,
                        ty,
                        _
                    ) in tracked.items():

                        if (
                            abs(cx - tx) < 25
                            and
                            abs(cy - ty) < 25
                        ):
                            oid = tid
                            break

                    if oid is None:
                        continue

                    dist = get_distance(
                        label,
                        h,
                        oid
                    )

                    update_trajectory(
                        oid,
                        cx,
                        cy
                    )

                    risk, _ = get_risk(dist)

                    if predict_collision(
                        oid,
                        FRAME_W // 2
                    ):
                        risk = "COLLISION PATH"
                        collision = True

                    if dist < 3:
                        risk = "COLLISION"
                        collision = True

                    category = CLASS_MAP.get(
                        label,
                        "unknown"
                    )

                    if category == "unknown":
                        label = (
                            f"UNKNOWN-"
                            f"{unknown_object_shape(w, h)}"
                        )

                    output.append({

                        "id": oid,
                        "label": label,

                        "distance": float(dist),

                        "risk": risk,

                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2)
                    })

                    # ---------------------------------
                    # DRAW ON FRAME ONLY ONCE
                    # ---------------------------------

                    color = (0, 255, 0)

                    if risk == "WARNING":
                        color = (0, 255, 255)

                    elif risk in [
                        "DANGER",
                        "COLLISION",
                        "COLLISION PATH"
                    ]:
                        color = (0, 0, 255)

                    cv2.rectangle(
                        processed_frame,
                        (x1, y1),
                        (x2, y2),
                        color,
                        2
                    )

                    cv2.putText(
                        processed_frame,
                        f"{label} {dist:.1f}m",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1
                    )

                with lock:

                    last_frame = clean_frame

                    last_processed_frame = processed_frame

                    last_output = output

                    last_collision = collision

                # terminal dashboard
                if (
                    time.time()
                    - last_display_time
                    > DISPLAY_INTERVAL
                ):

                    display_dashboard(output)

                    last_display_time = time.time()

            except Exception as e:

                print(
                    f"🔥 YOLO THREAD ERROR: {e}"
                )

            time.sleep(0.005)

    threading.Thread(
        target=yolo_thread,
        daemon=True
    ).start()


# ---------------------------------
# GETTERS
# ---------------------------------
def get_latest_frame():

    with lock:

        return (
            None
            if last_frame is None
            else last_frame.copy()
        )


def get_latest_processed_frame():

    with lock:

        return (
            None
            if last_processed_frame is None
            else last_processed_frame.copy()
        )


def get_latest_output():

    with lock:

        return last_output.copy()


def get_latest_collision():

    with lock:

        return last_collision