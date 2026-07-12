#!/usr/bin/env python3

import json
import os
import time

import paho.mqtt.client as mqtt


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def read(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return None


def write(path, value):
    try:
        with open(path, "w") as f:
            f.write(str(value))
        return True
    except Exception as e:
        print(f"Write failed: {path} -> {e}", flush=True)
        return False


def find_backlight():
    base = "/sys/class/backlight"

    try:
        entries = sorted(os.listdir(base))
        if entries:
            return os.path.join(base, entries[0])
    except Exception:
        pass

    return None


BACKLIGHT = find_backlight()


# ------------------------------------------------------------
# MQTT Configuration
# ------------------------------------------------------------

MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="surface_hardware"
)

if MQTT_USER and MQTT_PASSWORD:
    client.username_pw_set(
        MQTT_USER,
        MQTT_PASSWORD
    )

client.reconnect_delay_set(
    min_delay=1,
    max_delay=30
)

mqtt_connected = False


# ------------------------------------------------------------
# MQTT Helper
# ------------------------------------------------------------

def publish(topic, payload, retain=True):
    if isinstance(payload, (dict, list)):
        payload = json.dumps(payload)

    client.publish(
        topic,
        payload,
        qos=1,
        retain=retain
    )













    # ------------------------------------------------------------
# Home Assistant Discovery
# ------------------------------------------------------------

def publish_sensor(name, value, unit=None):

    topic = f"surface_hardware/{name}"

    client.publish(
        topic,
        value,
        retain=True
    )
    
def publish_discovery():

    sensors = {
        "battery": ("Surface Battery", "%"),
        "cycles": ("Surface Battery Cycles", "cycles"),
        "temperature": ("Surface CPU Temperature", "°C"),
        "brightness": ("Surface Brightness", "%"),
    }

    for key, (name, unit) in sensors.items():

        payload = {
            "name": name,
            "unique_id": f"surface_{key}",
            "state_topic": f"surface_hardware/{key}",
            "unit_of_measurement": unit,
            "device": {
                "identifiers": ["surface_hardware"],
                "name": "Surface Hardware",
                "manufacturer": "Microsoft",
                "model": "Surface Pro"
            }
        }

        publish(
            f"homeassistant/sensor/surface_{key}/config",
            payload
        )

    brightness_number = {
        "name": "Surface Brightness",
        "unique_id": "surface_brightness_control",
        "command_topic": "surface_hardware/brightness/set",
        "state_topic": "surface_hardware/brightness",
        "min": 0,
        "max": 100,
        "step": 1,
        "mode": "slider"
    }

    publish(
        "homeassistant/number/surface_brightness/config",
        brightness_number
    )

    for state, command in (
        ("On", "screen_on"),
        ("Off", "screen_off"),
    ):

        payload = {
            "name": f"Surface Screen {state}",
            "unique_id": f"surface_screen_{state.lower()}",
            "command_topic": "surface_hardware/screen",
            "payload_press": command
        }

        publish(
            f"homeassistant/button/surface_screen_{state.lower()}/config",
            payload
        )


# ------------------------------------------------------------
# MQTT Callbacks
# ------------------------------------------------------------

def on_connect(client, userdata, flags, reason_code, properties):

    global mqtt_connected

    mqtt_connected = True

    print("MQTT connected", flush=True)

    publish_discovery()

    client.subscribe("surface_hardware/#", qos=1)


# ------------------------------------------------------------
# Home Assistant Discovery
# ------------------------------------------------------------

def publish_discovery():

    sensors = {
        "battery": ("Surface Battery", "%"),
        "cycles": ("Surface Battery Cycles", "cycles"),
        "temperature": ("Surface CPU Temperature", "°C"),
        "brightness": ("Surface Brightness", "%"),
    }

    for key, (name, unit) in sensors.items():

        payload = {
            "name": name,
            "unique_id": f"surface_{key}",
            "state_topic": f"surface_hardware/{key}",
            "unit_of_measurement": unit,
            "device": {
                "identifiers": ["surface_hardware"],
                "name": "Surface Hardware",
                "manufacturer": "Microsoft",
                "model": "Surface Pro"
            }
        }

        publish(
            f"homeassistant/sensor/surface_{key}/config",
            payload
        )

    brightness_number = {
        "name": "Surface Brightness",
        "unique_id": "surface_brightness_control",
        "command_topic": "surface_hardware/brightness/set",
        "state_topic": "surface_hardware/brightness",
        "min": 0,
        "max": 100,
        "step": 1,
        "mode": "slider"
    }

    publish(
        "homeassistant/number/surface_brightness/config",
        brightness_number
    )

    for state, command in (
        ("On", "screen_on"),
        ("Off", "screen_off"),
    ):

        payload = {
            "name": f"Surface Screen {state}",
            "unique_id": f"surface_screen_{state.lower()}",
            "command_topic": "surface_hardware/screen",
            "payload_press": command
        }

        publish(
            f"homeassistant/button/surface_screen_{state.lower()}/config",
            payload
        )


