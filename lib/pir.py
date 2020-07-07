import machine
import time
from machine import Pin

import communicate_ubidots as ubi
import time_handler as tim3
import sound

# Config of the PIR Sensor
LOCKOUT_TIME = 10                    # Lockout time after the sensor has been triggered to avoid multiple triggers of one event.
                                     # At least 2.2 seconds so we don't check ubidots too often.


# Function that runs when PIR is triggered (interruption)
def call_back(arg):
    mode = ubi.alarm_mode()

    if mode==1:
        sound.play()                # Mode for connecting smart lights to in the future.

    elif mode==2:
        post_trigger_to_ubi()       # Silent Alarm mode
        time.sleep(0.5)

    elif mode==3:
        post_trigger_to_ubi()       # Alarm fully armed
        sound.play_mario()

    else:
        pass                        # Alarm turned off (mode==0)

    state = machine.disable_irq()
    time.sleep(LOCKOUT_TIME)
    machine.enable_irq(state)

# Interrupt config
P4 = machine.Pin('P4', Pin.IN)
irq_P4 = P4.callback(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=call_back)


# Post a trigger event to Ubidots
def post_trigger_to_ubi():
    trigger_time = time.time()
    print( tim3.present(time.localtime()) + " [Motion Detected]" )

    ubi.post("alarm_trigger", 0)
    time.sleep(1)
    ubi.post("alarm_trigger", trigger_time)
    time.sleep(1)
    ubi.post("alarm_trigger", 0)
