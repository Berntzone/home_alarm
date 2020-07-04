from machine import Pin

# Config of the PIR Sensor
motionDetected = 1
noMotionDetected = 0
hold_time_sec = 0.1

detection = Pin('P4',mode=Pin.IN)
