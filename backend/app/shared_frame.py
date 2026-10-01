import threading

lock = threading.Lock()

latest_raw_frame = None
latest_processed_frame = None


def update_frames(raw, processed):
    global latest_raw_frame, latest_processed_frame
    with lock:
        latest_raw_frame = raw
        latest_processed_frame = processed


def get_processed_frame():
    with lock:
        return latest_processed_frame


def get_raw_frame():
    with lock:
        return latest_raw_frame