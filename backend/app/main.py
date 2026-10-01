from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel

import cv2
import json
import time

from services.vision_service import (
    start_yolo,
    get_latest_frame,
    get_latest_output,
    get_latest_collision
)

from services.zone_service import (
    get_all_zones,
    get_zones_for_location
)

from services.risk_service import analyze_route

from services.dashboard_service import (
    get_live_risk,
    get_route_dashboard,
    get_region_dashboard
)

from scripts.camera import Camera
from app.config import STREAM_URL

# 🔥 WebRTC import
from app.webrtc_server import offer


# -------------------------------
# 📍 GPS MODEL
# -------------------------------
class GPSData(BaseModel):
    lat: float
    lon: float


# -------------------------------
# 🛣️ ROUTE MODEL
# -------------------------------
class RouteRequest(BaseModel):
    route: list


# -------------------------------
# 📍 GPS STORAGE
# -------------------------------
current_location = {
    "lat": None,
    "lon": None,
    "timestamp": None
}


# -------------------------------
# 🚀 APP INIT
# -------------------------------
app = FastAPI(title="🚗 Accident Prevention API")

print("🚀 Starting Accident Prevention System...")

camera = Camera(STREAM_URL)

# 🔥 Start ONE AI thread only
start_yolo(camera)

print("✅ System Ready")


# -------------------------------
# BASIC ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"message": "🚗 Accident Prevention API Running"}


@app.get("/health")
def health():
    return {"status": "running"}


# -------------------------------
# 🌲 GET ALL WILDLIFE ZONES
# -------------------------------
@app.get("/zones")
def zones():
    return get_all_zones()


# -------------------------------
# 📍 LOCATION RISK CHECK
# -------------------------------
@app.get("/location-risk")
def location_risk(lat: float, lon: float):

    return {
        "zones": get_zones_for_location(lat, lon)
    }


# -------------------------------
# 🛣️ ROUTE RISK ANALYSIS
# -------------------------------
@app.post("/route-risk")
def route_risk(data: RouteRequest):

    return analyze_route(data.route)


# -------------------------------
# 📊 DASHBOARD LIVE RISK
# -------------------------------
@app.get("/dashboard/live-risk")
def dashboard_live_risk(lat: float, lon: float):

    return get_live_risk(lat, lon)


# -------------------------------
# 🛣️ DASHBOARD ROUTE RISK
# -------------------------------
@app.post("/dashboard/route-risk")
def dashboard_route_risk(data: RouteRequest):

    return get_route_dashboard(data.route)


# -------------------------------
# 🌍 DASHBOARD REGION RISK
# -------------------------------
@app.get("/dashboard/region-risk")
def dashboard_region_risk(region: str):

    return get_region_dashboard(region)


# -------------------------------
# 📍 GPS UPDATE API
# -------------------------------
@app.post("/gps")
def update_gps(data: GPSData):

    try:

        current_location["lat"] = data.lat
        current_location["lon"] = data.lon
        current_location["timestamp"] = time.time()

        print(f"📍 GPS UPDATE → {data.lat}, {data.lon}")

        return {"status": "ok"}

    except Exception as e:

        print(f"🔥 GPS ERROR: {e}")

        return {"error": "GPS update failed"}


# -------------------------------
# 📍 GET GPS
# -------------------------------
@app.get("/gps")
def get_gps():

    return current_location


# -------------------------------
# 🧠 LIVE DETECTION API
# -------------------------------
# -------------------------------
# 🧠 LIVE DETECTION API
# -------------------------------
@app.get("/live")
def live_detection():

    objects = get_latest_output()

    print("LIVE OBJECTS =>", objects)

    return {
        "online": True,
        "objects": objects,
        "collision": get_latest_collision(),
        "gps": current_location
    }

# -------------------------------
# 📡 SSE STREAM
# -------------------------------
@app.get("/stream")
def stream_detection():

    def event_stream():

        while True:

            try:

                frame = get_latest_frame()

                if frame is None:
                    time.sleep(0.1)
                    continue

                data = {
                    "objects": get_latest_output(),
                    "collision": get_latest_collision(),
                    "gps": current_location,
                    "timestamp": time.time()
                }

                yield f"data: {json.dumps(data)}\n\n"

                time.sleep(0.2)

            except Exception as e:

                print(f"🔥 STREAM ERROR: {e}")

                time.sleep(0.5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


# -------------------------------
# 🎥 MJPEG VIDEO STREAM
# -------------------------------
def generate_video():

    while True:

        try:

            frame = get_latest_frame()

            if frame is None:
                time.sleep(0.05)
                continue

            objects = get_latest_output()

            # Draw detections
            for obj in objects:

                x1, y1, x2, y2 = (
                    obj["x1"],
                    obj["y1"],
                    obj["x2"],
                    obj["y2"]
                )

                label = obj["label"]
                dist = obj["distance"]
                risk = obj["risk"]

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
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    f"{label} {dist:.1f}m",
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1
                )

            # GPS overlay
            if current_location["lat"] is not None:

                cv2.putText(
                    frame,
                    f"GPS: "
                    f"{current_location['lat']:.5f}, "
                    f"{current_location['lon']:.5f}",
                    (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )

            _, buffer = cv2.imencode(
                '.jpg',
                frame
            )

            frame_bytes = buffer.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n'
                + frame_bytes +
                b'\r\n'
            )

            time.sleep(0.03)

        except Exception as e:

            print(f"🔥 VIDEO ERROR: {e}")

            time.sleep(0.1)


@app.get("/video")
def video_feed():

    return StreamingResponse(
        generate_video(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )


# -------------------------------
# 🖥️ VIDEO UI
# -------------------------------
@app.get("/video-ui", response_class=HTMLResponse)
def video_ui():

    return """
    <html>
        <head>
            <title>Live Camera</title>
        </head>

        <body style="text-align:center; background:black;">

            <h2 style="color:white;">
                🚗 Live Detection Stream
            </h2>

            <img src="/video" width="720"/>

        </body>
    </html>
    """


# -------------------------------
# 🎥 WEBRTC SIGNALING
# -------------------------------
@app.post("/offer")
async def webrtc_offer(request: Request):

    return await offer(request)