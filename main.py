
from network import WLAN
import urequests as requests
import machine
import time
import _thread

import keys
import sound
import pir

# Config
INIT_DELAY = 60         # Delay to allow initialization of PIR Sensor. 60s according to docs.

SLEEP_DELAY = 60        # Time between every check if alarm has been enabled.

LOCKOUT = 10            # Lockout time after the sensor has been triggered to avoid multiple triggers of one event.


# Function for syncing the rtc via ntp
def sync_time():
    rtc = machine.RTC()

    while not rtc.synced():
        rtc.ntp_sync("se.pool.ntp.org")
        time.sleep(1)
        if not rtc.synced():
            print("Failed to sync time. Trying again...")

    #time.timezone(3600) # adjust for local time zone (Sweden Winter time)
    time.timezone(7200)  # adjust for local time zone (Sweden Summer time)
    print("Time synced to: " + readable_time(time.localtime()))


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
    r = requests.get(url=(keys.url + keys.sub), headers=keys.headers)
    state = int(r.json())
    return state


# Checks control variable on Ubidots and returns True or False
def alarm_enabled():
    if listen()==1:
        return True
    else:
        return False


# Motion detection function with PIR
def motion_detection():
        if pir.detection()==pir.motionDetected:
            trigger_time = time.time()
            print(readable_time(time.localtime()) + " [Motion Detected]")
            post_var("alarm_trigger", 0)                # make graph nice
            time.sleep(1)
            post_var("alarm_trigger", trigger_time)     # send data to UBIDOTS
            time.sleep(1)
            post_var("alarm_trigger", 0)                # reset alarm on ubidots to allow events to trigger
            time.sleep(LOCKOUT)                         # avoid multiple triggers of one event

        elif pir.detection()==pir.noMotionDetected:
            pass


# Function to make the pycom sleep while the alarm is disabled. Wakes regularly and checks switch.
def sleep_if_disabled():
    memory = 1

    while not alarm_enabled():
        if memory == 1:         # Audio confirmation that the alarm has been turned off.
            sound.play_mario_short()
            memory = 0

        post_var("status", 0)   # Publishes OFF state and sleeps for DISABLED_DELAY seconds.
        print(readable_time(time.localtime()) + " [Alarm OFF]")

        time.sleep(SLEEP_DELAY)

    if memory == 0:             # Audio confirmation that the alarm has been turned on.
        sound.play()

    post_var("status", 1)       # Publishes ON state
    print(readable_time(time.localtime()) + " [Alarm ON]")



### --- MAIN --- ###

# Syncing system clock
sync_time()

# Startup (mainly debugging)
if alarm_enabled():
    print("Initial state: [Alarm ON]")
else:
    print("Initial state: [Alarm OFF]")

print("Initializing PIR sensor... (" + str(INIT_DELAY) + " seconds)")
time.sleep(INIT_DELAY)
print("Starting up. \n")

# Motion detection loop
varv = 1        # Variable to keep track of loops
while True:
    motion_detection()

    if varv==100:
        # Subscribing and publishing to Ubidots server every 10 seconds
        sleep_if_disabled()
        varv = 1
    else:
        varv += 1

    time.sleep(0.1)
