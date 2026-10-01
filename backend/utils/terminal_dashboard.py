import os

def display_dashboard(objects):
    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    print("🔥 STRAYGUARD LIVE DASHBOARD\n")

    print("+----------------+-----------+")
    print("| OBJECT         | DIST (m)  |")
    print("+----------------+-----------+")

    if not objects:
        print("| No objects detected        |")
        print("+----------------+-----------+")
        return

    for obj in objects:
        label = obj.get("label", "unknown")
        dist = obj.get("distance", 0)

        # simplify label categories
        if "person" in label:
            label = "person"
        elif "animal" in label:
            label = "animal"
        elif "vehicle" in label:
            label = "vehicle"
        else:
            label = "unknown"

        try:
            dist = f"{float(dist):.2f}"
        except:
            dist = "N/A"

        print(f"| {label:<14} | {dist:<9} |")

    print("+----------------+-----------+")