
from network import WLAN
import urequests as requests
import machine
import time
import _thread

import keys
import sound
import pir

print("Starting up")

#config
INIT_DELAY = 60 # Delay to allow initialization of PIR Sensor
STATUS_DELAY = 10  # Delay in seconds between every status update to Ubidots
CHECK_DELAY = 10  # Time between every check for updated on/off state
LOCKOUT = 10 # Lockout time after the sensor has been triggered to avoid multiple triggers of one event
ON_OFF = True # Variable to be able to control the device from Ubidots dashboard.

# Function for syncing the rtc via ntp
def sync_time():
    rtc = machine.RTC()
    while not rtc.synced():
        rtc.ntp_sync("se.pool.ntp.org")
        time.sleep(1)
        if not rtc.synced():
            print("Failed to sync time. Trying again...")
    #time.timezone(3600) # adjust for local time zone (Sweden Winter time)
    time.timezone(7200) # adjust for local time zone (Sweden Summer time)
    print("Time synced to: " + str(time.localtime()))

#convert time tuple from time.localtime() to more readable format.
def readable_time(input):
    year = str(input[0])
    month = str(input[1])
    day = str(input[2])

    if input[3] < 10:
        hour = "0" + str(input[3])
    else:
        hour = str(input[3])

    if input[4] < 10:
        minute = "0" + str(input[4])
    else:
        minute = str(input[4])
    output = str(year + "-" + month + "-" + day + " " + hour + ":" + minute)
    return output

# Builds the json to send the request
def build_json(variable, value):
    try:
        # data array creation
        data = {variable: {"value": value}}
                # Context can be added inside of variables if desired
                # ,"context": {"lat": 13.37, "lng": 73.31} for example
        return data
    except:
        return None

# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post_var(topic, value):
    try:
        data = build_json(topic, value)
        if data is not None:
            req = requests.post(url=(keys.url + keys.pub), headers=keys.headers, json=data) # include data as JSON object
            return req.json()
        else:
            print("ERROR: No data available.")
            pass
    except:
        print("ERROR: Can't send data to Ubidots.")
        pass

# Function for listening for commands from the Ubidots server
def listen():
    #print("Listening...")
    r = requests.get(url=(keys.url + keys.sub), headers=keys.headers)
    state = int(r.json())
    return state

# Function for letting the server know alarm status
def status():
    while True:
        if ON_OFF:
            post_var("status", 1)
        else:
            post_var("status", 0)
        time.sleep(STATUS_DELAY)

# Motion detection function with PIR
def motion_detection():
    while ON_OFF:
        if pir.detection()==pir.motionDetected:
            trigger_time = time.time()
            print(readable_time(time.localtime()) + " Motion Detected!")
            post_var("alarm_trigger", trigger_time)  # send data to UBIDOTS
            sound.play_mario_short()
            time.sleep(LOCKOUT) # avoid multiple triggers of one event
        elif pir.detection()==pir.noMotionDetected:
            pass
        time.sleep(0.1)

        # Call function to check Ubidots if alarm has been turned OFF
        switch = listen()
        if switch==0:
            print("Alarm turned OFF")
            time.sleep(5)
            break


### --- Main --- ###
sync_time()
print("Initializing PIR sensor.")
if ON_OFF:
    print("State: ON")
else:
    print("State: OFF")
time.sleep(INIT_DELAY)

# Thread which updates Ubidots on state of Alarm ("Did it turn off or not?")
# This signal updates every STATUS_DELAY seconds, which also functions as a way
# of knowing if the alarm has been tampered with or powered down
_thread.start_new_thread(status, ())

while True:
    # Call function to check Ubidots if alarm is turned ON or OFF
    switch = listen()
    if switch==1:
        ON_OFF = True
        print("Starting Detection")
    elif switch==0:
        ON_OFF = False

    # Calling motion detection function, which runs as long as ON_OFF is True
    motion_detection()
    
    time.sleep(CHECK_DELAY)
