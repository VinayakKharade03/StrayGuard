import cv2

class Camera:

    def __init__(self, stream_url):

        print(f"🔌 Connecting to: {stream_url}")

        # 🚀 USE FFMPEG FOR BETTER HTTP STREAMING
        self.cap = cv2.VideoCapture(
            stream_url,
            cv2.CAP_FFMPEG
        )

        # 🔄 FALLBACK
        if not self.cap.isOpened():

            print("⚠️ FFMPEG failed, trying default backend...")

            self.cap = cv2.VideoCapture(stream_url)

        if not self.cap.isOpened():
            raise Exception("❌ Camera connection failed")

        # 🚀 LOW LATENCY SETTINGS
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.cap.set(cv2.CAP_PROP_FPS, 24)

        print("✅ Camera connected")

    def get_frame(self):

        ret, frame = self.cap.read()

        if not ret or frame is None:
            return None

        # 🚀 RESIZE FOR FASTER PROCESSING
        frame = cv2.resize(frame, (640, 480))

        return frame

    def release(self):

        if self.cap:
            self.cap.release()