# WIFI Settings
ssid = 'INSERT WIFI NAME'
ssid_pass = 'INSERT WIFI PASSWORD'

# Ubidots
ubidots_token = 'INSERT UBIDOTS TOKEN'

# MQTT Broker
url = "https://industrial.api.ubidots.com/"
pub = "api/v1.6/devices/{DEVICE NAME}"
sub = "api/v1.6/devices/{DEVICE NAME}/{VARIABLE NAME}/lv"
headers = {"X-Auth-Token": ubidots_token, "Content-Type": "application/json"}
