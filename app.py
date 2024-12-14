from flask import Flask, render_template, jsonify, request
import random
import time
from threading import Thread

app = Flask(__name__)

# Simulated detection data
test_data = [
    {"image": "/static/images/test_license_plate1.jpg", "license_plate": "VHK-1164"},
    {"image": "/static/images/Cars118.png", "license_plate": "JA62 UAR"},
    {"image": "/static/images/normal.jpg", "license_plate": "R96-0YR"},
    {"image": "/static/images/Cars1.png", "license_plate": "PG-MN112"}
]

# Detection state
detection_state = {
    "status": "No vehicle detected.",
    "image": "/static/images/NoVehicleDetected.jpg",
    "license_plate": "",
    "is_running": True
}

# Proximity Sensor Dummy Function
def check_proximity():
    detection_state["status"] = "Checking proximity sensor..."
    distance = random.uniform(0, 5)  # Random distance between 0 and 5 meters
    print(f"Sensor distance: {distance:.2f} meters")
    if distance <= 3:
        detection_state["status"] = "Vehicle detected."
        return True
    else:
        detection_state["status"] = "No vehicle detected."
        return False

# Camera Capture Dummy Function
def capture_image():
    detection_state["status"] = "Capturing image..."
    print("Simulating image capture")
    selected_data = random.choice(test_data)
    detection_state["image"] = selected_data["image"]
    return selected_data

# Processing Image Dummy Function
def process_image(image_path):
    detection_state["status"] = "Processing image..."
    print(f"Processing image: {image_path}")
    time.sleep(4)  # Simulate delay for processing
    selected_data = next((data for data in test_data if data["image"] == image_path), None)
    detection_state["license_plate"] = selected_data["license_plate"] if selected_data else "Unknown Plate"
    detection_state["status"] = f"License plate detected: {detection_state['license_plate']}"

# Simulated Gate Function
def move_servo():
    print("Opening the gate...")
    time.sleep(3)  # Simulate delay for opening gate
    print("Gate opened.")

def close_gate():
    print("Closing the gate...")
    move_servo()
    time.sleep(3)
    print("Gate closed.")

def open_gate():
    print("Opening the gate...")
    move_servo()
    time.sleep(3)
    print("Gate opened.")

def check_plate_in_database(license_plate):
    print(f"Checking database for license plate: {license_plate}")
    time.sleep(2)  # Simulate delay for database check
    return True


# Flow Controller Function
def main_flow():
    while True:
        if detection_state["is_running"]:
            detection_state["image"] = "/static/images/NoVehicleDetected.jpg"
            detection_state["license_plate"] = ""
            detection_state["status"] = "No vehicle detected."

            time.sleep(5)  # Simulate delay for waiting

            if check_proximity():
                time.sleep(2)  # Simulate delay for proximity check
                captured_data = capture_image()
                time.sleep(2)  # Simulate delay for capturing image
                process_image(captured_data["image"])
                time.sleep(8)  # Simulate additional processing
            else:
                print("No vehicle detected. Resetting.")
        else:
            detection_state["status"] = "Detection stopped."
            time.sleep(1)

# Start the flow controller in a background thread
Thread(target=main_flow, daemon=True).start()

# Flask Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(detection_state)

@app.route("/toggle-detection", methods=["POST"])
def toggle_detection():
    detection_state["is_running"] = request.json.get("isDetectionRunning", True)
    print(f"Detection {'started' if detection_state['is_running'] else 'stopped'}.")
    return jsonify({"status": detection_state["status"]})

if __name__ == "__main__":
    app.run(debug=True)