import time
from services.vision_service import get_latest_frame, process_frame
from app.shared_frame import update_frames


def start_frame_worker():
    print("🚀 Frame worker started")

    while True:
        try:
            frame = get_latest_frame()

            if frame is None:
                time.sleep(0.01)
                continue

            processed, _, _ = process_frame(frame)

            update_frames(frame, processed)

        except Exception as e:
            print("🔥 Frame worker error:", e)
            time.sleep(0.05)