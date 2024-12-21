from flask import Flask, render_template, jsonify, request, send_from_directory
import random
import time
from threading import Thread, Lock
import os
import RPi.GPIO as GPIO
import logging
import atexit
from picamera2 import Picamera2
import datetime

app = Flask(__name__)

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

# GPIO Configuration using BCM numbering
SERVO_PIN = 17  # BCM GPIO 17 (BOARD Pin 11)
TRIG = 11       # BCM GPIO 11 (BOARD Pin 23)
ECHO = 8        # BCM GPIO 8  (BOARD Pin 24)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Initialize PWM on the servo pin at 50Hz
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)  # Initialize with 0 duty cycle

# Initialize TRIG to LOW
GPIO.output(TRIG, False)
time.sleep(0.1)  # Short delay to stabilize

# Lock for thread-safe GPIO operations
gpio_lock = Lock()

# Initialize Picamera2
picam2 = Picamera2()
picam2.start()

# Simulated detection data (can be removed if using real images)
test_data = [
    {"image": "/static/images/test_license_plate1.jpg", "license_plate": "VHK-1164"},
    {"image": "/static/images/Cars118.png", "license_plate": "JA62 UAR"},
    {"image": "/static/images/normal.jpg", "license_plate": "R96-0YR"},
    {"image": "/static/images/Cars1.png", "license_plate": "PG-MN112"}
]

# Known license plates for simulation
known_plates = {"VHK-1164", "JA62 UAR", "R96-0YR", "PG-MN112"}

# Detection state
detection_state = {
    "status": "No vehicle detected.",
    "image": "/static/images/NoVehicleDetected.jpg",
    "license_plate": "",
    "plate_known": False,
    "gate_status": "Gate Closed",
    "is_running": True
}

# Real Proximity Sensor Function
def measure_distance():
    """
    Measures the distance using an ultrasonic sensor.
    Returns distance in meters if successful, otherwise None.
    """
    with gpio_lock:
        GPIO.output(TRIG, False)
    time.sleep(0.1)  # Short delay to stabilize

    with gpio_lock:
        GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10 microseconds
    with gpio_lock:
        GPIO.output(TRIG, False)

    pulse_start = None
    pulse_end = None

    # Start time for timeout
    start_time = time.time()

    # Wait for ECHO to go HIGH
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - start_time > 1:
            logging.warning("Timeout waiting for ECHO to go HIGH")
            return None

    # Reset start_time for the next timeout
    start_time = time.time()

    # Wait for ECHO to go LOW
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - start_time > 1:
            logging.warning("Timeout waiting for ECHO to go LOW")
            return None

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start
    logging.debug(f"Pulse duration: {pulse_duration} seconds")

    # Calculate distance (speed of sound = 34300 cm/s)
    distance_cm = pulse_duration * 17150  # 17150 = 34300 / 2
    distance_cm = round(distance_cm, 2)
    distance_m = distance_cm / 100  # Convert to meters
    logging.info(f"Measured Distance: {distance_m} meters")
    return distance_m


# Replace Dummy Proximity Sensor Function with Real Function
def capture_image():
    detection_state["status"] = "Capturing image..."
    logging.info("Starting image capture")

    # Generate a unique filename based on the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"car_{timestamp}.jpg"
    filepath = os.path.join("static", "images", filename)

    try:
        # Capture the image and save it to the specified filepath
        picam2.capture_file(filepath)
        logging.info(f"Image captured and saved as {filename}")

        # Update the detection state with the new image path
        detection_state["image"] = f"/static/images/{filename}"

        # For demonstration, randomly assign a license plate (remove if using actual OCR)
        selected_data = random.choice(test_data)
        # detection_state["license_plate"] = selected_data["license_plate"]
        return selected_data
    except Exception as e:
        logging.error(f"Error capturing image: {e}")
        detection_state["status"] = "Image capture failed."
        return None
