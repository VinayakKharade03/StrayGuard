from app.config import *

class Tracker:
    def __init__(self):
        self.objects = {}
        self.next_id = 0

    def update(self, detections):
        updated = {}

        for cx, cy in detections:
            matched = None

            for oid, (ox, oy, lost) in self.objects.items():
                if abs(cx - ox) < MAX_TRACK_DIST and abs(cy - oy) < MAX_TRACK_DIST:
                    matched = oid
                    break

            if matched is not None:
                updated[matched] = (cx, cy, 0)
            else:
                updated[self.next_id] = (cx, cy, 0)
                self.next_id += 1

        for oid, (ox, oy, lost) in self.objects.items():
            if oid not in updated and lost < MAX_LOST:
                updated[oid] = (ox, oy, lost + 1)

        self.objects = updated
        return updated