# ------------------------------------------------------------
# MQTT Callbacks
# ------------------------------------------------------------

def on_connect(client, userdata, flags, reason_code, properties):

    global mqtt_connected

    mqtt_connected = True

    print("MQTT connected", flush=True)

    publish_discovery()

    client.subscribe("surface_hardware/#", qos=1)

def set_brightness(value):
    if not BACKLIGHT:
        return

    maximum = int(read(BACKLIGHT + "/max_brightness"))

    raw = int(maximum * float(value) / 100)

    with open(BACKLIGHT + "/brightness", "w") as f:
        f.write(str(raw))


def screen(power):
    if not BACKLIGHT:
        return

    try:
        with open(BACKLIGHT + "/bl_power", "w") as f:
            f.write("1" if power == "screen_off" else "0")
    except Exception as e:
        print("Screen control failed:", e)


def on_message(client, userdata, msg):


    print(
        "MQTT COMMAND:",
        msg.topic,
        msg.payload.decode(),
        flush=True
    )

    if msg.topic == "surface_hardware/brightness/set":
        brightness.set(msg.payload.decode())

    elif msg.topic == "surface_hardware/screen":
        if msg.payload.decode() == "screen_on":
            display.screen_on()
        elif msg.payload.decode() == "screen_off":
            display.screen_off()

    try:
        payload = msg.payload.decode().strip()

        if msg.topic == "surface_hardware/brightness/set":
            set_brightness(payload)

        elif msg.topic == "surface_hardware/screen":
            screen(payload)

    except Exception as e:
        print("MQTT command failed:", e)


client.on_message = on_message

client.loop_start()


while True:

    print("----------------------", flush=True)

    if BACKLIGHT:

        maximum = int(read(BACKLIGHT + "/max_brightness") or 1000)
        current = int(read(BACKLIGHT + "/brightness") or 0)

        brightness = int(current * 100 / maximum)

        print(f"Brightness: {brightness} %", flush=True)

        publish_sensor("brightness", brightness)

    battery = read("/sys/class/power_supply/BAT0/capacity") or "0"
    cycles = read("/sys/class/power_supply/BAT0/cycle_count") or "0"
    temp = read("/sys/class/thermal/thermal_zone1/temp")

    print(f"Battery: {battery} %", flush=True)
    print(f"Cycles: {cycles}", flush=True)

    publish_sensor("battery", battery)
    publish_sensor("cycles", cycles)

    if temp:
        temperature = round(int(temp) / 1000, 1)

        print(f"CPU Temp: {temperature} °C", flush=True)

        publish_sensor("temperature", temperature)

    time.sleep(30)

    
import os
import json
import time
import paho.mqtt.client as mqtt

MQTT_HOST = os.environ.get(
    "MQTT_HOST",
    "core-mosquitto"
)

MQTT_PORT = int(
    os.environ.get(
        "MQTT_PORT",
        1883
    )
)


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except:
        return None


def find_backlight():
    base = "/sys/class/backlight"

    try:
        devices = os.listdir(base)

        if devices:
            return os.path.join(base, devices[0])

    except:
        pass

    return None


BACKLIGHT = find_backlight()

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)
MQTT_HOST = os.environ.get(
    "MQTT_HOST",
    "core-mosquitto"
)

MQTT_PORT = int(
    os.environ.get(
        "MQTT_PORT",
        "1883"
    )
)

MQTT_USER = os.environ.get(
    "MQTT_USER"
)

MQTT_PASSWORD = os.environ.get(
    "MQTT_PASSWORD"
)





if MQTT_USER and MQTT_PASSWORD:
    client.username_pw_set(
        MQTT_USER,
        MQTT_PASSWORD
    )
client.reconnect_delay_set(
    min_delay=1,
    max_delay=30
)