# Processing Image Dummy Function
def process_image(image_path):
    detection_state["status"] = "Processing image..."
    logging.info(f"Processing image: {image_path}")
    time.sleep(4)  # Simulate delay for processing

    # Simulate license plate recognition (replace with actual OCR in production)
    selected_data = next((data for data in test_data if data["image"] == image_path), None)
    detection_state["license_plate"] = selected_data["license_plate"] if selected_data else "Unknown Plate"

    # Check if the plate is known
    detection_state["plate_known"] = detection_state["license_plate"] in known_plates
    plate_status = "Known" if detection_state["plate_known"] else "Unknown"
    detection_state["status"] = f"License plate detected: {detection_state['license_plate']} ({plate_status})"
    logging.info(f"License plate status: {plate_status}")

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
    with gpio_lock:
        detection_state["gate_status"] = "Gate Opening"
    set_servo_angle(90)  # Adjust angle as per your servo's configuration
    with gpio_lock:
        detection_state["gate_status"] = "Gate Opened"
    logging.info("Gate opened.")

def close_gate():
    logging.info("Closing the gate...")
    with gpio_lock:
        detection_state["gate_status"] = "Gate Closing"
    set_servo_angle(0)  # Adjust angle as per your servo's configuration
    with gpio_lock:
        detection_state["gate_status"] = "Gate Closed"
    logging.info("Gate closed.")

def check_plate_in_database(license_plate):
    logging.info(f"Checking database for license plate: {license_plate}")
    time.sleep(2)  # Simulate delay for database check
    # Implement actual database check logic here
    # For demonstration, we'll assume all plates in known_plates are valid
    is_known = license_plate in known_plates
    if is_known:
        logging.info(f"License plate {license_plate} is known.")
    else:
        logging.warning(f"License plate {license_plate} is unknown.")
    return is_known

# Flow Controller Function
def main_flow():
    while True:
        if detection_state["is_running"]:
            with gpio_lock:
                detection_state["image"] = "/static/images/NoVehicleDetected.jpg"
                detection_state["license_plate"] = ""
                detection_state["plate_known"] = False
                detection_state["status"] = "No vehicle detected."
                detection_state["gate_status"] = "Gate Closed"

            time.sleep(5)  # Simulate delay for waiting

            distance = measure_distance()
            if distance is not None:
                # logging.info(f"Measured Distance: {distance} meters")
                if distance <= 0.2:  # Threshold distance in meters
                    detection_state["status"] = "Vehicle detected."
                    time.sleep(2)  # Simulate delay for proximity check
                    captured_data = capture_image()
                    if captured_data:
                        time.sleep(2)  # Simulate delay for capturing image
                        process_image(captured_data["image"])
                        time.sleep(1)  # Short delay before checking database

                        # Check license plate in database
                        if check_plate_in_database(detection_state["license_plate"]):
                            open_gate()
                            time.sleep(2)  # Short delay before closing gate
                            close_gate()
                        else:
                            logging.warning("License plate not recognized. Gate remains closed.")
                            with gpio_lock:
                                detection_state["gate_status"] = "Gate Closed - Unknown Plate"
                else:
                    detection_state["status"] = "No vehicle detected."
                    logging.info("No vehicle within threshold distance.")
            else:
                detection_state["status"] = "Proximity sensor error."
                logging.warning("Failed to measure distance.")
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
        return jsonify({
            "status": detection_state["status"],
            "gate_status": detection_state["gate_status"],
            "license_plate": detection_state["license_plate"],
            "plate_known": detection_state["plate_known"],
            "image": detection_state["image"]
        })

# Cleanup GPIO and Camera on application exit
def cleanup_resources():
    logging.info("Cleaning up resources...")
    servo_pwm.stop()
    GPIO.cleanup()
    picam2.stop()
    logging.info("GPIO and Camera cleanup complete.")

atexit.register(cleanup_resources)

if __name__ == "__main__":
    try:
        app.run(debug=False, use_reloader=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        logging.info("Application interrupted by user.")
    finally:
        cleanup_resources()
