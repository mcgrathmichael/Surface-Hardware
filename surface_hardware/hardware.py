import os
import time
import json
import subprocess
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


mqtt_user = os.environ.get("MQTT_USER")
mqtt_password = os.environ.get("MQTT_PASSWORD")

if mqtt_user and mqtt_password:
    client.username_pw_set(
        mqtt_user,
        mqtt_password
    )

client.connect(
    MQTT_HOST,
    MQTT_PORT,
    60
)

try:

    client.connect(
        MQTT_HOST,
        MQTT_PORT,
        60
    )

    print(
        "MQTT connected",
        MQTT_HOST,
        flush=True
    )

except Exception as e:

    print(
        "MQTT failed:",
        e,
        flush=True
    )


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
        "surface_brightness_control"
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


    client.loop()

    time.sleep(30)