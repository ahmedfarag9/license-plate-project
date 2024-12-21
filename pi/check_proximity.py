import RPi.GPIO as GPIO
import time

# Define GPIO pins based on BCM numbering
TRIG = 11  # BCM GPIO 11 (Physical Pin 23)
ECHO = 8   # BCM GPIO 8  (Physical Pin 24)

# Set GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Ensure TRIG is low
    GPIO.output(TRIG, False)
    time.sleep(0.1)  # Short delay to stabilize

    # Send a 10us pulse to TRIG to start measurement
    print("Sending trigger pulse")
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(TRIG, False)

    pulse_start = None
    pulse_end = None

    # Start time for timeout
    start_time = time.time()

    # Wait for ECHO to go HIGH
    print("Waiting for ECHO to go HIGH")
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - start_time > 1:
            print("Timeout waiting for ECHO to go HIGH")
            return None

    # Reset start_time for the next timeout
    start_time = time.time()

    # Wait for ECHO to go LOW
    print("Waiting for ECHO to go LOW")
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - start_time > 1:
            print("Timeout waiting for ECHO to go LOW")
            return None

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start
    print(f"Pulse duration: {pulse_duration} seconds")

    # Calculate distance (speed of sound = 34300 cm/s)
    distance = pulse_duration * 17150  # 17150 = 34300 / 2
    distance = round(distance, 2)
    return distance

try:
    print("Waiting for sensor to settle")
    time.sleep(2)  # Allow sensor to settle

    distance = measure_distance()
    if distance is not None:
        print(f"Distance: {distance} cm")
    else:
        print("Failed to measure distance")

except KeyboardInterrupt:
    print("Measurement stopped by User")

finally:
    GPIO.cleanup()