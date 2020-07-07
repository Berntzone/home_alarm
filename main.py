# Imported libraries
import urequests as requests
from machine import Pin
import machine
import time
# My own libraries to structure the code
import communicate_ubidots as ubi
import time_handler as tim3
import keys
import sound
import pir

# Config
INIT_DELAY = 60         # Delay to allow initialization of PIR Sensor. 60s according to docs.

SLEEP_DELAY = 60        # Time between every status update to Ubidots.


# Checks desired mode of device
def check_mode():                           # 0: Alarm turned off.
    mode = ubi.alarm_mode()                 # 1: Only sound. Mode for connecting smart lights to in the future.
    ubi.post("status", mode)                # 2: Silent Alarm mode. Only ubidots.
    print("[Status updated to Ubidots]")    # 3: Alarm fully armed. Both sound and ubidots.

                                            # Ubidots is notified of device mode.


## -- MAIN CODE -- ##


# Syncing system clock to the internet
tim3.sync_time()

# Startup
state = machine.disable_irq()               # Makes sure device can't be interrupted by PIR.
print("Initializing PIR sensor... (" + str(INIT_DELAY) + " seconds)")
time.sleep(INIT_DELAY)
print("Starting up. \n")
machine.enable_irq(state)                   # Allow interruption again.


while True:

    check_mode()                    # Checks mode on ubidots and updates device status.

    time.sleep(SLEEP_DELAY)         # Sleeps for SLEEP_DELAY seconds or until interrupted by PIR.
