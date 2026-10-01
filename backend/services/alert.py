import requests
from app.config import ALERT_URL

def send_alert(label, distance):
    try:
        requests.post(
            ALERT_URL,
            json={
                "object": label,
                "distance": distance
            },
            timeout=0.5   # 🔥 faster, no blocking
        )
    except:
        pass