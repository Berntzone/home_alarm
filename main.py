
from network import WLAN
import urequests as requests
import machine
import time
#import _thread         # Tried at first, but realized MicroPython's multithread functionality is "highly experimental"
                        # and couldn't do what I wanted. 3/10 would not recommend. Unpleasant experience.
                        # https://docs.micropython.org/en/latest/library/_thread.html
import keys
import sound
import pir

# Config
INIT_DELAY = 60         # Delay to allow initialization of PIR Sensor. 60s according to docs.

SUB_DELAY = 10          # Time between every check if alarm has been enabled. Want pretty short to be able to
                        # turn off alarm when you get home and dont want to wait for a long time.

PUB_DELAY = 60          # Delay in seconds between every time the device posts its status to ubidots.

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
    print("Time synced to: " + neat_time(time.localtime()))


# Convert time tuple from time.localtime() to more readable format.
def neat_time(input):
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

    return str(year + "-" + month + "-" + day + " " + hour + ":" + minute)


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
def listen(topic):
    r = requests.get(url=(keys.url + topic), headers=keys.headers)
    state = int(r.json())
    return state


# Checks control variable on Ubidots and returns True or False
def alarm_enabled():
    if listen(keys.sub)==1:
        return True
    else:
        return False


# Motion detection function with PIR
def motion_detection():
        if pir.detection()==pir.motionDetected:
            trigger_time = time.time()
            print(neat_time(time.localtime()) + " [Motion Detected]")

            post_var("alarm_trigger", 0)                # Ugly code, but makes graph on ubidots nice :)
            time.sleep(1)
            post_var("alarm_trigger", trigger_time)     # Send data to UBIDOTS.
            time.sleep(1)
            post_var("alarm_trigger", 0)                # Reset alarm on ubidots to allow events to trigger.

            time.sleep(LOCKOUT)                         # Avoid multiple triggers of one event

        elif pir.detection()==pir.noMotionDetected:
            pass


# Function to make the pycom sleep while the alarm is disabled. Wakes regularly and checks switch.
def sleep_if_disabled():
    memory = 1
    j = 1

    while not alarm_enabled():

        if memory == 1:                                 # Audio confirmation that the alarm has been turned off.
            sound.play_mario_short()
            memory = 0

        if j == (PUB_DELAY/10):
            post_var("status", 0)                       # Publishes OFF state every 60 seconds when off.
            print(neat_time(time.localtime()) + " [Alarm OFF]")
            j = 1
        else:
            j += 1

        time.sleep(SUB_DELAY)                           # sleeps for SLEEP_DELAY seconds.

    if memory == 0:                                     # Audio confirmation that the alarm has been turned on.
        sound.play()




### --- MAIN --- ###

# Syncing system clock to the internet
sync_time()


# Startup (mainly debugging)
if alarm_enabled():
    print("Initial state: [Alarm ON]")
else:
    print("Initial state: [Alarm OFF]")

print("Initializing PIR sensor... (" + str(INIT_DELAY) + " seconds)")
time.sleep(INIT_DELAY)
print("Starting up. \n")


# Alarm loop
i = 1
while True:
    motion_detection()

    if i%(10*10)==0:                                    # Subscribing to Ubidots server every 10 seconds. (Limit: every 2s)
        sleep_if_disabled()                             # Enters sleep loop if state is disabled.

    if i==(10*PUB_DELAY):                                      # Publishes ON state every 60 seconds when on.
        post_var("status", 1)                           # Ubidots STEM has publishing limit of 4000 dots/day (every 22s)
        print(neat_time(time.localtime()) + " [Alarm ON]")
        i = 1
    else:
        i += 1
    time.sleep(0.1)
