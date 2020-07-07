import urequests as requests
import keys
import sound

last_mode = None


# Builds the JSON object to send the request
def build_json(variable, value):
    try:
        # data array creation
        data = {variable: {"value": value}}
        return data
    except:
        return None


# Sends the request. Please reference the REST API reference https://ubidots.com/docs/api/
def post(topic, value):
    try:
        data = build_json(topic, value)
        if data is not None:
            r = requests.post(url=(keys.url + keys.pub), headers=keys.headers, json=data) # include data as JSON object
            json_obj = r.json()
            r.close()
            return json_obj
        else:
            print("ERROR: JSON Empty. Nothing to post.")
            pass
    except:
        print("ERROR: Can't send data to Ubidots.")
        pass


# Function for listening for commands from the Ubidots server. In my case only integers.
def listen(topic):
    r = requests.get(url=(keys.url + topic), headers=keys.headers)
    value = int(r.json())
    r.close()
    return value


# Checks control variable on Ubidots and returns True or False
def alarm_mode():
    global last_mode
    mode = listen(keys.sub)

    if mode==last_mode:
        pass
    else:
        print("Mode: [" + str(mode) + "]")
        sound.mode_change(mode)

    last_mode = mode
    return mode
