# Import libraries
import RPi.GPIO as GPIO
import time


# Set GPio numbering mode
GPIO.setmode(GPIO.BOARD)

#set pin 11 as an onput , and set servo as pin 11 as PWM
GPIO.setup(11,GPIO.OUT)
servo1 = GPIO.PWM(11,50) # Note 11 is pin , 50 = 50HZ pulses

#start PWM running but with value of 0 (pulse off)
servo1.start(0)
print ("Waiting 2 sec")
time.sleep(6)

#Let's move the servo
print ("Rotating 180 degree in 10 step")

#define variable Duty
duty = 2
# loop for duty values from 2 to 12 (0 to 180 degrees)
while duty <= 7:
    servo1.ChangeDutyCycle(duty)
    time.sleep(.1)
    duty = duty + 1
     
# wait a couple of seconds
time.sleep(2)

# Turn back to 90 degree
print("Turning back to 90 degree for 2 seconds")
servo1.ChangeDutyCycle(7)
time.sleep(2)


# Turn back to 90 degree
#print("Turning back to 0 degree for 2 seconds")
servo1.ChangeDutyCycle(2)
time.sleep(1)
servo.ChangeDutyCycle(0)

#Clesn things up at the end
servo1.stop()
GPIO.cleanup()
print ("Goodbye")