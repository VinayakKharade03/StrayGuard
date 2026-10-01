import cv2

def detect_unknown(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    unknowns = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 1500:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        if w > frame.shape[1]*0.8 and h > frame.shape[0]*0.8:
            continue

        aspect_ratio = w / float(h)

        if aspect_ratio < 0.3 or aspect_ratio > 3:
            unknowns.append((x, y, x+w, y+h, area))
        else:
            if 1500 < area < 50000:
                unknowns.append((x, y, x+w, y+h, area))

    return unknowns


# 🔥 ADD THIS FUNCTION (missing one)
def unknown_object_shape(w, h):
    ratio = w / float(h)

    if ratio > 1.5:
        return "WIDE"
    elif ratio < 0.5:
        return "TALL"
    else:
        return "NORMAL"