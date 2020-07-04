from machine import UART
from network import WLAN
import machine
import time
import os
import pycom
import keys

pycom.pybytes_on_boot(False)
pycom.heartbeat(False)

uart = UART(0, baudrate=115200)
os.dupterm(uart)

# config wifi hardware
wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.INT_ANT)

# Assign your Wi-Fi credentials
wlan.connect(keys.ssid, auth=(WLAN.WPA2, keys.ssid_pass), timeout=5000)

# Connecting to WiFi
while not wlan.isconnected ():
    print("Connecting to WiFi...")
    time.sleep(1)
    #machine.idle()
print("Connected to Wifi \n")
time.sleep(0.5)

machine.main('main.py')