connected = False

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("MQTT connected")

    publish_discovery()

    client.subscribe("surface_hardware/#")


client.on_connect = on_connect


client.connect(
    MQTT_HOST,
    MQTT_PORT,
    60
)
print("MQTT SETTINGS")
print(MQTT_HOST)
print(MQTT_PORT)
print(MQTT_USER)
print(bool(MQTT_PASSWORD))

while not connected:
    time.sleep(0.1)

def publish_sensor(name, value, unit=None):

    topic = f"surface_hardware/{name}"

    client.publish(
        topic,
        value,
        retain=True
    )


def publish_discovery():

    sensors = {

        "battery": {
            "name": "Surface Battery",
            "unit": "%"
        },

        "cycles": {
            "name": "Surface Battery Cycles",
            "unit": "cycles"
        },

        "temperature": {
            "name": "Surface CPU Temperature",
            "unit": "°C"
        },

        "brightness": {
            "name": "Surface Brightness",
            "unit": "%"
        }

    }


    for key,data in sensors.items():

        payload = {
            "name": data["name"],
            "state_topic": f"surface_hardware/{key}",
            "unit_of_measurement": data["unit"],
            "unique_id":"surface_screen_control"
        }


        client.publish(
            f"homeassistant/sensor/surface_{key}/config",
            json.dumps(payload),
            retain=True
        )


    # brightness control

    payload = {

        "name":"Surface Brightness",

        "command_topic":
        "surface_hardware/brightness/set",

        "state_topic":
        "surface_hardware/brightness",

        "min":0,

        "max":100,

        "unique_id":
        f"surface_{key}"
    }


    client.publish(
        "homeassistant/number/surface_brightness/config",
        json.dumps(payload),
        retain=True
    )


    # screen power switches

    for state,command in [
        ("on","screen_on"),
        ("off","screen_off")
    ]:

        payload={

            "name":
            f"Surface Screen {state}",

            "command_topic":
            "surface_hardware/screen",

            "payload_on":
            command,

            "unique_id":
            f"surface_screen_{state}"

        }


        client.publish(
            f"homeassistant/button/surface_screen_{state}/config",
            json.dumps(payload),
            retain=True
        )



publish_discovery()



def set_brightness(value):

    if not BACKLIGHT:
        return

    maximum=int(
        read(
            BACKLIGHT+"/max_brightness"
        )
    )


    raw=int(
        maximum *
        float(value)/100
    )


    with open(
        BACKLIGHT+"/brightness",
        "w"
    ) as f:

        f.write(str(raw))



def screen(power):

    if not BACKLIGHT:
        return


    if power == "screen_off":

        with open(
            BACKLIGHT + "/bl_power",
            "w"
        ) as f:

            f.write("1")


    elif power == "screen_on":

        with open(
            BACKLIGHT + "/bl_power",
            "w"
        ) as f:

            f.write("0")



def message(client,userdata,msg):

    if msg.topic=="surface_hardware/brightness/set":

        set_brightness(
            msg.payload.decode()
        )


    if msg.topic=="surface_hardware/screen":

        screen(
            msg.payload.decode()
        )



client.subscribe(
    "surface_hardware/#"
)

client.on_message = message



while True:

    print("----------------------", flush=True)

    if BACKLIGHT:

        maximum = int(
            read(
                BACKLIGHT + "/max_brightness"
            ) or 1000
        )

        current = int(
            read(
                BACKLIGHT + "/brightness"
            )
        )

        brightness = int(current * 100 / maximum)

        print(
            "Brightness:",
            brightness,
            "%",
            flush=True
        )

        publish_sensor(
            "brightness",
            brightness
        )


    battery = read(
        "/sys/class/power_supply/BAT0/capacity"
    )

    cycles = read(
        "/sys/class/power_supply/BAT0/cycle_count"
    )

    temp = read(
        "/sys/class/thermal/thermal_zone1/temp"
    )


    print(
        "Battery:",
        battery,
        "%",
        flush=True
    )

    print(
        "Cycles:",
        cycles,
        flush=True
    )


    if temp:

        temperature = round(
            int(temp)/1000,
            1
        )

        print(
            "CPU Temp:",
            temperature,
            "°C",
            flush=True
        )

        publish_sensor(
            "temperature",
            temperature
        )


    publish_sensor(
        "battery",
        battery
    )

    publish_sensor(
        "cycles",
        cycles
    )


    client.loop_start()

    time.sleep(30)