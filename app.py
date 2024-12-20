from flask import Flask, render_template, jsonify, request, send_from_directory
import random
import time
from threading import Thread, Lock
import os
import RPi.GPIO as GPIO
import logging

app = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# GPIO Configuration
SERVO_PIN = 11  # BOARD numbering
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Initialize PWM on the servo pin at 50Hz
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)  # Initialize with 0 duty cycle

# Lock for thread-safe GPIO operations
gpio_lock = Lock()

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
    logging.info(f"Sensor distance: {distance:.2f} meters")
    if distance <= 3:
        detection_state["status"] = "Vehicle detected."
        return True
    else:
        detection_state["status"] = "No vehicle detected."
        return False

# Camera Capture Dummy Function
def capture_image():
    detection_state["status"] = "Capturing image..."
    logging.info("Simulating image capture")
    selected_data = random.choice(test_data)
    detection_state["image"] = selected_data["image"]
    return selected_data

# Processing Image Dummy Function
def process_image(image_path):
    detection_state["status"] = "Processing image..."
    logging.info(f"Processing image: {image_path}")
    time.sleep(4)  # Simulate delay for processing
    selected_data = next((data for data in test_data if data["image"] == image_path), None)
    detection_state["license_plate"] = selected_data["license_plate"] if selected_data else "Unknown Plate"
    detection_state["status"] = f"License plate detected: {detection_state['license_plate']}"

# Servo Control Functions
def set_servo_angle(angle):
    """
    Sets the servo to the specified angle.
    Angle should be between 0 and 180 degrees.
    """
    duty = 2 + (angle / 18)  # Convert angle to duty cycle
    with gpio_lock:
        servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Wait for servo to move
    with gpio_lock:
        servo_pwm.ChangeDutyCycle(0)  # Stop sending signal to prevent jitter

def open_gate():
    logging.info("Opening the gate...")
    set_servo_angle(90)  # Adjust angle as per your servo's configuration
    logging.info("Gate opened.")

def close_gate():
    logging.info("Closing the gate...")
    set_servo_angle(0)  # Adjust angle as per your servo's configuration
    logging.info("Gate closed.")

def check_plate_in_database(license_plate):
    logging.info(f"Checking database for license plate: {license_plate}")
    time.sleep(2)  # Simulate delay for database check
    # Implement actual database check logic here
    # For demonstration, we'll assume all plates are valid
    return True

# Flow Controller Function
def main_flow():
    while True:
        if detection_state["is_running"]:
            with gpio_lock:
                detection_state["image"] = "/static/images/NoVehicleDetected.jpg"
                detection_state["license_plate"] = ""
                detection_state["status"] = "No vehicle detected."

            time.sleep(5)  # Simulate delay for waiting

            if check_proximity():
                time.sleep(2)  # Simulate delay for proximity check
                captured_data = capture_image()
                time.sleep(2)  # Simulate delay for capturing image
                process_image(captured_data["image"])
                time.sleep(1)  # Short delay before checking database

                # Check license plate in database
                if check_plate_in_database(detection_state["license_plate"]):
                    open_gate()
                    time.sleep(2)  # Short delay before checking database
                    close_gate()

                else:
                    logging.warning("License plate not recognized. Gate remains closed.")
            else:
                logging.info("No vehicle detected. Resetting.")
        else:
            with gpio_lock:
                detection_state["status"] = "Detection stopped."
            time.sleep(1)

# Start the flow controller in a background thread
flow_thread = Thread(target=main_flow, daemon=True)
flow_thread.start()

# Flask Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/data", methods=["GET"])
def get_data():
    with gpio_lock:
        return jsonify(detection_state)

@app.route("/toggle-detection", methods=["POST"])
def toggle_detection():
    with gpio_lock:
        detection_state["is_running"] = request.json.get("isDetectionRunning", True)
        logging.info(f"Detection {'started' if detection_state['is_running'] else 'stopped'}.")
        return jsonify({"status": detection_state["status"]})

# Cleanup GPIO on application exit
def cleanup_gpio():
    logging.info("Cleaning up GPIO...")
    servo_pwm.stop()
    GPIO.cleanup()
    logging.info("GPIO cleanup complete.")

import atexit
atexit.register(cleanup_gpio)

if __name__ == "__main__":
    try:
        app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        logging.info("Application interrupted by user.")
    finally:
        cleanup_gpio()
